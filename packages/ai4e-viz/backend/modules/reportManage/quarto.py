"""Quarto project generation and persisted asynchronous exports.

ReportDocument JSON is canonical.  Quarto files are generated artifacts and
never accept user-provided executable cells, command line arguments or paths.
"""

from __future__ import annotations

import html
import json
import os
import shutil
import subprocess
import threading
import zipfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from modules.dataAssets import get_artifact
from modules.visIO import get_visualization
from modules.visConvertor import convert_to_glb
from modules.reportManage import get_export, get_report_version
from modules.reportManage.repository import update_export
from infrastructure.config import runtime_paths


MODULE_ROOT = Path(__file__).resolve().parent
BACKEND_ROOT = MODULE_ROOT.parents[1]
ROOT = BACKEND_ROOT.parent
EXPORT_ROOT = runtime_paths().exports / "reports"
QUARTO_VERSION = "1.10.18"
FRONTEND_BASE = os.environ.get("QODER_FRONTEND_BASE", "http://127.0.0.1:5275")
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="quarto-export")
_RUNNING: set[str] = set()
_RUNNING_LOCK = threading.Lock()


def find_quarto() -> str | None:
    """按显式配置、系统路径和项目工具目录依次查找锁定版本的 Quarto。"""

    explicit = os.environ.get("QUARTO_BIN")
    if explicit and Path(explicit).is_file():
        return explicit
    system = shutil.which("quarto")
    if system:
        return system
    tool_root = BACKEND_ROOT / ".tools" / "quarto" / QUARTO_VERSION
    candidates = [tool_root / "bin" / "quarto", *tool_root.glob("**/bin/quarto")]
    return str(next((path for path in candidates if path.is_file()), "")) or None


def quarto_health() -> dict[str, Any]:
    """检查 Quarto 可执行文件、版本和 Typst 导出能力并返回结构化状态。"""

    binary = find_quarto()
    if not binary:
        return {
            "state": "offline", "required_version": QUARTO_VERSION, "version": None,
            "binary": None, "pdf_engine": "typst", "message": "Quarto 尚未安装；其他服务不受影响。",
        }
    try:
        result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=15, check=True)
        version = result.stdout.strip()
        return {
            "state": "live" if version == QUARTO_VERSION else "stale", "required_version": QUARTO_VERSION,
            "version": version, "binary": binary, "pdf_engine": "typst",
            "message": "Quarto 导出可用" if version == QUARTO_VERSION else "Quarto 版本与项目锁定版本不一致",
        }
    except (OSError, subprocess.SubprocessError) as exc:
        return {
            "state": "error", "required_version": QUARTO_VERSION, "version": None,
            "binary": binary, "pdf_engine": "typst", "message": str(exc),
        }


def _directory_bytes(path: Path) -> int:
    """Return allocated file bytes without following symlinks."""
    if not path.exists():
        return 0
    if path.is_file() or path.is_symlink():
        return path.lstat().st_size
    return sum(item.lstat().st_size for item in path.rglob("*") if item.is_file() or item.is_symlink())


def _remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def compact_export_directory(export_id: str, *, output_path: str | None = None, failed: bool = False) -> dict[str, Any]:
    """删除可重建的 Quarto 中间目录，同时保留下载产物和诊断日志。

    便携 HTML 的 ZIP 位于 ``project`` 外；PDF 只保留最终文件；连接式 HTML 保留
    ``project/output`` 中维持相对资源关系所需的内容。日志始终保留在项目目录旁。
    """
    root = (EXPORT_ROOT / export_id).resolve()
    export_root = EXPORT_ROOT.resolve()
    if root.parent != export_root or root.name != export_id:
        raise ValueError("EXPORT_PATH_INVALID")
    project = root / "project"
    before = _directory_bytes(root)
    if not project.exists():
        return {"before_bytes": before, "after_bytes": before, "reclaimed_bytes": 0}

    if failed:
        _remove_path(project)
    else:
        if not output_path:
            raise ValueError("EXPORT_OUTPUT_MISSING")
        output = Path(output_path).resolve()
        try:
            output.relative_to(root)
        except ValueError as exc:
            raise ValueError("EXPORT_OUTPUT_OUTSIDE_ROOT") from exc
        if not output.is_file():
            raise ValueError("EXPORT_OUTPUT_MISSING")

        if project not in output.parents:
            # Portable HTML ZIPs live next to project, so the full generated
            # Quarto source/output tree can be rebuilt and safely discarded.
            _remove_path(project)
        else:
            output_dir = project / "output"
            try:
                output.relative_to(output_dir.resolve())
            except ValueError as exc:
                raise ValueError("EXPORT_OUTPUT_LAYOUT_INVALID") from exc
            for child in list(project.iterdir()):
                if child != output_dir:
                    _remove_path(child)
            if output.suffix.lower() == ".pdf":
                for child in list(output_dir.iterdir()):
                    if child.resolve() != output:
                        _remove_path(child)

    after = _directory_bytes(root)
    return {"before_bytes": before, "after_bytes": after, "reclaimed_bytes": max(before - after, 0)}


