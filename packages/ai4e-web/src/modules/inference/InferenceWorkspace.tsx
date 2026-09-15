import { Alert, Button } from "antd";
import { useEffect, useRef, useState } from "react";
import { ExecutionLog } from "../executions";
import { useInference } from "./useInference";
import { useInferenceResults } from "./useInferenceResults";
import { CheckpointPicker } from "./CheckpointPicker";
import { SamplePicker } from "./SamplePicker";
import { FieldPicker } from "./FieldPicker";
import { MetricPicker } from "./MetricPicker";
import { InferenceSettings } from "./InferenceSettings";
import { BatchProgress } from "./BatchProgress";
import { InferenceResults } from "./InferenceResults";
import { InferenceMetricTable } from "./InferenceMetricTable";
import { InferenceCharts } from "./InferenceCharts";
import { ResultViewSettings } from "./ResultViewSettings";
import { exportResults, download } from "./api";
import { statusLabel, terminal } from "./model";
import "./inference.css";
/** 四栏推理工作台；编辑范围与固定批次结果分离，日志和文件复用既有组件。 */
export function InferenceWorkspace({project,task,onOpenResult}:{project:string;task:string;onOpenResult:(batch:string,run:string,sample:string,index:number,split?:string)=>void}) {
 const m=useInference(project,task), view=useInferenceResults(m.result), [log,setLog]=useState(""), [settings,setSettings]=useState(false), [exporting,setExporting]=useState(false),[exportError,setExportError]=useState("");
 const progress=useRef<HTMLDetailsElement>(null);
 useEffect(()=>{if(progress.current&&m.detail&&!terminal(m.detail.status))progress.current.open=true;},[m.detail?.status]);
 async function exportFile(format:string){setExporting(true);setExportError("");try{const file=await exportResults(project,task,m.active,format,{field_id:view.field,metric:view.metric,split:view.split});const href=download(project,task,file);if(!href)throw new Error("导出缺少下载引用");const a=document.createElement("a");a.href=href;a.download=file.name;a.click();}catch(e:any){setExportError(e.message);}finally{setExporting(false);}}
 return <div className="inference-workspace" aria-busy={m.loading}>
 {m.error&&<Alert type="error" showIcon message={m.error}/>} {m.notice&&<Alert type="info" showIcon message={m.notice} closable/>}{exportError&&<Alert type="error" message={exportError}/>}
 {!m.selectionSupported&&<Alert type="info" message="旧 post 模板按原字段和指标执行；自定义选择需要独立 infer 模板。历史结果仍可查看和下载。"/>}
 <div className="infer-selection"><CheckpointPicker items={m.catalog.items} selected={m.selected} onChange={m.setSelected} disabled={m.busy}/><SamplePicker partitions={m.partitions} split={m.split} onSplit={m.changeSplit} selected={m.sampleIds} totalSelected={m.sampleSelection.length} onChange={m.setSampleIds} disabled={m.busy}/><FieldPicker items={m.fields} selected={m.fieldIds} onChange={m.setFieldIds} disabled={m.busy||!m.selectionSupported}/><MetricPicker items={m.metrics} selected={m.metricIds} onChange={m.setMetricIds} disabled={m.busy||!m.selectionSupported}/></div>
 {!m.samePreparation&&<Alert type="warning" message="所选权重准备记录不同，请分批提交"/>}{m.duplicate&&<Alert type="warning" message="所选检查点含相同内容，请保留一个标签"/>}
 <InferenceSettings m={m}/>
 <InferenceMetricTable view={view} onConfigure={()=>setSettings(true)} onExport={exportFile} exporting={exporting}/><InferenceCharts view={view} onConfigure={()=>setSettings(true)}/>
 <details ref={progress} className="infer-details"><summary>批次历史、进度与完整日志{m.detail?` · ${m.detail.name||m.active} · ${statusLabel(m.detail.status)} · ${m.detail.completed??0}/${m.detail.total??0}`:""}</summary><Button onClick={m.refresh} loading={m.loading}>刷新检查点与批次</Button><BatchProgress batches={m.batches} active={m.active} onSelect={id=>{m.setActive(id);setLog("");}} detail={m.detail} busy={m.busy} onCancel={m.cancel} onRetry={m.retry} onRecover={m.recover} onLog={setLog}/>{log&&<ExecutionLog project={project} run={log}/>}</details>
 <details className="infer-details" id="stage-handoff"><summary>固定结果文件与后处理交接 · {m.result.items.length} 组</summary><InferenceResults key={m.active} project={project} task={task} value={m.result} onOpen={(run,sample,index)=>onOpenResult(m.active,run,sample,index,m.result.items[index]?.split)}/></details>
 <ResultViewSettings view={view} open={settings} onClose={()=>setSettings(false)}/>
 </div>;
}
