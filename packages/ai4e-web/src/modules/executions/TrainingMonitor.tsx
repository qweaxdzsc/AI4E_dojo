import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import {Alert, Card, Select, Space, Table} from "antd";
import { useEffect,useState } from 'react';
import { metrics,resume } from './api';
import { ExecutionLog } from './ExecutionLog';
/** 训练监控只绘制产物中存在的有限数值；外壳对照运行细节页，不填演示曲线。 */
export function TrainingMonitor({project,run,runs,onRun,onStart,busy,inputs,onInput}:{project:string;run?:string;runs:any[];onRun:(id:string)=>void;onStart:()=>void;busy:boolean;inputs:any[];onInput:(ref:any)=>void}){
 const [value,setValue]=useState<any>(),[error,setError]=useState('');
 useEffect(()=>{setValue(undefined);if(!run)return;let live=true;const read=()=>metrics(project,run).then(v=>live&&setValue(v)).catch(e=>live&&setError(e.message));void read();const timer=setInterval(read,1500);return()=>{live=false;clearInterval(timer)}},[project,run]);
 const history=(value?.history||[]).filter((row:any)=>typeof row.loss==='number'&&Number.isFinite(row.loss));
 const points=history.map((row:any,i:number)=>`${40+(history.length>1?i/(history.length-1)*760:0)},${230-(row.loss-Math.min(...history.map((h:any)=>h.loss)))/(Math.max(...history.map((h:any)=>h.loss))-Math.min(...history.map((h:any)=>h.loss))||1)*190}`).join(' ');
 const last=history.at(-1),evaluation=last?.evaluation?.metrics||{};
 return <div className="training-monitor">
  <section className="run-summary">
   <div className="run-summary-header"><h2>训练运行监控</h2><span className="run-badge">{value?.status||'尚无运行'}</span></div>
   <Space wrap id="stage-handoff"><Select aria-label="选择运行" style={{width:300}} placeholder="选择运行" value={run} options={runs.map(r=>({value:r.id,label:r.id.slice(0,8)+' · '+r.status}))} onChange={onRun}/><Select aria-label="train.manifest" style={{width:280}} placeholder="选择物理数据清单" options={inputs.filter(i=>i.binding==='train.manifest').map(i=>({value:i.ref.asset_id,label:i.run_id.slice(0,8)+' / '+i.name}))} onChange={id=>onInput(inputs.find(i=>i.ref.asset_id===id).ref)}/><Button type="primary" loading={busy} onClick={onStart}>准备并训练</Button></Space>
   <div className="monitor-kpis run-numbers">{[['当前 epoch',last?.epoch??'尚无记录'],['优化步数',last?.updates??'尚无记录'],['开始时间',value?.created_at?new Date(value.created_at).toLocaleString():'—'],['进程 CPU',value?.resources?value.resources.cpu_percent+'%':'尚无记录'],['进程常驻内存',value?.resources?(value.resources.resident_bytes/1024/1024).toFixed(1)+' MB':'尚无记录']].map(([label,v])=><div key={label} className="run-number"><small>{label}</small><strong>{v}</strong></div>)}</div>
  </section>
  <div className="run-grid monitor-grid">
   <div className="run-left">
    <Card title="Loss 曲线">{history.length?<svg role="img" aria-label="真实训练 Loss 曲线" viewBox="0 0 840 270"><path d="M40 20V230H810" stroke="#cddcf1" fill="none"/><polyline points={points} fill="none" stroke="#1677ff" strokeWidth="2"/><text x="40" y="255" fontSize="12">epoch {history[0].epoch}</text><text x="720" y="255" fontSize="12">epoch {last.epoch}</text></svg>:<div className="empty-record">尚无已记录的训练曲线<br/><small>完成的轮次记录可用后显示真实数据</small></div>}</Card>
    <Card title="评估指标"><Table rowKey="name" pagination={false} dataSource={Object.entries(evaluation).map(([name,v])=>({name,value:typeof v==='object'?(v as any)?.value:v}))} columns={[{title:'指标',dataIndex:'name'},{title:'最新值',dataIndex:'value'}]}/></Card>
   </div>
   <div className="run-right">
    <ExecutionLog project={project} run={run}/>
    <Card title="快捷操作"><Space><Button disabled={!run} onClick={()=>run&&resume(project,run).then(v=>onRun(v.id)).catch(e=>setError(e.message))}>从检查点继续</Button><Button disabled>生成评估报告（未开放）</Button></Space></Card>
   </div>
  </div>
  {error&&<Alert type="error" message={error}/>}
 </div>;
}