def _safe_text(value: Any) -> str:
    text = str(value or "")
    # Preserve ordinary Markdown while preventing raw HTML, Quarto shortcodes and
    # executable/raw fenced blocks from crossing the ReportDocument boundary.
    # Quarto execution is disabled too, but escaping here keeps the generated HTML
    # safe even when a renderer changes its Markdown defaults later.
    text = text.replace("```", "｀｀｀").replace("{{<", "{{‹")
    return html.escape(text, quote=False)


def _yaml_string(value: Any) -> str:
    return json.dumps(str(value or ""), ensure_ascii=False)


def _copy_media(source: Path, asset_dir: Path, prefix: str) -> str:
    asset_dir.mkdir(parents=True, exist_ok=True)
    name = f"{prefix}-{source.name}".replace("/", "-")
    target = asset_dir / name
    if not target.exists() or target.stat().st_size != source.stat().st_size:
        shutil.copy2(source, target)
    return f"assets/media/{name}"


def _runtime_script() -> str:
    return r'''(function(){
const palette={engineering:['#1677ff','#0e9f9f','#8250df','#d97706','#dc2626'],viridis:['#440154','#3b528b','#21918c','#5ec962','#fde725'],plasma:['#0d0887','#7e03a8','#cc4778','#f89540','#f0f921'],turbo:['#30123b','#466be3','#28bbec','#a4fc3c','#f9ba38','#d93806'],coolwarm:['#3b4cc0','#8db0fe','#dddcdc','#f4987a','#b40426'],grayscale:['#111827','#4b5563','#9ca3af','#d1d5db']};
function heat(payload){const d=payload.data,m=d.values||d.matrix||[];const v=[];m.forEach((row,y)=>row.forEach((x,i)=>v.push([i,y,Number(x)])));const nums=v.map(x=>x[2]).filter(Number.isFinite);return{animation:false,tooltip:{},grid:{left:52,right:70,top:24,bottom:46},xAxis:{type:'category'},yAxis:{type:'category'},visualMap:{min:Math.min(...nums),max:Math.max(...nums),right:0,top:'middle'},series:[{type:'heatmap',data:v}]};}
function option(payload){const k=payload.artifact.kind,d=payload.data,p=payload.resolved_spec.params||{},common={animation:!!p.animation,color:palette[p.palette]||palette.engineering,tooltip:{show:p.show_tooltip!==false,trigger:'axis'},legend:{show:p.show_legend!==false&&p.legend_position!=='hidden',top:0},grid:{left:56,right:24,top:44,bottom:p.zoom?70:46},dataZoom:p.zoom?[{type:'inside'},{type:'slider',height:18}]:undefined};
if(['matrix','tensor','raster','volume','field'].includes(k))return heat(payload);
if(k==='scalar')return{...common,xAxis:{type:'category',data:[d.unit||p.unit||'当前值']},yAxis:{type:'value',min:0},series:[{type:'bar',barMaxWidth:96,data:[d.value],label:{show:true,position:'top',formatter:'{c}'+(p.unit||d.unit||'')},markLine:Number.isFinite(p.target??d.target)?{symbol:'none',data:[{yAxis:p.target??d.target}]}:undefined}]};
if(k==='series')return{...common,xAxis:{type:p.x_scale==='linear'?'value':p.x_scale==='time'?'time':'category',data:d.x},yAxis:{type:p.y_scale==='log'?'log':'value'},series:d.series.map(s=>({name:s.name,type:'line',showSymbol:!!p.show_symbols,smooth:!!p.smooth,lineStyle:{width:p.line_width||2,type:p.line_style||'solid'},data:s.values}))};
if(k==='distribution'){const horizontal=p.orientation==='horizontal',category={type:'category',data:d.bins.slice(0,-1)},value={type:'value'};return{...common,xAxis:horizontal?value:category,yAxis:horizontal?category:value,series:[{type:'bar',data:d.counts}]};}
if(k==='ensemble')return{...common,xAxis:{type:'category',data:d.x},yAxis:{type:'value'},series:[...d.members.map((values,i)=>({name:'成员 '+(i+1),type:'line',showSymbol:false,lineStyle:{width:1,opacity:.28},data:values})),{name:'均值',type:'line',showSymbol:false,lineStyle:{width:3},data:d.mean}]};
if(k==='uncertainty')return{...common,xAxis:{type:'category',data:d.x},yAxis:{type:'value'},series:[{name:'下界',type:'line',symbol:'none',lineStyle:{opacity:0},stack:'interval',data:d.lower},{name:'95% 区间',type:'line',symbol:'none',lineStyle:{opacity:0},areaStyle:{color:'rgba(22,119,255,.24)'},stack:'interval',data:d.upper.map((value,i)=>value-d.lower[i])},{name:'均值',type:'line',data:d.mean}]};
if(k==='optimization')return{...common,tooltip:{trigger:'item'},xAxis:{type:'value',name:'效率'},yAxis:{type:'value',name:'压降'},series:[{type:'scatter',data:d.points.map(point=>({value:[point.efficiency,point.loss],name:point.id,symbolSize:point.pareto?13:8}))}]};
if(k==='graph')return{animation:!!p.animation,tooltip:{},series:[{type:'graph',layout:p.layout==='manual'?'none':p.layout==='circular'?'circular':'force',roam:p.zoom!==false,label:{show:p.show_labels!==false,position:'right'},symbolSize:p.node_size||28,data:d.nodes.map((node,i)=>({...node,x:node.x??node.stage*150??i*120,y:node.y??80+(i%3)*90})),links:d.links.map(edge=>Array.isArray(edge)?{source:edge[0],target:edge[1]}:edge)}]};return null;}
function traces(payload){const k=payload.artifact.kind,d=payload.data,p=payload.resolved_spec.params||{};
if(k==='series')return d.series.map(s=>({x:d.x,y:s.values,name:s.name,type:'scatter',mode:p.show_symbols?'lines+markers':'lines',line:{width:p.line_width||2,dash:p.line_style==='dashed'?'dash':p.line_style==='dotted'?'dot':'solid'}}));
if(k==='distribution')return[{x:d.bins.slice(0,-1),y:d.counts,type:'bar'}];
if(k==='ensemble')return[...d.members.map((values,i)=>({x:d.x,y:values,name:'成员 '+(i+1),type:'scatter',mode:'lines',line:{width:1},opacity:.28,showlegend:false})),{x:d.x,y:d.mean,name:'均值',type:'scatter',mode:'lines',line:{width:3}}];
if(k==='uncertainty')return[{x:d.x,y:d.lower,name:'下界',type:'scatter',mode:'lines',line:{width:0},showlegend:false},{x:d.x,y:d.upper,name:'95% 区间',type:'scatter',mode:'lines',line:{width:0},fill:'tonexty',fillcolor:'rgba(22,119,255,.24)'},{x:d.x,y:d.mean,name:'均值',type:'scatter',mode:'lines',line:{width:3}}];
if(k==='optimization')return[{x:d.points.map(v=>v.efficiency),y:d.points.map(v=>v.loss),text:d.points.map(v=>v.id),mode:'markers',type:'scatter'}];
if(['matrix','tensor'].includes(k))return[{z:d.values||d.matrix,type:'heatmap',colorscale:p.colormap||'Viridis',reversescale:!!p.reverse_colormap,zmin:p.range_min,zmax:p.range_max}];return[];}
function vegaSpec(payload){const p=payload.resolved_spec.params||{},m=payload.data.values||payload.data.matrix||[],values=[];m.forEach((row,y)=>row.forEach((value,x)=>values.push({x,y,value:Number(value)})));return{$schema:'https://vega.github.io/schema/vega-lite/v6.json',width:'container',height:p.height||420,background:p.background_color||'#fff',data:{values},mark:{type:'rect',tooltip:p.show_tooltip!==false},encoding:{x:{field:'x',type:'ordinal'},y:{field:'y',type:'ordinal'},color:{field:'value',type:'quantitative',scale:{scheme:p.colormap||'viridis',reverse:!!p.reverse_colormap}}},config:{view:{stroke:null}}};}
function jsx(type,props,key){return React.createElement(type,{...(props||{}),key:key??props?.key});}
async function render(el){const canvas=el.querySelector('.qoder-viz-canvas'),payload=JSON.parse(el.querySelector('script[type="application/json"]').textContent),owner=payload.renderer.owner,p=payload.resolved_spec.params||{};
if(owner==='echarts-svg'){const chart=echarts.init(canvas,null,{renderer:'svg'});chart.setOption(option(payload));new ResizeObserver(()=>chart.resize()).observe(el);return;}
if(owner==='plotly'){await Plotly.newPlot(canvas,traces(payload),{paper_bgcolor:p.background_color||'#fff',plot_bgcolor:p.background_color||'#fff',showlegend:p.show_legend!==false,margin:{l:58,r:24,t:28,b:48}},{responsive:true,displaylogo:false});return;}
if(owner==='vega'){await vegaEmbed(canvas,vegaSpec(payload),{actions:true,renderer:'svg'});return;}
if(owner==='perspective'){await window.qoderPerspectiveReady;const viewer=document.createElement('perspective-viewer');viewer.setAttribute('plugin','Datagrid');viewer.style.height=(p.height||480)+'px';canvas.replaceChildren(viewer);await viewer.load(payload.data.rows||[]);await viewer.restore({columns:p.columns?.length?p.columns:undefined,settings:!!p.show_search});return;}
if(owner==='react-flow'&&window.ReactFlow&&window.ReactDOM){const nodes=(payload.data.nodes||[]).map((n,i)=>({id:String(n.id),data:{label:n.name||n.label||n.id},position:{x:Number(n.x??n.stage*180??i*140),y:Number(n.y??(i%3)*110)}})),edges=(payload.data.links||[]).map((e,i)=>({id:'edge-'+i,source:String(Array.isArray(e)?e[0]:e.source),target:String(Array.isArray(e)?e[1]:e.target)}));ReactDOM.createRoot(canvas).render(jsx(window.ReactFlow.ReactFlow,{nodes,edges,fitView:true,children:[jsx(window.ReactFlow.Background,{},'bg'),jsx(window.ReactFlow.Controls,{},'controls')]}));return;}
if(owner==='react'){canvas.innerHTML='<div class="qoder-kpi"><strong>'+String(payload.data.value)+'</strong><span>'+String(p.unit||payload.data.unit||'')+'</span></div>';return;}
if(owner==='browser-native'){const pre=document.createElement('pre');pre.textContent=payload.data.markdown||payload.data.summary||'浏览器原生素材';canvas.replaceChildren(pre);return;}
canvas.innerHTML='<p>冻结数据与来源已保留；远程交互服务当前不可用。</p>';}
window.jsxRuntime={Fragment:React?.Fragment,jsx,jsxs:jsx};
document.querySelectorAll('[data-qoder-viz]').forEach(el=>render(el).catch(err=>{el.querySelector('.qoder-viz-canvas').textContent='可视化加载失败：'+err.message;}));
})();'''


