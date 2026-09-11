import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import {Alert, Checkbox, InputNumber, Select, Space, Spin, } from "antd";
import { useCallback, useEffect, useState } from "react";
import { ExecutionLog, listRuns } from "../executions";
import { BoundDatasetFiles } from "./BoundDatasetFiles";
import "./rawprep-workbench.css";
import type { DatasetBinding } from "./api";
import { capabilities, check, execute, read, save, datasetCatalog, trial } from "./api";
import { FieldExtractionEditor } from "./FieldExtractionEditor";

/** 页面只编辑 rawprep 段；实际执行配置由 task 覆盖机制捕获。 */
export function RawprepWorkbench({
  project,
  task,
}: {
  project: string;
  task: string;
}) {
  const [cfg, setCfg] = useState<any>(),
    [catalog,setCatalog] = useState<any>(),
    [binding,setBinding] = useState<DatasetBinding>(),
    [samples,setSamples] = useState<string[]>(),
    [caps, setCaps] = useState<any>(),
    [root, setRoot] = useState(""),
    [files, setFiles] = useState<string[]>([]),
    [all, setAll] = useState(true),
    [count, setCount] = useState(1),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [busy, setBusy] = useState(false),
    [dirty, setDirty] = useState(false),
    [entryEdit,setEntryEdit] = useState<any>(),
    [run, setRun] = useState<string>(),
    [key, setKey] = useState(() => crypto.randomUUID());
  useEffect(() => {
    Promise.all([read(project, task), capabilities(), listRuns(project, task)])
      .then(([c, a, r]) => {
        setCfg(c);
        setCaps(a);
        setRun(r.at(-1)?.id);
      })
      .catch((e) => setError(e.message));
  }, [project, task]);
  const receiveBinding=useCallback((value:DatasetBinding,saved:boolean)=>{
    setBinding(value);
    if(saved){setFiles([]);setSamples(undefined);setCatalog(undefined);setKey(crypto.randomUUID());read(project,task).then(c=>{setCfg(c);setDirty(false);setNotice('数据绑定已保存，请重新选择处理文件')}).catch(e=>setError(e.message))}
  },[project,task]);
  const selection = useCallback((r: string, f: string[]) => {
    setRoot(r);
    setFiles(f);
    setNotice("");
    setKey(crypto.randomUUID());
  }, []);
  const raw = {
    geometry: [],
    filters: {},
    statistics: { mode: "none", fields: [], position_fields: [] },
    vtkhdf: false,
    ...(cfg?.rawprep || {}),
  };
  const ready = binding?.status === "valid" && files.length > 0;
  const change = (next: any) => {
    if (JSON.stringify(next) === JSON.stringify(raw)) return;
    setCfg({ ...cfg, rawprep: next });
    setDirty(true);
    setNotice("");
    setKey(crypto.randomUUID());
  };
  async function action(kind: string) {
    if(kind!=="save"&&binding?.status!=="valid"){setError("请先绑定有效数据来源");return}
    if(kind!=="save"&&kind!=="check"&&!files.length){setError("请先选择处理文件");return}
    setBusy(true);
    setError("");
    setNotice("");
    try {
      let current = cfg;
      if (kind === "save" || dirty) {
        current = await save(project, task, cfg);
        setCfg(current);
        setDirty(false);
        if (kind === "save") {
          setNotice("配置已保存，未创建新版本");
          return;
        }
      }
      const v = {
        revision: current.revision,
        root,
        files,
        all_selected: all,
        count,
        idempotency_key: key,
        samples,
      };
      if (kind === "check") {
        const result = await check(project, task, v);
        setNotice(
          "校验通过：" +
            result.sample_count +
            " 个完整样本，" +
            result.file_count +
            " 个文件",
        );
      } else {
        const r = await (kind==="trial"?trial:execute)(project, task, v);
        setRun(r.id);
        setKey(crypto.randomUUID());
        setNotice("已提交运行 " + r.id);
      }
    } catch (e: any) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  if (!cfg || !caps)
    return error ? <Alert type="error" message={error} /> : <Spin />;
  return (
    <>
      <div className="workbench-grid layout">
        <section className="data-panel bound-source-column" id="stage-handoff"><BoundDatasetFiles key={JSON.stringify([binding?.sources,binding?.status])} project={project} task={task} binding={binding} onBinding={receiveBinding} onSelection={selection} disabled={dirty||busy}/></section>
        <section className="settings-panel">
          <div className="panel-title">
            <b>处理设置</b>
            <span className={"settings-badge"+(run?" done":"")}>{run?"已有运行":"未执行"}</span>
            <Button
              onClick={() => action("save")}
              disabled={!dirty}
              loading={busy}
            >
              保存配置
            </Button>
          </div>
          <div className="settings-body">
          <div className="processing-group setting"><h3>01　字段提取</h3><p>每个条目绑定来源，可配置多个输出。</p>
          <Button block type="primary" onClick={()=>setEntryEdit({id:crypto.randomUUID(),name:'字段提取',source_selector:'surface',outputs:[]})}>＋ 添加字段提取</Button>
          {(raw.extraction?.entries||[]).length===0&&<div className="extraction-empty">尚未添加自定义字段提取<br/><small>当前继续使用案例已声明的字段输出</small></div>}
          {(raw.extraction?.entries||[]).map((entry:any)=><div className="extraction-card" key={entry.id}><b>{entry.name}</b><p>{entry.outputs.map((o:any)=>o.name).join(' / ')}</p><Space><Button onClick={()=>setEntryEdit(entry)}>编辑</Button><Button onClick={()=>change({...raw,extraction:{entries:raw.extraction.entries.filter((v:any)=>v.id!==entry.id)}})}>删除</Button></Space></div>)}
          <small>共 {raw.extraction?.entries?.length||0} 个提取条目 · {(raw.extraction?.entries||[]).reduce((n:number,e:any)=>n+e.outputs.length,0)} 个输出</small></div>
          <div className="setting">
          <h3>02　清洗与实体校验</h3>
          {[
            ["surface", "mask", "清洗未参与网格的表面节点"],
            ["volume", "exterior_mask", "清洗体积域中的表面点"],
          ].map(([s, k, label]) => (
            <p key={s}>
              <Checkbox
                checked={raw.filters?.[s]?.includes(k)}
                onChange={(e) =>
                  change({
                    ...raw,
                    filters: {
                      ...raw.filters,
                      [s]: e.target.checked ? [k] : [],
                    },
                  })
                }
              >
                {label}
              </Checkbox>
            </p>
          ))}
          </div>
          <div className="setting">
          <h3>03　几何派生</h3>
          {[
            ["nearest_vertex", "最近顶点距离与方向"],
            ["nearest_surface", "点到网格表面距离"],
            ["surface_normals", "表面法向"],
            ["exterior_mask", "体积点重合标记"],
          ].map(([k, label]) => (
            <p key={k}>
              <Checkbox
                checked={raw.geometry.includes(k)}
                onChange={(e) =>
                  change({
                    ...raw,
                    geometry: e.target.checked
                      ? [...raw.geometry, k]
                      : raw.geometry.filter((v: string) => v !== k),
                  })
                }
              >
                {label}
              </Checkbox>
            </p>
          ))}
          </div>
          <div className="setting">
          <h3>04　落盘与交付</h3>
          <p><Checkbox checked>PT · 具名字段张量</Checkbox></p>
          <p>
            <Checkbox
              checked={raw.vtkhdf}
              onChange={(e) => change({ ...raw, format: raw.format || "pt", vtkhdf: e.target.checked })}
            >
              VTKHDF · 网格与场关联
            </Checkbox>
          </p>
          <p><Checkbox disabled>Zarr · 待接入</Checkbox></p>
          <small>PT 可减少实体；VTKHDF 保留原网格拓扑，筛除位置的回贴值为 NaN。</small>
          </div>
          <div className="setting">
          <h3>05　训练分片统计</h3>
          {[
            ["reference", "引用参考统计"],
            ["fit", "完整训练分片重算"],
            ["none", "不生成统计"],
          ].map(([value, label]) => (
            <p key={value}>
              <Checkbox
                checked={raw.statistics.mode === value}
                onChange={() => {
                  if (raw.statistics.mode === value) return;
                  change({ ...raw, statistics: { ...raw.statistics, mode: value } });
                }}
              >
                {label}
              </Checkbox>
            </p>
          ))}
          <small>统计只记录分片策略，不能在此手填数值。</small>
          </div>
          </div>
        </section>
        <section className="execution-panel">
          <div className="execution-head">
            <h2>执行配置</h2>
            <small>配置执行参数并启动原始数据处理流程。</small>
          </div>
          <div className="executionbox">
            <div className="execution-title"><h3>执行设置 ⓘ</h3></div>
            <label className="execution-check">
              <Checkbox
                checked={all}
                onChange={(e) => {
                  setAll(e.target.checked);
                  setKey(crypto.randomUUID());
                }}
              >
                所有已选择文件
              </Checkbox>
            </label>
            <div className="runrow">
              <span>总处理文件数量</span>
              <InputNumber
                aria-label="总处理文件数量"
                min={1}
                max={Math.max(1, files.length)}
                value={all ? files.length : count}
                disabled={all}
                onChange={(v) => {
                  setCount(v || 1);
                  setKey(crypto.randomUUID());
                }}
              />
              <span>个文件</span>
            </div>
            <div className="runrow">
              <span>并行线程数量</span>
              <InputNumber aria-label="并行线程数量" disabled value={1} />
              <span>个线程</span>
            </div>
            <Button
              className="runbutton"
              type="primary"
              aria-label="开始处理"
              disabled={!ready}
              loading={busy}
              onClick={() => action("execute")}
            >
              ▶ 执行
            </Button>
            <p className="execution-note">ⓘ　将按所选文件和配置核对完整样本依赖后执行。文件数量和样本数量独立，缺少依赖时拒绝。并行线程固定为 1。</p>
            <div className="execution-secondary">
              <Button disabled={!ready} onClick={() => { setBusy(true); datasetCatalog(project, task, { revision: cfg.revision, root, files }).then((v) => { setCatalog(v); setSamples(v.samples.map((s: any) => v.dataset_id === "nasa_crm" ? s.partition + "::" + s.sample_id : s.sample_id)); }).catch((e) => setError(e.message)).finally(() => setBusy(false)); }}>读取真实样本目录</Button>
              <Button disabled={binding?.status !== "valid"} loading={busy} onClick={() => action("check")}>校验输入与配置</Button>
              <Button disabled={!ready} loading={busy} onClick={() => action("trial")}>按所选范围试跑</Button>
            </div>
            {catalog && <><p>{catalog.sources.length} 个来源文件 · {catalog.samples.length} 个样本</p><Select mode="multiple" aria-label="执行样本" style={{ width: "100%" }} value={samples} onChange={setSamples} options={catalog.samples.map((sample: any) => ({ value: catalog.dataset_id === "nasa_crm" ? sample.partition + "::" + sample.sample_id : sample.sample_id, label: sample.partition + " / " + sample.sample_id }))} /></>}
            {dirty && <Alert type="info" message="执行时会先保存当前处理设置，不新增版本" />}
            {error && <Alert type="error" message={error} />}
            {notice && <Alert type="success" message={notice} />}
          </div>
        </section>
      </div>
      <ExecutionLog project={project} run={run} />
      {entryEdit && <FieldExtractionEditor project={project} task={task} root={root} files={files} entry={entryEdit} onCancel={()=>setEntryEdit(undefined)} onSave={entry=>{const entries=raw.extraction?.entries||[];change({...raw,extraction:{entries:entries.some((v:any)=>v.id===entry.id)?entries.map((v:any)=>v.id===entry.id?entry:v):[...entries,entry]}});setEntryEdit(undefined)}}/>}

    </>
  );
}
