import { Button, Empty } from "antd";
import type { useInferenceResults } from "./useInferenceResults";
import type { Statistic } from "./model";
import { displayNumber } from "./InferenceMetricTable";
const colors=["#0867ff","#00c17a","#ff7800","#8845cf"];
/** 图表仅把后台统计映射到坐标，缺失与非正对数值留空，不重复预测。 */
export function InferenceCharts({view,onConfigure}:{view:ReturnType<typeof useInferenceResults>;onConfigure:()=>void}) {
 const blocked=view.rows.length>1&&!(["comparable","compatible"].includes(view.comparison?.status));
 const values=view.rows.flatMap(r=>view.series.map(k=>r[k as keyof Statistic]).filter(v=>typeof v==="number"&&(view.scale!=="log"||v>0))) as number[];
 const valid=(v:unknown):v is number=>typeof v==="number"&&Number.isFinite(v)&&(view.scale!=="log"||v>0);
 const transform=(v:number)=>view.scale==="log"?Math.log10(v):v;
 const numbers=values.map(transform),lo=numbers.length?Math.min(...numbers):0,hi=numbers.length?Math.max(...numbers):1;
 const lower=view.scale==="log"?Math.floor(lo):Math.min(0,lo),upper=hi===lower?lower+1:hi+(hi-lower)*.12;
 const x=(i:number)=>85+(i+.5)*1195/Math.max(1,view.rows.length),y=(v:number)=>102-(transform(v)-lower)/(upper-lower)*78;
 return <section className="infer-card infer-chart" data-region="chart"><header><h3>8. {view.kind==="line"?"折线图":view.kind==="scatter"?"散点图":"柱状图"}</h3><div className="infer-tabs">{[["line","折线图"],["scatter","散点图"],["bar","柱状图"]].map(([k,label])=><Button key={k} className={view.kind===k?"active":""} onClick={()=>view.setKind(k)}>{label}</Button>)}</div><div className="infer-chart-legend">{view.series.map((s,i)=><span key={s} style={{color:colors[i]}}>● {s==="p90"?"P90":s[0].toUpperCase()+s.slice(1)}</span>)}</div><Button aria-label="配置" onClick={onConfigure} disabled={!view.fields.length}>配置</Button></header>
 {blocked?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={view.comparison?.reason||"比较口径未通过核验"}/>:!values.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={view.rows.length?"当前指标或坐标范围没有有效数值":"尚无图表数据"}/>:<svg role="img" aria-label={`${view.metric} 按 Checkpoint 的${view.kind}图`} viewBox="0 0 1400 154" preserveAspectRatio="none">
 {[0,1,2,3].map(i=>{const v=lower+(upper-lower)*i/3, yy=102-i*26;return <g key={i}><line x1="78" x2="1390" y1={yy} y2={yy} stroke="#d9e7fa" strokeDasharray="2 3"/><text x="68" y={yy+4} textAnchor="end">{displayNumber(view.scale==="log"?10**v:v)}</text></g>})}<path d="M78 20V102H1390" stroke="#8194bd" fill="none"/>
 {view.series.map((s,j)=>{const points=view.rows.map((r,i)=>({v:r[s as keyof Statistic],i}));const segments:string[]=[];let path="";points.forEach(({v,i})=>{if(valid(v)){path+=`${path?"L":"M"}${x(i)},${y(v)} `;}else if(path){segments.push(path);path="";}});if(path)segments.push(path);return <g key={s} fill={colors[j]}>{view.kind==="line"&&segments.map((d,i)=><path key={i} d={d} fill="none" stroke={colors[j]} strokeWidth="1.5"/>)}{points.filter(p=>valid(p.v)).map(({v,i})=>view.kind==="bar"?<rect key={i} x={x(i)+(j-view.series.length/2)*Math.min(16,200/view.rows.length)} y={Math.min(y(v as number),y(view.scale==="log"?10**lower:0))} width={Math.min(14,180/view.rows.length)} height={Math.max(1,Math.abs(y(v as number)-y(view.scale==="log"?10**lower:0)))}><title>{view.rows[i].checkpoint}: {s} {displayNumber(v as number)}</title></rect>:<circle key={i} cx={x(i)} cy={y(v as number)} r="3"><title>{view.rows[i].checkpoint}: {s} {displayNumber(v as number)}</title></circle>)}</g>})}
 {view.rows.map((r,i)=><text key={r.checkpoint_id} x={x(i)} y="125" textAnchor="middle"><title>{r.checkpoint_id}</title>{r.checkpoint.length>23?r.checkpoint.slice(0,20)+"…":r.checkpoint}</text>)}<text x="715" y="150" textAnchor="middle">Checkpoint</text><text transform="translate(17 67) rotate(-90)" textAnchor="middle">{view.metric}</text></svg>}
 </section>;
}
