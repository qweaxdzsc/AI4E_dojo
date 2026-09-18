import { Alert, Modal, Radio, Select, Switch } from "antd";
import { useState } from "react";
import type { TickDensity, useInferenceResults } from "./useInferenceResults";
/** 图表只选择当前表格的数值列，并配置刻度、网格与点数值；草稿仅在应用后写入任务图表配置。 */
export function ChartViewSettings({view,onClose}:{view:ReturnType<typeof useInferenceResults>;onClose:()=>void}) {
 const [draft,setDraft]=useState(view.chart);
 return <Modal title="图表坐标配置" open onCancel={onClose} onOk={()=>{view.setChart(draft);onClose();}} okText="应用" cancelText="取消" okButtonProps={{disabled:!draft.series.length,"aria-label":"应用"}} cancelButtonProps={{"aria-label":"取消"}} width={680} styles={{body:{maxHeight:"min(70vh,560px)",overflow:"auto"}}}><div className="infer-view-settings">
 <label>X 轴<Select aria-label="图表 X 轴" disabled value={view.xLabel} options={[{value:view.xLabel,label:view.xLabel}]}/></label><p className="infer-config-help">由表格的{view.config.mode==="checkpoint"?" Checkpoint 对比":"样本对比"}模式确定；修改模式请使用表格配置。</p>
 <label>Y 轴字段（多选）<Select aria-label="图表 Y 轴字段" mode="multiple" maxTagCount="responsive" value={draft.series} options={view.columns.map(c=>({value:c.id,label:c.label}))} onChange={series=>setDraft({...draft,series})}/></label>
 <label>Y 轴尺度<Select aria-label="图表坐标尺度" value={draft.scale} onChange={scale=>setDraft({...draft,scale})} options={[{value:"linear",label:"线性"},{value:"log",label:"对数（只显示正值）"}]}/></label>
 <div className="infer-display-options">
 <label>刻度<div className="infer-switch-row"><Switch aria-label="刻度" checked={draft.ticks} onChange={ticks=>setDraft({...draft,ticks})}/> <span>{draft.ticks?"显示轴刻度":"隐藏轴刻度"}</span></div></label>
 <label>网格线<div className="infer-switch-row"><Switch aria-label="网格线" checked={draft.grid} onChange={grid=>setDraft({...draft,grid})}/> <span>{draft.grid?"显示网格":"隐藏网格"}</span></div></label>
 <label>点数值<div className="infer-switch-row"><Switch aria-label="点数值" checked={draft.pointLabels} onChange={pointLabels=>setDraft({...draft,pointLabels})}/> <span>{draft.pointLabels?"每个点显示数值":"不显示点数值"}</span></div></label>
 </div>
 <div className="infer-config-control" role="radiogroup" aria-label="刻度疏密"><span>刻度疏密</span><Radio.Group disabled={!draft.ticks} value={draft.tickDensity} onChange={e=>setDraft({...draft,tickDensity:e.target.value as TickDensity})} options={[{value:"dense",label:"密"},{value:"normal",label:"中"},{value:"sparse",label:"疏"}]}/></div>
 <Alert type="info" message="每个 Y 轴字段对应一条系列，直接使用表格数值。不同单位的字段请分开查看。样本很多时打开点数值会重叠，默认关闭。"/>
 </div></Modal>;
}
