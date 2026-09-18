import { useEffect, useMemo, useState } from "react";
import type { Results } from "./model";
export const aggregations = [{value:"mean",label:"Mean"},{value:"median",label:"Median"},{value:"p90",label:"P90"},{value:"max",label:"Max"}];
export type TableConfig = {mode:"checkpoint"|"sample"; checkpoint_id:string; pairs:string[]; aggregations:string[]};
export type TickDensity = "dense"|"normal"|"sparse";
export type ChartConfig = {series:string[];scale:string;ticks:boolean;tickDensity:TickDensity;grid:boolean;pointLabels:boolean};
export const pairKey=(field:string,metric:string)=>JSON.stringify([field,metric]);
export const chartStorageKey=(project:string,task:string)=>`dojo.infer.chart.${project}.${task}`;
/** 图表显示默认：刻度与网格开，点数值关，避免样本多时标签重叠。 */
export function defaultChartConfig():ChartConfig {
 return {series:[],scale:"linear",ticks:true,tickDensity:"normal",grid:true,pointLabels:false};
}
/** 读取已保存图表选项；缺字段回落到默认，不沿用未知键。 */
export function normalizeChartConfig(raw:unknown):ChartConfig {
 const fallback=defaultChartConfig();
 if(!raw||typeof raw!=="object")return fallback;
 const value=raw as Record<string,unknown>;
 return {
  series:Array.isArray(value.series)?value.series.filter((item):item is string=>typeof item==="string"):fallback.series,
  scale:value.scale==="log"?"log":"linear",
  ticks:value.ticks!==false,
  tickDensity:value.tickDensity==="dense"||value.tickDensity==="sparse"?value.tickDensity:"normal",
  grid:value.grid!==false,
  pointLabels:value.pointLabels===true,
 };
}
function readStoredChart(scope?:{project:string;task:string}):ChartConfig {
 if(!scope||typeof localStorage==="undefined")return defaultChartConfig();
 try{return normalizeChartConfig(JSON.parse(localStorage.getItem(chartStorageKey(scope.project,scope.task))||"null"));}
 catch{return defaultChartConfig();}
}
function writeStoredChart(scope:{project:string;task:string}|undefined,chart:ChartConfig) {
 if(!scope||typeof localStorage==="undefined")return;
 localStorage.setItem(chartStorageKey(scope.project,scope.task),JSON.stringify(chart));
}
/** 仅将已有指标展开成字段和行；跨样本聚合由后台提供。图表显示选项按任务写入浏览器，刷新后仍在。 */
export function useInferenceResults(value:Results,scope?:{project:string;task:string}) {
 const stats=value.statistics||[], records=value.records||[];
 const pairs=useMemo(()=>[...new Map(stats.map(r=>[pairKey(r.field_id,r.metric),{value:pairKey(r.field_id,r.metric),field:r.field_id,metric:r.metric,fieldLabel:stats.some(other=>other.field===r.field&&other.field_id!==r.field_id)?`${r.field} [${r.field_id}]`:r.field,label:`${stats.some(other=>other.field===r.field&&other.field_id!==r.field_id)?`${r.field} [${r.field_id}]`:r.field} · ${r.metric}`,unit:r.unit}])).values()],[value.statistics]);
 // 运行中的批次可能尚未产出某个 checkpoint 的聚合统计；结果成员仍是
 // 服务端已提交的权威清单，因此先按 checkpoint 身份占位，避免表格把它误合并/隐藏。
 const checkpointEntries=[...stats,...records,...(value.items||[]).map(item=>({checkpoint_id:item.checkpoint?.id,checkpoint:item.checkpoint?.name||item.checkpoint?.id}))].filter(r=>r.checkpoint_id);
 const checkpoints=[...new Map(checkpointEntries.map(r=>[r.checkpoint_id,{value:r.checkpoint_id,label:r.checkpoint||r.checkpoint_id}])).values()];
 const [config,setConfig]=useState<TableConfig>({mode:"checkpoint",checkpoint_id:"",pairs:[],aggregations:["mean","median","p90","max"]});
 const [chart,setChart]=useState<ChartConfig>(()=>readStoredChart(scope)),[kind,setKind]=useState("line");
 const selected=pairs.filter(p=>config.pairs.includes(p.value));
 useEffect(()=>{setChart(readStoredChart(scope));},[scope?.project,scope?.task]);
 useEffect(()=>{setConfig(old=>({...old,pairs:old.pairs.some(id=>pairs.some(p=>p.value===id))?old.pairs.filter(id=>pairs.some(p=>p.value===id)):pairs.slice(0,1).map(p=>p.value),checkpoint_id:checkpoints.some(c=>c.value===old.checkpoint_id)?old.checkpoint_id:checkpoints[0]?.value||""}));},[JSON.stringify(pairs),JSON.stringify(checkpoints)]);
 const columns=selected.flatMap(p=>(config.mode==="checkpoint"?config.aggregations:[""]).map(aggregate=>({id:JSON.stringify([p.field,p.metric,aggregate]),pair:p,aggregate,label:`${p.label}${aggregate?` · ${aggregations.find(a=>a.value===aggregate)?.label}`:""}${p.unit?` (${p.unit})`:""}`})));
 useEffect(()=>{setChart(old=>normalizeChartConfig({...old,series:old.series.some(id=>columns.some(c=>c.id===id))?old.series.filter(id=>columns.some(c=>c.id===id)):columns.slice(0,3).map(c=>c.id)}));},[JSON.stringify(columns.map(c=>c.id))]);
 useEffect(()=>{writeStoredChart(scope,chart);},[scope?.project,scope?.task,chart]);
 type Row={id:string;label:string;split?:string;count?:number;cells:Record<string,number|null>;reasons:Record<string,string>};
 const rows:Row[]=[];
 if(config.mode==="checkpoint"){
  for(const cp of checkpoints){const cells:Row["cells"]={},reasons:Row["reasons"]={};let found=false,count=0;
   for(const col of columns){const stat=stats.find(r=>r.checkpoint_id===cp.value&&r.split==="__all__"&&r.field_id===col.pair.field&&r.metric===col.pair.metric);if(stat){found=true;count=Math.max(count,stat.expected);}
    cells[col.id]=stat?(stat as any)[col.aggregate]:null;reasons[col.id]=!stat?"尚无全部样本的聚合结果":`有效 ${stat.valid} / ${stat.expected}${stat.complete?"":"；部分结果"}${stat.undefined_reasons?.length?`；${stat.undefined_reasons.join("；")}`:""}`;
   }rows.push({id:cp.value,label:cp.label,count,cells,reasons});
  }
 }else{
  const available=records.filter(r=>r.checkpoint_id===config.checkpoint_id);
  for(const r of available){const id=JSON.stringify([r.split,r.sample]);if(rows.some(row=>row.id===id))continue;
   const cells:Row["cells"]={},reasons:Row["reasons"]={};
   for(const col of columns){const record=available.find(v=>v.split===r.split&&v.sample===r.sample&&v.field_id===col.pair.field);cells[col.id]=record?.values?.[col.pair.metric]??null;reasons[col.id]=record?.undefined?.[col.pair.metric]||(cells[col.id]==null?"该样本未交付此指标":"固定样本指标");}
   rows.push({id,label:r.sample,split:r.split,cells,reasons});
  }
 }
 const applyChart=(next:ChartConfig)=>setChart(normalizeChartConfig(next));
 return {config,setConfig,chart,setChart:applyChart,kind,setKind,pairs,checkpoints,columns,rows,comparison:value.comparison,xLabel:config.mode==="checkpoint"?"Checkpoint":"样本",exportSelection:{view:{...config,pairs:selected.map(p=>({field_id:p.field,metric:p.metric}))}}};
}