def _capture_visualization_static(
    visualization: dict[str, Any], project_dir: Path
) -> tuple[str | None, str | None]:
    """Capture the frozen browser renderer, never a substitute renderer.

    The script is fixed project code and receives only a server-created
    Visualization id plus a controlled output path. If the owning renderer is
    unavailable, the report keeps a structured diagnostic instead of creating
    a misleading image with another engine.
    """

    node = shutil.which("node")
    script = ROOT / "frontend" / "scripts" / "capture-visualization.mjs"
    if not node or not script.is_file():
        return None, "STATIC_CAPTURE_RUNTIME_MISSING"
    target_dir = project_dir / "assets" / "static"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{visualization['visualization_id']}-v{visualization['spec_version']}.png"
    params = visualization.get("parameters") or {}
    width = max(320, min(1600, int(params.get("width", 960))))
    height = max(360, min(1200, int(params.get("height", 480)) + 180))
    url = f"{FRONTEND_BASE.rstrip('/')}/#/visualizations/{visualization['visualization_id']}?embed=1"
    result = subprocess.run(
        [node, str(script), url, str(target), str(width), str(height)],
        cwd=ROOT / "frontend", capture_output=True, text=True, timeout=120, check=False,
    )
    if result.returncode != 0 or not target.is_file() or target.stat().st_size < 1024:
        message = _capture_error_summary(result.stderr, result.stdout)
        return None, f"STATIC_CAPTURE_FAILED: {message}"
    return f"assets/static/{target.name}", None


