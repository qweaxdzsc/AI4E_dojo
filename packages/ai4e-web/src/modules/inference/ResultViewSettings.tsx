import { Alert, Checkbox, Modal, Radio, Select } from "antd";
import { useState } from "react";
import { aggregations, type useInferenceResults } from "./useInferenceResults";
/** 表格字段配置；草稿仅在应用后改变表格，关闭不保存。 */
export function ResultViewSettings({view,onClose}:{view:ReturnType<typeof useInferenceResults>;onClose:()=>void}) {
 const [draft,setDraft]=useState(view.config);
 const fields=[...new Map(view.pairs.map(p=>[p.field,{id:p.field,label:p.fieldLabel}])).values()];
 const valid=draft.pairs.length>0&&(draft.mode==="sample"?!!draft.checkpoint_id:draft.aggregations.length>0);
 return <Modal title="表格字段配置" open onCancel={onClose} onOk={()=>{view.setConfig(draft);onClose();}} okText="应用" cancelText="取消" okButtonProps={{disabled:!valid,"aria-label":"应用"}} cancelButtonProps={{"aria-label":"取消"}} width={680}><div className="infer-view-settings">
 <div className="infer-config-control"><span>对比模式</span><Radio.Group value={draft.mode} onChange={e=>setDraft({...draft,mode:e.target.value})} options={[{value:"checkpoint",label:"Checkpoint 对比"},{value:"sample",label:"样本对比"}]}/></div>
 {draft.mode==="checkpoint"?<><Alert type="info" message="每行一个 Checkpoint，默认聚合本批次全部分片的所有样本。"/><div className="infer-config-control"><span>聚合方式（多选）</span><Checkbox.Group value={draft.aggregations} options={aggregations} onChange={v=>setDraft({...draft,aggregations:v as string[]})}/></div></>:<label>Checkpoint<Select aria-label="样本对比 Checkpoint" value={draft.checkpoint_id||undefined} options={view.checkpoints} onChange={checkpoint_id=>setDraft({...draft,checkpoint_id})}/></label>}
 <div><strong>物理量与指标（表格字段）</strong><p className="infer-config-help">逐个物理量选择已计算的指标；每个组合生成独立列。</p></div>
 <div className="infer-pair-options">{fields.map(f=><fieldset key={f.id}><legend>{f.label}</legend><Checkbox.Group value={draft.pairs.filter(id=>view.pairs.some(p=>p.field===f.id&&p.value===id))} options={view.pairs.filter(p=>p.field===f.id).map(p=>({value:p.value,label:p.metric}))} onChange={v=>setDraft({...draft,pairs:[...draft.pairs.filter(id=>!view.pairs.some(p=>p.field===f.id&&p.value===id)),...v as string[]]})}/></fieldset>)}</div>
 {!view.pairs.length&&<Alert type="info" message="暂无已推理的物理量与指标；完成计算后可选择字段。"/>}
 <p className="infer-config-help">预计 {draft.pairs.length*(draft.mode==="checkpoint"?draft.aggregations.length:1)} 个指标列；不可定义的数值保留原因。</p>
 </div></Modal>;
}
