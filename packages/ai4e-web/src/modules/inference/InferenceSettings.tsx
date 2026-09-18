import { Alert, Button, Checkbox, InputNumber, Select, Tooltip } from "antd";
import { PlayCircleFilled, InfoCircleOutlined } from "@ant-design/icons";
import type { useInference } from "./useInference";

/** 推理参数和实际批次预算；网格化导出在训练集不能还原 VTK 时置灰。 */
export function InferenceSettings({m}:{m:ReturnType<typeof useInference>}) {
 const count=m.sampleSelection.length, splits=new Set(m.sampleSelection.map(s=>s.split)).size;
 const meshAvailable=m.meshExportAvailable;
 const reason=!m.selected.length?"请先选择检查点":!count?"请先选择样本":m.selectionSupported&&!m.fieldIds.length?"请至少选择一个物理量":m.selectionSupported&&m.options.evaluate&&!m.metricIds.length?"请至少选择一个指标":!m.ready?"请检查输入、设备及输出选项":"";
 return <section className="infer-card infer-settings" data-region="settings">
  <h3>推理配置</h3>
  <div className="infer-settings-body">
   <div className="infer-settings-controls">
    <label>执行设备<Select aria-label="推理设备" value={m.device||undefined} onChange={m.setDevice} options={m.catalog.device_options.map(d=>({value:d.id,label:d.label+(d.busy?"（占用）":"")}))}/></label>
    <label>查询块大小<InputNumber aria-label="推理查询块大小" min={1} precision={0} value={m.options.query_chunk_size} onChange={v=>m.setOptions({...m.options,query_chunk_size:v||0})}/></label>
    <div className="infer-output-options">
     <Checkbox checked={m.options.evaluate} onChange={e=>m.setOptions({...m.options,evaluate:e.target.checked})}>评估指标</Checkbox>
     <Checkbox checked={m.options.export_pointcloud} onChange={e=>m.setOptions({...m.options,export_pointcloud:e.target.checked})}>导出点云数据</Checkbox>
     <Tooltip title={meshAvailable?"":(m.meshExportReason||"训练集没有可还原的 VTK 网格")}>
      <Checkbox disabled={!meshAvailable} checked={meshAvailable&&m.options.export_mesh} onChange={e=>m.setOptions({...m.options,export_mesh:e.target.checked,export_vtk:e.target.checked})}>导出VTK网格化数据</Checkbox>
     </Tooltip>
    </div>
    <div className="infer-settings-actions">
     <Tooltip title={reason}><Button disabled={!m.ready||m.busy} onClick={()=>m.run(true)}>检查推理配置</Button></Tooltip>
     <Tooltip title={m.running?"已有推理批次正在运行，请等待完成或取消后再提交":reason}><Button aria-label="开始计算" type="primary" icon={<PlayCircleFilled/>} disabled={!m.ready||m.running} loading={m.busy} onClick={()=>m.run()}>开始计算</Button></Tooltip>
    </div>
   </div>
   <div className="infer-budget" title={`${m.selected.length} 个检查点 × ${splits} 个分片 = ${m.selected.length*splits} 个串行子运行；字段按分量评价`}><InfoCircleOutlined/> <span>已选择 {m.selected.length} 个 Checkpoint × {count} 个样本 × {m.fieldIds.length} 个物理量 × {m.metricIds.length} 个指标</span></div>
   {!meshAvailable&&<Alert type="info" showIcon message="当前训练集没有可还原的 VTK 网格，已禁用导出 VTK 网格化数据。点云仍可写出预测与真值。"/>}
   {meshAvailable&&!m.options.export_mesh&&<Alert type="warning" showIcon message="已关闭导出 VTK 网格化数据。本次不会把预测回贴到原始网格；需要网格化结果时请重新勾选并再跑推理。"/>}
   {!m.options.export_pointcloud&&<Alert type="warning" showIcon message="已关闭导出点云数据。本次不会写出锚点 VTK 点云。"/>}
   {m.running&&<Alert type="info" showIcon message="推理已提交到运行队列，当前批次执行期间不能重复开始计算。"/>}
   <p className="infer-vtk-note">默认导出点云和 VTK 网格化数据，同文件写入预测与真值。网格化只认来源 VTK/VTKHDF 文件名或已绑定的连接关系路径；没有来源时该项置灰。纯粹空网格不会写出。关闭保存预测时不能单独出 VTK。</p>
  </div>
 </section>;
}
