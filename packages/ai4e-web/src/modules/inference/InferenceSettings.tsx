import { Button, Checkbox, InputNumber, Select, Tooltip } from "antd";
import { PlayCircleFilled, InfoCircleOutlined } from "@ant-design/icons";
import type { useInference } from "./useInference";
/** 推理参数和实际批次预算；关闭保存同时关闭网格输出。 */
export function InferenceSettings({m}:{m:ReturnType<typeof useInference>}) {
 const count=m.sampleSelection.length, splits=new Set(m.sampleSelection.map(s=>s.split)).size;
 const reason=!m.selected.length?"请先选择检查点":!count?"请先选择样本":m.selectionSupported&&!m.fieldIds.length?"请至少选择一个物理量":m.selectionSupported&&m.options.evaluate&&!m.metricIds.length?"请至少选择一个指标":!m.ready?"请检查输入、设备及输出选项":"";
 return <section className="infer-card infer-settings" data-region="settings"><h3>5. 推理配置</h3><div className="infer-settings-row">
 <label>执行设备<Select aria-label="推理设备" value={m.device||undefined} onChange={m.setDevice} options={m.catalog.device_options.map(d=>({value:d.id,label:d.label+(d.busy?"（占用）":"")}))}/></label>
 <label>查询块大小<InputNumber aria-label="推理查询块大小" min={1} precision={0} value={m.options.query_chunk_size} onChange={v=>m.setOptions({...m.options,query_chunk_size:v||0})}/></label>
 <div className="infer-output-options">{(["evaluate","save_predictions","export_vtk"] as const).map((k,i)=><Checkbox key={k} disabled={k==="export_vtk"&&!m.options.save_predictions} checked={m.options[k]} onChange={e=>m.setOptions({...m.options,[k]:e.target.checked,...(k==="save_predictions"&&!e.target.checked?{export_vtk:false}:{})})}>{["评估指标","保存数据","导出网格"][i]}</Checkbox>)}</div>
 <div className="infer-budget" title={`${m.selected.length} 个检查点 × ${splits} 个分片 = ${m.selected.length*splits} 个串行子运行；字段按分量评价`}><InfoCircleOutlined/> 已选择 {m.selected.length} 个 Checkpoint × {count} 个样本 × {m.fieldIds.length} 个物理量 × {m.metricIds.length} 个指标</div>
 <Tooltip title={reason}><Button disabled={!m.ready||m.busy} onClick={()=>m.run(true)}>检查推理配置</Button></Tooltip><Tooltip title={reason}><Button aria-label="开始计算" type="primary" icon={<PlayCircleFilled/>} disabled={!m.ready} loading={m.busy} onClick={()=>m.run()}>开始计算</Button></Tooltip>
 </div></section>;
}