def _capture_error_summary(stderr: str | None, stdout: str | None) -> str:
    """Keep the actionable Playwright error instead of a trailing Node version."""

    lines = [line.strip() for line in (stderr or stdout or "capture failed").splitlines() if line.strip()]
    meaningful = [
        line for line in lines
        if any(marker in line for marker in (
            "TimeoutError", "page.goto", "locator.", "waitFor", "O3DV_", "Error:", "ERR_",
        ))
    ]
    chosen = meaningful[-6:] if meaningful else [line for line in lines[-8:] if not line.startswith("Node.js v")]
    summary = " | ".join(dict.fromkeys(chosen)) or "capture failed"
    return summary[:720]


def _capture_reader_report(export: dict[str, Any], document: dict[str, Any]) -> tuple[Path, dict[str, Any]]:
    """Capture the exact React report reader that corresponds to a frozen API payload."""

    node = shutil.which("node")
    script = ROOT / "frontend" / "scripts" / "capture-report.mjs"
    if not node or not script.is_file():
        raise RuntimeError("REPORT_CAPTURE_RUNTIME_MISSING")
    source_report_id = str(document.get("source_report_id") or "report")
    safe_name = "".join(char if char.isalnum() or char in "-_" else "-" for char in source_report_id).strip("-") or "report"
    root = EXPORT_ROOT / export["export_id"]
    root.mkdir(parents=True, exist_ok=True)
    suffix = ".pdf" if export["format"] == "pdf" else ".html"
    target = root / f"{safe_name}-current{suffix}"
    route = (
        f"{FRONTEND_BASE.rstrip('/')}/#/reports/{source_report_id}"
        f"?exportSnapshot={export['report_id']}&snapshotVersion={export['report_version']}&print=1"
    )
    result = subprocess.run(
        [node, str(script), route, str(target), export["format"]],
        cwd=ROOT / "frontend", capture_output=True, text=True, timeout=240, check=False,
    )
    if result.returncode != 0 or not target.is_file() or target.stat().st_size < 1024:
        raise RuntimeError(f"REPORT_CAPTURE_FAILED: {_capture_error_summary(result.stderr, result.stdout)}")
    manifest = {
        "source_report_id": source_report_id,
        "report_id": export["report_id"],
        "report_version": export["report_version"],
        "content_hash": document.get("content_hash"),
        "format": export["format"],
        "mode": "current-reader",
        "engine": "chromium-reader-snapshot",
        "output_name": target.name,
        "bytes": target.stat().st_size,
    }
    return target, manifest


