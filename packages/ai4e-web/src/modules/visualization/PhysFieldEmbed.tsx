/** 独立Vis宿主：任务身份决定生命周期，来源追加与会话创建分开。 */
import {forwardRef,useEffect,useImperativeHandle,useRef,useState} from 'react';
import {Alert,Button,Select,Space} from 'antd';
import {openPhysicalWorkspace,closePhysicalWorkspace,physicalTargets,savedVisualizations,physicalSources,appendPhysicalSources} from './api';
import type {Source} from './model';
import './physical-workspace.css';

export interface PhysicalWorkspaceHandle {append:(sources:Source[])=>Promise<any>}
const identity=(s:Source)=>JSON.stringify([s.project_id,s.asset_id,s.revision,s.member??null,s.block??null]);
/** iframe始终绑定同一会话；只有显式重开或离开任务时释放。 */
export const PhysFieldEmbed=forwardRef<PhysicalWorkspaceHandle,{sources:Source[];scope?:{project_id?:string;task_id?:string};mode?:string;active?:boolean;onError?:(e:Error)=>void}>(function PhysFieldEmbed({sources,scope,mode,active=true,onError},ref){
 const project=scope?.project_id||sources[0]?.project_id;
 const [task,setTask]=useState(scope?.task_id||sources[0]?.task_id||''),[targets,setTargets]=useState<any[]>([]),[saved,setSaved]=useState<any[]>([]),[session,setSession]=useState<any>(),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const frame=useRef<HTMLIFrameElement>(null),current=useRef<any>(),opening=useRef<Promise<any>>(),generation=useRef(0),known=useRef(new Set<string>()),latest=useRef({sources,onError,active});latest.current={sources,onError,active};
 const explain=(e:Error)=>{const raw=e.message||String(e);return raw.includes('phys_session_capacity')?new Error('三维工作区并发会话已满。请关闭其他预览窗口后重试。'):e;};
 const fail=(e:Error)=>{const err=explain(e);setError(err.message);latest.current.onError?.(err);};
 const notify=()=>frame.current?.contentWindow?.postMessage({type:'ai4e-vis:visibility',request_id:crypto.randomUUID(),visible:latest.current.active},window.location.origin);
 const acquire=(id?:string)=>openPhysicalWorkspace(project,task,id?{visualization_id:id}:{sources:latest.current.sources});
 const open=(id?:string):Promise<any>=>{
  if(!id&&current.current)return Promise.resolve(current.current);
  if(opening.current)return opening.current;
  if(!project||!task)return Promise.reject(new Error('缺少项目和目标任务'));
  const version=++generation.current;setBusy(true);setError('');
  const pending=(async()=>{
   const previous=current.current;current.current=undefined;
   if(previous){setSession(undefined);await closePhysicalWorkspace(previous.project,previous.task,previous.session_id);}
   if(version!==generation.current)throw new Error('工作区已关闭');
   let result;
   try{result=await acquire(id);}
   catch(e){
    if(version!==generation.current||!String((e as Error).message).includes('phys_session_capacity'))throw e;
    await new Promise(resolve=>setTimeout(resolve,500));
    if(version!==generation.current)throw e;
    result=await acquire(id);
   }
   if(version!==generation.current){await closePhysicalWorkspace(project,task,result.session_id);throw new Error('工作区已关闭');}
   current.current={...result,project,task};known.current=new Set(id?[]:latest.current.sources.map(identity));setSession(result);
   return current.current;
  })();opening.current=pending;
  void pending.finally(()=>{if(opening.current===pending)opening.current=undefined;if(version===generation.current)setBusy(false);}).catch(()=>{});
  return pending;
 };
 const append=async(values:Source[])=>{const target=await open();const fresh=values.filter(s=>!known.current.has(identity(s)));if(!fresh.length)return {status:'already_added'};setBusy(true);try{const result=await appendPhysicalSources(target.project,target.task,target.session_id,fresh.map(ref=>({ref,name:ref.name})));if(current.current!==target)throw new Error('追加来源时工作区已关闭');fresh.forEach(s=>known.current.add(identity(s)));setError('');return result;}catch(e){fail(e as Error);throw e;}finally{if(current.current===target)setBusy(false);}};
 useImperativeHandle(ref,()=>({append}),[project,task]);
 useEffect(()=>{let live=true;if(project&&!scope?.task_id)physicalTargets(project).then(v=>live&&setTargets(v)).catch(e=>live&&fail(e));return()=>{live=false;};},[project,scope?.task_id]);
 useEffect(()=>{let live=true;if(project&&task)savedVisualizations(project,task).then(v=>live&&setSaved(v.items.filter((i:any)=>i.kind==='phys_field'))).catch(e=>live&&fail(e));return()=>{live=false;};},[project,task,session]);
 useEffect(()=>{const timer=setTimeout(()=>{if(project&&task)void open().catch(fail);},0);return()=>{clearTimeout(timer);generation.current++;opening.current=undefined;const value=current.current;current.current=undefined;known.current.clear();if(value)void closePhysicalWorkspace(value.project,value.task,value.session_id);};},[project,task]);
 useEffect(()=>{notify();},[active,session]);
 useEffect(()=>{const receive=async(event:MessageEvent)=>{
  if(event.origin!==window.location.origin||event.source!==frame.current?.contentWindow)return;
  const m=event.data,target=current.current;
  if(m?.type==='ai4e-vis:ready'){notify();return;}
  if(!target||!['ai4e-vis:source-list','ai4e-vis:source-append','ai4e-vis:session-open'].includes(m?.type)||typeof m.request_id!=='string')return;
  try{let result;if(m.type==='ai4e-vis:session-open'){if(typeof m.visualization_id!=='string')throw new Error('缺少配置资产身份');result=await open(m.visualization_id);}else if(m.type==='ai4e-vis:source-list')result=await physicalSources(target.project);else result=await appendPhysicalSources(target.project,target.task,target.session_id,m.sources);
   frame.current?.contentWindow?.postMessage({type:'ai4e-vis:host-response',request_id:m.request_id,result},window.location.origin);
  }catch(e){frame.current?.contentWindow?.postMessage({type:'ai4e-vis:host-response',request_id:m.request_id,error:(e as Error).message},window.location.origin);}
 };window.addEventListener('message',receive);return()=>window.removeEventListener('message',receive);},[project,task]);
 return <section className={'phys-host'+(mode==='preview'?' preview':'')} aria-label="三维物理场工作台" data-session-id={session?.session_id}>
 {mode!=='preview'&&<div className="phys-host-context"><Space wrap>{!scope?.task_id&&<><span>保存到任务</span><Select aria-label="可视化目标任务" value={task||undefined} style={{width:200}} options={targets.filter(t=>!t.archived).map(t=>({value:t.id,label:t.name||t.id}))} onChange={setTask}/></>}<Select aria-label="重新打开可视化" placeholder="打开已保存配置" style={{width:240}} options={saved.map(a=>({value:a.visualization_id,label:`${a.name} · r${a.revision}`}))} disabled={busy||!task} onChange={id=>void open(id).catch(fail)}/>{busy&&<span role="status">正在连接或加载三维结果…</span>}</Space></div>}
 {error&&<Alert type="error" message={error} action={<Button disabled={busy||!task} onClick={()=>void open().catch(fail)}>重试连接</Button>}/>}
 {!project&&<Alert type="warning" message="缺少项目上下文，请从任务或文件进入。"/>}
 {session&&<iframe key={session.session_id} ref={frame} title="独立可视化应用" src={session.embed_url} className="phys-host-frame" onLoad={notify}/>}
 </section>;
});
