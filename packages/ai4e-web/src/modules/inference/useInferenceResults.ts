import { useEffect, useMemo, useState } from "react";
import type { Results } from "./model";
/** 已提交结果的显示范围独立于当前编辑选择，不触发预测。 */
export function useInferenceResults(value:Results) {
 const rows=value.statistics||[];
 const [field,setField]=useState(""),[metric,setMetric]=useState(""),[split,setSplit]=useState(""),[kind,setKind]=useState("line"),[scale,setScale]=useState("linear"),[series,setSeries]=useState(["mean","median","p90"]);
 const fields=useMemo(()=>[...new Map(rows.map(r=>[r.field_id,{value:r.field_id,label:r.field+(r.unit?` (${r.unit})`:"")}])).values()],[rows]);
 const metrics=[...new Set(rows.filter(r=>!field||r.field_id===field).map(r=>r.metric))];
 const splits=[...new Set(rows.map(r=>r.split))];
 useEffect(()=>{if(!fields.some(f=>f.value===field))setField(fields[0]?.value||"");},[fields,field]);
 useEffect(()=>{if(!metrics.includes(metric))setMetric(metrics.includes("relative_l2")?"relative_l2":metrics[0]||"");},[metrics.join(","),metric]);
 useEffect(()=>{if(!splits.includes(split))setSplit(splits[0]||"");},[splits.join(","),split]);
 return {comparison:value.comparison,field,setField,metric,setMetric,split,setSplit,kind,setKind,scale,setScale,series,setSeries,fields,metrics,splits,rows:rows.filter(r=>r.field_id===field&&r.metric===metric&&r.split===split)};
}
