import {useEffect,useRef,useState} from 'react';
import {submitMetrics,readMetrics,cancelMetrics,exportMetrics,metricJobs} from './api';
import {finished,type MetricJob} from './model';
/** 评价运行独立于Tab挂载；失败重试沿用原请求身份。 */
export function usePostMetrics(project:string,task:string){
 const [job,setJob]=useState<MetricJob>(),[busy,setBusy]=useState(false),[error,setError]=useState(''),[history,setHistory]=useState<MetricJob[]>([]);
 const live=useRef(true),intent=useRef<{signature:string;key:string}>();
 useEffect(()=>{live.current=true;metricJobs(project,task).then(v=>{if(live.current)setHistory(Array.isArray(v?.items)?v.items:[]);}).catch(e=>live.current&&setError(e.message));return()=>{live.current=false;};},[project,task]);
 useEffect(()=>{if(!job||finished(job.status))return;let active=true;const timer=setInterval(()=>readMetrics(project,task,job.id).then(v=>{if(active){setJob(v);setError('');}}).catch(e=>active&&setError(e.message)),1000);return()=>{active=false;clearInterval(timer);};},[project,task,job?.id,job?.status]);
 async function submit(body:any){setBusy(true);setError('');const signature=JSON.stringify(body);if(intent.current?.signature!==signature)intent.current={signature,key:crypto.randomUUID()};try{const value=await submitMetrics(project,task,{...body,idempotency_key:intent.current.key});if(live.current){setJob(value);setHistory(old=>[...old.filter(j=>j.id!==value.id),value]);intent.current=undefined;}}catch(e){if(live.current)setError((e as Error).message);}finally{if(live.current)setBusy(false);}}
 async function open(id:string){try{const value=await readMetrics(project,task,id);if(live.current)setJob(value);}catch(e){if(live.current)setError((e as Error).message);}}
 async function cancel(){if(job)try{await cancelMetrics(project,task,job.id);}catch(e){setError((e as Error).message);}}
 async function download(format:string,row_ids?:string[]){if(!job)return;setBusy(true);try{return await exportMetrics(project,task,job.id,{format,...(row_ids?{row_ids}:{})});}catch(e){setError((e as Error).message);}finally{if(live.current)setBusy(false);}}
 return {job,busy,error,history,submit,open,cancel,download};
}