def _visualization_html(visualization: dict[str, Any], project_dir: Path, *, portable: bool) -> tuple[str, str]:
    payload = visualization.get("payload") or {}
    artifact = payload.get("artifact") or {}
    renderer = payload.get("renderer") or {}
    kind = artifact.get("kind")
    artifact_name = artifact.get("name") or visualization["visualization_id"]
    title = html.escape(artifact_name)
    source = html.escape(f"{visualization['artifact_id']} · {visualization['spec_id']} v{visualization['spec_version']}")
    textual_fallback = f"**{_safe_text(artifact_name)}**  \n{_safe_text(artifact.get('takeaway'))}  \n来源：`{source}`"
    pdf_fallback = textual_fallback

    if kind == "mesh":
        if not portable:
            static_path, capture_error = _capture_visualization_static(visualization, project_dir)
            if static_path:
                pdf_fallback = (
                    f"![{_safe_text(artifact_name)}]({static_path})\n\n"
                    f"{_safe_text(artifact.get('takeaway'))}  \n来源：`{source}`"
                )
                static_evidence = (
                    f'<details class="qoder-static-evidence"><summary>查看同参数静态证据</summary>'
                    f'<img src="{static_path}" alt="{title} 的冻结静态表示"></details>'
                )
            else:
                pdf_fallback = (
                    "::: {.callout-warning}\n## O3DV 静态表示未生成\n"
                    f"{textual_fallback}\n\n原因：`{_safe_text(capture_error)}`\n:::"
                )
                static_evidence = f'<p class="qoder-render-diagnostic">静态证据未生成：{html.escape(capture_error or "unknown")}</p>'
            url = f"{FRONTEND_BASE.rstrip('/')}/#/visualizations/{visualization['visualization_id']}?embed=1"
            return (
                f'<figure class="qoder-connected"><iframe src="{html.escape(url)}" title="{title}" loading="lazy"></iframe>{static_evidence}<figcaption>{source}</figcaption></figure>',
                pdf_fallback,
            )

        # Only the offline HTML bundle owns a local copy of the model and O3DV
        # runtime. Connected HTML and PDF use the live frozen visualization plus
        # a same-renderer screenshot, avoiding a 74 MiB GLB copy per export.
        stored = get_artifact(visualization["artifact_id"])
        model_dir = project_dir / "assets" / "models"
        model_dir.mkdir(parents=True, exist_ok=True)
        model_target = model_dir / f"{visualization['artifact_id']}.glb"
        source_path = Path(stored["file_path"])
        if source_path.suffix.lower() == ".glb":
            shutil.copy2(source_path, model_target)
        else:
            convert_to_glb(str(source_path), str(model_target))
        viewer_target = project_dir / "assets" / "o3dv"
        if not viewer_target.exists():
            shutil.copytree(ROOT / "frontend" / "public" / "3dviewer", viewer_target)
        frame = f'assets/o3dv/embed.html#model={html.escape("../models/" + model_target.name)}'
        return (
            f'<figure class="qoder-o3dv"><iframe src="{frame}" title="{title}"></iframe><figcaption>{source}</figcaption></figure>',
            pdf_fallback,
        )

    if kind == "image" or (kind == "video" and portable):
        stored = get_artifact(visualization["artifact_id"])
        relative = _copy_media(Path(stored["file_path"]), project_dir / "assets" / "media", visualization["artifact_id"])
        if kind == "image":
            return (f'<figure><img src="{relative}" alt="{title}"><figcaption>{source}</figcaption></figure>', f"![{_safe_text(title)}]({relative})\n\n{source}")
        return (f'<figure><video src="{relative}" controls muted playsinline></video><figcaption>{source}</figcaption></figure>', textual_fallback)

    if kind == "text_document":
        markdown = _safe_text((payload.get("data") or {}).get("markdown") or artifact.get("takeaway"))
        return f'<article class="qoder-native-text"><pre>{markdown}</pre><p>{source}</p></article>', markdown + f"\n\n来源：`{source}`"

    if not portable:
        static_path, capture_error = _capture_visualization_static(visualization, project_dir)
        if static_path:
            pdf_fallback = f"![{_safe_text(artifact_name)}]({static_path})\n\n{_safe_text(artifact.get('takeaway'))}  \n来源：`{source}`"
            static_evidence = (
                f'<details class="qoder-static-evidence"><summary>查看同参数静态证据</summary>'
                f'<img src="{static_path}" alt="{title} 的冻结静态表示"></details>'
            )
        else:
            pdf_fallback = (
                "::: {.callout-warning}\n## 静态表示未生成\n"
                f"{textual_fallback}\n\n原因：`{_safe_text(capture_error)}`\n:::"
            )
            static_evidence = f'<p class="qoder-render-diagnostic">静态证据未生成：{html.escape(capture_error or "unknown")}</p>'
        url = f"{FRONTEND_BASE.rstrip('/')}/#/visualizations/{visualization['visualization_id']}?embed=1"
        return (
            f'<figure class="qoder-connected"><iframe src="{html.escape(url)}" title="{title}" loading="lazy"></iframe>{static_evidence}<figcaption>{source}</figcaption></figure>',
            pdf_fallback,
        )

    encoded = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    block = (
        f'<figure class="qoder-viz" data-qoder-viz="{html.escape(renderer.get("owner", "unknown"))}">'
        f'<div class="qoder-viz-canvas" style="height:{int((visualization.get("parameters") or {}).get("height", 480))}px"></div>'
        f'<script type="application/json">{encoded}</script><figcaption>{title} · {source}</figcaption></figure>'
    )
    return block, pdf_fallback


