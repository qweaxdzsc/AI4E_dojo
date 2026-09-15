import { Checkbox, Modal, Select } from "antd";
import type { useInferenceResults } from "./useInferenceResults";
import { splitLabel } from "./SamplePicker";
/** 配置仅查询和筛选固定结果，绝不改推理请求。 */
export function ResultViewSettings({view,open,onClose}:{view:ReturnType<typeof useInferenceResults>;open:boolean;onClose:()=>void}) {
 return <Modal title="结果显示配置" open={open} onCancel={onClose} onOk={onClose} okText="应用" okButtonProps={{"aria-label":"应用"}} cancelText="关闭"><div className="infer-view-settings">
 <label>物理量<Select aria-label="结果物理量" value={view.field||undefined} onChange={view.setField} options={view.fields}/></label>
 <label>指标<Select aria-label="结果指标" value={view.metric||undefined} onChange={view.setMetric} options={view.metrics.map(value=>({value,label:value}))}/></label>
 <label>分片<Select aria-label="结果分片" value={view.split||undefined} onChange={view.setSplit} options={view.splits.map(value=>({value,label:splitLabel(value)}))}/></label>
 <label>坐标尺度<Select aria-label="图表坐标尺度" value={view.scale} onChange={view.setScale} options={[{value:"linear",label:"线性"},{value:"log",label:"对数（只显示正值）"}]}/></label>
 <label>统计系列<Checkbox.Group value={view.series} onChange={v=>view.setSeries(v as string[])} options={[{value:"mean",label:"Mean"},{value:"median",label:"Median"},{value:"p90",label:"P90"},{value:"max",label:"Max"}]}/></label>
 </div></Modal>;
}
