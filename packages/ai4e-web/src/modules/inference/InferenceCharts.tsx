import { Button, Empty } from "antd";
import type { TickDensity, useInferenceResults } from "./useInferenceResults";
import { displayNumber } from "./InferenceMetricTable";
const colors=["#0867ff","#00c17a","#ff7800","#8845cf"];
const yDivisions:Record<TickDensity,number>={dense:6,normal:3,sparse:2};
const xLabelDenom:Record<TickDensity,number>={dense:20,normal:10,sparse:5};
const plot={left:78,right:1390,top:28,bottom:300,width:1400,height:368};
/** 图表仅把后台统计映射到坐标，缺失与非正对数值留空，不重复预测。 */
export function InferenceCharts({view,onConfigure}:{view:ReturnType<typeof useInferenceResults>;onConfigure:()=>void}) {
 const rowLabel=(r:typeof view.rows[number])=>r.split?`${({train:"训练集",eval:"评价集",validation:"评价集",test:"测试集"} as Record<string,string>)[r.split]||r.split} / ${r.label}`:r.label;
 const blocked=view.config.mode==="checkpoint"&&view.rows.length>1&&!(["comparable","compatible"].includes(view.comparison?.status));
 const values=view.rows.flatMap(r=>view.chart.series.map(k=>r.cells[k]).filter(v=>typeof v==="number"&&(view.chart.scale!=="log"||v>0))) as number[];
 const valid=(v:unknown):v is number=>typeof v==="number"&&Number.isFinite(v)&&(view.chart.scale!=="log"||v>0);
 const transform=(v:number)=>view.chart.scale==="log"?Math.log10(v):v;
 const numbers=values.map(transform),lo=numbers.length?Math.min(...numbers):0,hi=numbers.length?Math.max(...numbers):1;
 const lower=view.chart.scale==="log"?Math.floor(lo):Math.min(0,lo),upper=hi===lower?lower+1:hi+(hi-lower)*.12;
 const plotHeight=plot.bottom-plot.top;
 const x=(i:number)=>85+(i+.5)*1195/Math.max(1,view.rows.length),y=(v:number)=>plot.bottom-(transform(v)-lower)/(upper-lower)*plotHeight;
 const density=view.chart.tickDensity||"normal";
 const divisions=yDivisions[density];
 const xStep=Math.max(1,Math.ceil(view.rows.length/xLabelDenom[density]));
 const yTicks=Array.from({length:divisions+1},(_,i)=>{const v=lower+(upper-lower)*i/divisions;return {v,yy:plot.bottom-i*(plotHeight/divisions)};});
 const xTicks=view.rows.map((r,i)=>({r,i})).filter(({i})=>i%xStep===0||i===view.rows.length-1);
 const zero=y(view.chart.scale==="log"?10**lower:0);
 return <section className="infer-card infer-chart" data-region="chart"><header><h3>{view.kind==="line"?"折线图":view.kind==="scatter"?"散点图":"柱状图"}</h3><div className="infer-tabs">{[["line","折线图"],["scatter","散点图"],["bar","柱状图"]].map(([k,label])=><Button key={k} className={view.kind===k?"active":""} onClick={()=>view.setKind(k)}>{label}</Button>)}</div><div className="infer-chart-legend">{view.chart.series.map((s,i)=><span key={s} style={{color:colors[i%colors.length]}}>● {view.columns.find(c=>c.id===s)?.label}</span>)}</div><Button aria-label="配置" onClick={onConfigure} >配置</Button></header>
 {blocked?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={view.comparison?.reason||"比较口径未通过核验"}/>:!values.length?<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={view.rows.length?"当前指标或坐标范围没有有效数值":"尚无图表数据"}/>:<div className="infer-chart-body"><svg role="img" aria-label={`${view.xLabel} 对比${view.kind}图`} viewBox={`0 0 ${plot.width} ${plot.height}`} preserveAspectRatio="none" data-ticks={view.chart.ticks?"on":"off"} data-grid={view.chart.grid?"on":"off"} data-point-labels={view.chart.pointLabels?"on":"off"} data-tick-density={density}>
 {view.chart.grid&&yTicks.map(({yy},i)=><line key={`yg${i}`} x1={plot.left} x2={plot.right} y1={yy} y2={yy} stroke="#d9e7fa" strokeDasharray="2 3"/>)}
 {view.chart.grid&&xTicks.map(({i})=><line key={`xg${i}`} x1={x(i)} x2={x(i)} y1={plot.top} y2={plot.bottom} stroke="#d9e7fa" strokeDasharray="2 3"/>)}
 {view.chart.ticks&&yTicks.map(({v,yy},i)=><g key={`yt${i}`}><line x1={plot.left-6} x2={plot.left} y1={yy} y2={yy} stroke="#8194bd"/><text x={plot.left-10} y={yy+4} textAnchor="end">{displayNumber(view.chart.scale==="log"?10**v:v)}</text></g>)}
 <path d={`M${plot.left} ${plot.top}V${plot.bottom}H${plot.right}`} stroke="#8194bd" fill="none"/>
 {view.chart.series.map((s,j)=>{const points=view.rows.map((r,i)=>({v:r.cells[s],i}));const segments:string[]=[];let path="";points.forEach(({v,i})=>{if(valid(v)){path+=`${path?"L":"M"}${x(i)},${y(v)} `;}else if(path){segments.push(path);path="";}});if(path)segments.push(path);const color=colors[j%colors.length];return <g key={s} fill={color}>{view.kind==="line"&&segments.map((d,i)=><path key={i} d={d} fill="none" stroke={color} strokeWidth="1.5"/>)}{points.filter(p=>valid(p.v)).map(({v,i})=>{const n=v as number,cx=x(i),cy=y(n),label=`${rowLabel(view.rows[i])}: ${view.columns.find(c=>c.id===s)?.label} ${displayNumber(n)}`;return view.kind==="bar"?<g key={i}><rect x={cx+(j-view.chart.series.length/2)*Math.min(16,200/view.rows.length)} y={Math.min(cy,zero)} width={Math.min(14,180/view.rows.length)} height={Math.max(1,Math.abs(cy-zero))}><title>{label}</title></rect>{view.chart.pointLabels&&<text className="infer-point-label" x={cx} y={Math.min(cy,zero)-6} textAnchor="middle">{displayNumber(n)}</text>}</g>:<g key={i}><circle cx={cx} cy={cy} r="3"><title>{label}</title></circle>{view.chart.pointLabels&&<text className="infer-point-label" x={cx} y={cy-8} textAnchor="middle">{displayNumber(n)}</text>}</g>;})}</g>;})}
 {view.chart.ticks&&xTicks.map(({r,i})=><g key={r.id}><line x1={x(i)} x2={x(i)} y1={plot.bottom} y2={plot.bottom+5} stroke="#8194bd"/><text x={x(i)} y={plot.bottom+26} textAnchor="middle"><title>{rowLabel(r)}</title>{rowLabel(r).length>23?rowLabel(r).slice(0,20)+"…":rowLabel(r)}</text></g>)}
 <text x="715" y={plot.height-10} textAnchor="middle">{view.xLabel}</text><text transform={`translate(17 ${(plot.top+plot.bottom)/2}) rotate(-90)`} textAnchor="middle">表格指标</text></svg></div>}
 </section>;
}