def _block_qmd(block: dict[str, Any], project_dir: Path, *, portable: bool, vis_context=None, vis_exports=None) -> str:
    block_type = block.get("type")
    title = _safe_text(block.get("title"))
    body = _safe_text(block.get("body"))
    if block_type == "visualization" and (block.get("source_ref") or {}).get("visualization_id"):
        source_ref = block["source_ref"]
        if source_ref.get('revision'):
            if not vis_context or not vis_exports:
                raise ValueError('report_visualization_context_required')
            from modules.visIO import read_fixed_reference
            visualization = read_fixed_reference(vis_context, source_ref)
            if visualization['kind'] == 'phys_field':
                from .application import resolve_visualization_reference
                produced = resolve_visualization_reference(vis_context, source_ref, vis_exports)
                relative = _copy_media(produced['path'], project_dir/'assets'/'media', source_ref['visualization_id'])
                return f"![{title}]({relative})"
        else:
            visualization = get_visualization(source_ref["visualization_id"])
        if visualization.get("content_hash") != source_ref.get("content_hash"):
            return (
                "::: {.callout-warning}\n## 冻结素材校验失败\n"
                f"Visualization `{_safe_text(source_ref.get('visualization_id'))}` 的内容哈希与报告冻结引用不一致；"
                "为避免静默替换证据，本块未渲染。\n:::"
            )
        html_block, pdf_block = _visualization_html(visualization, project_dir, portable=portable)
        return f"::: {{.content-visible when-format=\"html\"}}\n{html_block}\n:::\n\n::: {{.content-visible when-format=\"typst\"}}\n{pdf_block}\n:::"
    if block_type in {"markdown", "source"}:
        heading = f"### {title}\n\n" if title and title != "待补充" else ""
        return heading + body
    if block_type == "callout":
        return f"::: {{.callout-note}}\n## {title or '说明'}\n{body}\n:::"
    if block_type == "metric":
        value = _safe_text(block.get("value"))
        unit = _safe_text(block.get("unit"))
        return f"::: {{.metric-block}}\n**{title}**\n\n# {value} {unit}\n:::"
    if block_type == "table":
        columns = block.get("columns") or []
        rows = block.get("rows") or []
        if not columns:
            return f"**{title}**\n\n暂无表格数据。"
        lines = ["| " + " | ".join(map(_safe_text, columns)) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
        lines.extend("| " + " | ".join(_safe_text(value) for value in row) + " |" for row in rows)
        return (f"### {title}\n\n" if title else "") + "\n".join(lines)
    if block_type == "divider":
        return "---"
    if block_type == "page_break":
        return "{{< pagebreak >}}"
    if block_type == "toc":
        return "<!-- Quarto TOC is enabled by the report theme. -->"
    return f"### {title or '诊断'}\n\n{body or '该块暂无可导出内容。'}"


def _document_qmd(document: dict[str, Any], project_dir: Path, *, portable: bool, vis_context=None, vis_exports=None) -> str:
    metadata = document.get("metadata") or {}
    output = [
        "---",
        f"title: {_yaml_string(metadata.get('title'))}",
        f"author: {_yaml_string(metadata.get('author'))}",
        "execute:",
        "  enabled: false",
        "---",
        "",
    ]
    for section in document.get("sections", []):
        if section.get("page_break_before"):
            output.append("{{< pagebreak >}}\n")
        output.append(f"## {_safe_text(section.get('title') or '未命名章节')}\n")
        if section.get("description"):
            output.append(_safe_text(section["description"]) + "\n")
        for row in section.get("rows", []):
            visible = [block for block in row.get("blocks", []) if not (block.get("layout") or {}).get("hidden")]
            if len(visible) > 1:
                output.append(":::: {.columns}\n")
            for block in visible:
                span = int((block.get("layout") or {}).get("span", 12))
                if (block.get("layout") or {}).get("page_break_before"):
                    output.append("{{< pagebreak >}}\n")
                if len(visible) > 1:
                    output.append(f"::: {{.column width=\"{span / 12:.4f}\"}}\n")
                output.append(_block_qmd(block, project_dir, portable=portable, vis_context=vis_context, vis_exports=vis_exports) + "\n")
                if len(visible) > 1:
                    output.append(":::\n")
            if len(visible) > 1:
                output.append("::::\n")
    return "\n".join(output)


def _theme_css() -> str:
    return """
:root{--q-primary:#1677ff;--q-accent:#0e9f9f;--q-border:#dfe4ec;--q-muted:#5b6b7f}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans CJK SC',sans-serif;color:#182230}
h1,h2,h3{letter-spacing:-.015em}.columns{gap:18px}.column{min-width:0}
.qoder-viz,.qoder-connected,.qoder-o3dv{margin:1rem 0;border:1px solid var(--q-border);border-radius:8px;padding:12px;background:#fff}
.qoder-viz canvas,.qoder-viz svg{max-width:100%}.qoder-connected iframe,.qoder-o3dv iframe{width:100%;height:520px;border:0;background:#161a20}
figcaption{margin-top:8px;color:var(--q-muted);font-size:.84rem}.metric-block{border-left:4px solid var(--q-primary);padding:12px 16px;background:#f4f6fa}
video,img{max-width:100%;height:auto}@media(max-width:720px){.columns{display:block!important}.column{width:100%!important}.qoder-connected iframe,.qoder-o3dv iframe{height:420px}}
.qoder-static-evidence{margin-top:8px}.qoder-static-evidence summary{cursor:pointer;color:var(--q-primary)}.qoder-render-diagnostic{padding:10px;background:#fff7e6;color:#8a4b08}
"""


def _copy_runtime_assets(project_dir: Path) -> None:
    """Copy pinned local renderer runtimes; no CDN is used by portable HTML."""
    modules = ROOT / "frontend" / "node_modules"
    assets = project_dir / "assets"
    copies = {
        modules / "echarts" / "dist" / "echarts.min.js": assets / "echarts.min.js",
        modules / "plotly.js-dist-min" / "plotly.min.js": assets / "plotly.min.js",
        modules / "vega" / "build" / "vega.min.js": assets / "vega.min.js",
        modules / "vega-lite" / "build" / "vega-lite.min.js": assets / "vega-lite.min.js",
        modules / "vega-embed" / "build" / "vega-embed.min.js": assets / "vega-embed.min.js",
        modules / "react" / "umd" / "react.production.min.js": assets / "react.production.min.js",
        modules / "react-dom" / "umd" / "react-dom.production.min.js": assets / "react-dom.production.min.js",
        modules / "@xyflow" / "react" / "dist" / "umd" / "index.js": assets / "react-flow.min.js",
        modules / "@xyflow" / "react" / "dist" / "style.css": assets / "react-flow.css",
    }
    for source, target in copies.items():
        if source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    perspective_root = assets / "perspective"
    for package in ("perspective", "perspective-viewer", "perspective-viewer-datagrid"):
        package_root = modules / "@finos" / package / "dist"
        for folder in ("cdn", "wasm", "css"):
            source = package_root / folder
            if source.is_dir():
                shutil.copytree(source, perspective_root / folder, dirs_exist_ok=True)
    (assets / "perspective-loader.js").write_text(
        "import './perspective/cdn/perspective-viewer.js';\n"
        "import './perspective/cdn/perspective-viewer-datagrid.js';\n",
        encoding="utf-8",
    )


def _write_project(export: dict[str, Any], *, vis_context=None, vis_exports=None) -> tuple[Path, dict[str, Any]]:
    version = get_report_version(export["report_id"], export["report_version"])
    document = version["document"]
    project_dir = EXPORT_ROOT / export["export_id"] / "project"
    if project_dir.exists():
        shutil.rmtree(project_dir)
    (project_dir / "assets").mkdir(parents=True, exist_ok=True)
    portable = export["mode"] == "portable"
    (project_dir / "index.qmd").write_text(_document_qmd(document, project_dir, portable=portable, vis_context=vis_context, vis_exports=vis_exports), encoding="utf-8")
    (project_dir / "report.css").write_text(_theme_css(), encoding="utf-8")
    (project_dir / "assets" / "report-runtime.js").write_text(_runtime_script(), encoding="utf-8")
    if portable:
        _copy_runtime_assets(project_dir)
    theme = document.get("theme") or {}
    config_lines = [
        "project:",
        "  type: default",
        "  output-dir: output",
        "lang: zh-CN",
        "resources:",
        "  - assets/**",
        "execute:",
        "  enabled: false",
        "format:",
        "  html:",
        f"    toc: {str(bool(theme.get('toc', True))).lower()}",
        "    toc-title: 目录",
        f"    number-sections: {str(bool(theme.get('number_sections', True))).lower()}",
        "    css: report.css",
        # Portable exports ship an explicit local asset tree. Connected exports
        # must preserve the frozen Visualization iframe URL; Quarto's resource
        # embedding rewrites it to a data: document and breaks Vite module URLs.
        "    embed-resources: false",
    ]
    if portable:
        config_lines.extend([
            "    include-in-header:",
            "      - text: |",
            '          <link rel="stylesheet" href="assets/react-flow.css">',
            '          <link rel="stylesheet" href="assets/perspective/css/themes.css">',
            '          <script src="assets/echarts.min.js"></script>',
            '          <script src="assets/plotly.min.js"></script>',
            '          <script src="assets/vega.min.js"></script>',
            '          <script src="assets/vega-lite.min.js"></script>',
            '          <script src="assets/vega-embed.min.js"></script>',
            '          <script src="assets/react.production.min.js"></script>',
            '          <script src="assets/react-dom.production.min.js"></script>',
            "          <script>window.jsxRuntime={Fragment:React.Fragment,jsx:function(t,p,k){return React.createElement(t,Object.assign({},p,{key:k==null?p&&p.key:k}));},jsxs:function(t,p,k){return React.createElement(t,Object.assign({},p,{key:k==null?p&&p.key:k}));}};</script>",
            '          <script src="assets/react-flow.min.js"></script>',
            "          <script>window.qoderPerspectiveReady=import('./assets/perspective-loader.js');</script>",
            '          <script defer src="assets/report-runtime.js"></script>',
        ])
    config_lines.extend([
        "  typst:",
        f"    toc: {str(bool(theme.get('toc', True))).lower()}",
        "    toc-title: 目录",
        f"    number-sections: {str(bool(theme.get('number_sections', True))).lower()}",
        f"    papersize: {str(theme.get('page_size', 'A4')).lower()}",
    ])
    if theme.get("orientation") == "landscape":
        config_lines.extend([
            "    include-in-header:",
            "      - text: |",
            "          #set page(flipped: true)",
        ])
    config = "\n".join(config_lines) + "\n"
    (project_dir / "_quarto.yml").write_text(config, encoding="utf-8")
    manifest = {
        "report_id": export["report_id"], "report_version": export["report_version"],
        "content_hash": version["content_hash"], "format": export["format"], "mode": export["mode"],
        "quarto_version": QUARTO_VERSION, "execute_enabled": False,
    }
    (project_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return project_dir, manifest


def run_export(export_id: str, *, vis_context=None, vis_exports=None) -> None:
    """执行一个持久化导出任务，并逐阶段写回成功产物或可重试错误。"""

    with _RUNNING_LOCK:
        if export_id in _RUNNING:
            return
        _RUNNING.add(export_id)
    try:
        export = get_export(export_id)
        # A retry starts a clean attempt. Do not leak the previous failure into
        # a successful task modal or persisted export record.
        update_export(export_id, status="running", stage="resolve-assets", error=None, output_path=None)
        version = get_report_version(export["report_id"], export["report_version"])
        document = version["document"]
        if document.get("document_type") == "reader-snapshot-v1":
            update_export(export_id, stage="capture-current-report")
            output_path, manifest = _capture_reader_report(export, {**document, "content_hash": version["content_hash"]})
            update_export(
                export_id, status="succeeded", stage="complete", output_path=str(output_path), manifest=manifest,
                error=None,
            )
            return
        project_dir, manifest = _write_project(export, vis_context=vis_context, vis_exports=vis_exports)
        update_export(export_id, stage="quarto-render", manifest=manifest)
        binary = find_quarto()
        if not binary:
            raise RuntimeError(f"QUARTO_NOT_INSTALLED: required {QUARTO_VERSION}")
        target_format = "typst" if export["format"] == "pdf" else "html"
        log_path = project_dir.parent / "quarto.log"
        result = subprocess.run(
            [binary, "render", "index.qmd", "--to", target_format], cwd=project_dir,
            capture_output=True, text=True, timeout=300, check=False,
        )
        log_path.write_text(result.stdout + "\n" + result.stderr, encoding="utf-8")
        update_export(export_id, log_path=str(log_path))
        if result.returncode != 0:
            raise RuntimeError(f"QUARTO_RENDER_FAILED: exit {result.returncode}")
        output_dir = project_dir / "output"
        if export["format"] == "pdf":
            candidates = list(output_dir.glob("*.pdf"))
            if not candidates:
                raise RuntimeError("QUARTO_OUTPUT_MISSING: PDF")
            output_path = candidates[0]
        elif export["mode"] == "portable":
            update_export(export_id, stage="package")
            archive = project_dir.parent / f"{export['report_id']}-v{export['report_version']}-html-portable.zip"
            with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
                for path in output_dir.rglob("*"):
                    if path.is_file():
                        bundle.write(path, path.relative_to(output_dir))
                for name in ("index.qmd", "_quarto.yml", "manifest.json"):
                    bundle.write(project_dir / name, Path("source") / name)
            output_path = archive
        else:
            candidates = list(output_dir.glob("*.html"))
            if not candidates:
                raise RuntimeError("QUARTO_OUTPUT_MISSING: HTML")
            output_path = candidates[0]
        update_export(
            export_id, status="succeeded", stage="complete", output_path=str(output_path),
            log_path=str(log_path), manifest={**manifest, "output_name": output_path.name, "bytes": output_path.stat().st_size},
            error=None,
        )
        if os.environ.get("QODER_KEEP_EXPORT_PROJECT") != "1":
            try:
                compact_export_directory(export_id, output_path=str(output_path))
            except Exception:  # noqa: BLE001 - cleanup must never invalidate a valid export
                pass
    except Exception as exc:  # noqa: BLE001
        current = get_export(export_id)
        update_export(
            export_id, status="failed", stage=current.get("stage") or "unknown",
            error={"code": str(exc).split(":", 1)[0], "message": str(exc), "retryable": True},
        )
        if os.environ.get("QODER_KEEP_EXPORT_PROJECT") != "1":
            try:
                compact_export_directory(export_id, failed=True)
            except Exception:  # noqa: BLE001 - diagnostics are already persisted
                pass
    finally:
        with _RUNNING_LOCK:
            _RUNNING.discard(export_id)


def start_export(export_id: str, *, vis_context=None, vis_exports=None) -> None:
    """把导出任务提交到单工作线程，防止多个 Quarto 进程争抢资源。"""

    _EXECUTOR.submit(run_export, export_id, vis_context=vis_context, vis_exports=vis_exports)
