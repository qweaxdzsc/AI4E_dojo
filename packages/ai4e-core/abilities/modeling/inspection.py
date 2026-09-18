"""真实模型结构跟踪；仅成功前向的完整 HTML 可以原子发布。"""

import sys
from contextlib import redirect_stdout
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.inference.randomness import preserve_randomness

_FIT_ENTIRE_GRAPH = "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;"
_FIT_WIDTH = "const scale = Math.min(1, (width * 0.92) / Math.max(graphWidth, 1));"
_CENTER_VERTICAL = "height / 2 - (minY + graphHeight / 2) * scale"
_TOP_ALIGN = "24 - minY * scale"
# 根适配器之下一层模块收成盒，避免正式网络展开成整图算子。
_MODULE_TRACE_DEPTH = 1


def fit_graph_viewport(html: str) -> str:
    """把 TorchVista 默认的整图塞进视口改成按宽度适配，避免深网络缩成看不见的细线。"""
    if _FIT_ENTIRE_GRAPH not in html:
        raise RuntimeError("TorchVista 结构页缺少整图缩放语句，无法改成按宽度显示")
    return html.replace(_FIT_ENTIRE_GRAPH, _FIT_WIDTH, 1).replace(_CENTER_VERTICAL, _TOP_ALIGN, 1)


def trace(
    model: torch.nn.Module,
    inputs,
    output_dir: Path,
    *,
    revision: str,
    input_source: dict,
    predict=None,
) -> dict:
    """保持正式模型参数，以真实输入执行中等体量 TorchVista 模块图并记录来源。"""
    from torchvista import trace_model

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "model.html"

    class ForwardAdapter(torch.nn.Module):
        def __init__(self, network):
            super().__init__()
            self.network = network

        def forward(self, values):
            return predict(self.network, values)

    target_model = ForwardAdapter(model).eval() if predict else model.eval()
    html = ""
    with preserve_randomness(), atomic_path(target) as temporary, redirect_stdout(sys.stderr):
        trace_model(
            target_model,
            inputs,
            export_format="html",
            export_path=str(temporary),
            show_compressed_view=True,
            collapse_modules_after_depth=_MODULE_TRACE_DEPTH,
            forced_module_tracing_depth=_MODULE_TRACE_DEPTH,
        )
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("TorchVista 未生成结构资产")
        html = fit_graph_viewport(temporary.read_text())
        temporary.write_text(html, encoding="utf-8")
    record = {
        "schema_version": 1,
        "status": "succeeded",
        "path": str(target),
        "configuration_revision": revision,
        "input_source": input_source,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_type": type(model).__module__ + "." + type(model).__name__,
        "graph_nodes": html.count('"node_type"'),
        "graph_view": "compressed_modules",
    }
    save_json(output_dir / "model-inspection.json", record)
    return record
