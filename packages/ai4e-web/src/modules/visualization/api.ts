import type {Source} from './model';
import {request} from '../../infrastructure/http/client';
/** 调用平台辅助操作，不创建独立服务或训练任务。 */
async function operation(source:Source,kind:string,options:any,signal:AbortSignal){
 if(signal.aborted)throw new DOMException('Canceled','AbortError');
 const base=`/api/v1/projects/${source.project_id}`;
 // 提交必须收取回执：中断传输会丢掉已创建的订阅身份，收到后再释放本订阅。
 const response=await fetch(`${base}/${kind==='transform'?'visualization':'previews'}/operations`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({source,operation:kind,options})});
 if(!response.ok)throw new Error(await response.text());let record=await response.json();
 const id=record.operation_id,subscriptionId=record.subscription_id;
 // 捕获本次 POST 的订阅，不能从共享 GET 快照猜测其他消费者身份。
 let released=false;const cancel=()=>{if(released)return;released=true;void fetch(`${base}/operations/${id}/cancel`,{method:'POST',...(subscriptionId?{headers:{'Content-Type':'application/json'},body:JSON.stringify({subscription_id:subscriptionId})}:{})}).catch(()=>{});};
 signal.addEventListener('abort',cancel,{once:true});
 try{
  if(signal.aborted){cancel();throw new DOMException('Canceled','AbortError');}
  while(['queued','running'].includes(record.status)){
   await new Promise<void>((resolve,reject)=>{const timer=setTimeout(done,250);function done(){signal.removeEventListener('abort',abort);resolve();}function abort(){clearTimeout(timer);signal.removeEventListener('abort',abort);reject(new DOMException('Canceled','AbortError'));}signal.addEventListener('abort',abort,{once:true});if(signal.aborted)abort();});
   const response=await fetch(`${base}/operations/${id}`,{signal});if(!response.ok)throw new Error(await response.text());record=await response.json();
  }
  if(record.status!=='succeeded')throw new Error(record.error?.message||record.status);
  return record;
 }finally{signal.removeEventListener('abort',cancel);}
}
export async function transform(source:Source,pipeline:any[],signal:AbortSignal){const record=await operation(source,'transform',{pipeline,block:source.block},signal);const display_ref=record.result_refs?.[0];if(!display_ref?.revision)throw new Error('显示资产缺少固定内容修订');return {...record.result,asset_id:display_ref.asset_id,display_ref};}
export function bufferUrl(source:Source,asset:Source,path:string){if(!asset?.revision)throw new Error('显示资产缺少固定内容修订');return `/api/v1/projects/${source.project_id}/assets/${asset.asset_id}/content?member=${encodeURIComponent(path)}&revision=${encodeURIComponent(asset.revision)}`;}
export function previewOptions(source:Source,options:any){return {...options,field:options.field??source.member};}
/** 读取有限预览数据，不在组件中拼接服务路径。 */
export async function inspectAsset(source:Source,kind:string,options:any,signal:AbortSignal){return (await operation(source,kind,previewOptions(source,options),signal)).result;}

/** 宿主只传固定来源和项目任务身份，不提供任意输出路径。 */
const physicalRequest = (path:string, body?:unknown, method?:string) => request(path,body,method);
/** 查询当前项目可用任务作为明确保存目标。 */
export const physicalTargets=(project:string)=>physicalRequest(`/projects/${project}/tasks`);
/** 按目标任务列出配置资产。 */
export const savedVisualizations=(project:string,task:string)=>physicalRequest(`/projects/${project}/tasks/${task}/visualizations`);
/** 创建或重新打开独立工作区。 */
export const openPhysicalWorkspace=(project:string,task:string,body:unknown)=>physicalRequest(`/projects/${project}/tasks/${task}/visualizations/sessions`,body);
/** 有界释放页面所属会话。 */
export const closePhysicalWorkspace=(project:string,task:string,session:string)=>physicalRequest(`/projects/${project}/tasks/${task}/visualizations/sessions/${session}`,undefined,'DELETE').catch(()=>{});

/** 当前项目受控结果列表。 */
export const physicalSources=(project:string,task?:string,root?:string,path?:string)=>{
 if(task){
  const query=new URLSearchParams();
  if(root)query.set('root',root);
  if(path)query.set('path',path);
  const suffix=query.toString();
  return physicalRequest(`/projects/${project}/tasks/${task}/visualizations/sources${suffix?`?${suffix}`:''}`);
 }
 return physicalRequest(`/projects/${project}/assets`);
};
/** 把受控路径登记为固定资产，追加前仍走修订核验。 */
export const registerPhysicalSource=(project:string,body:unknown)=>physicalRequest(`/projects/${project}/assets`,body);
/** 现有工作区追加结果，不创建任务版本。 */
export const appendPhysicalSources=(project:string,task:string,session:string,sources:unknown[])=>physicalRequest(`/projects/${project}/tasks/${task}/visualizations/sessions/${session}/sources`,{sources});
