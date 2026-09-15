import { query, request } from "../../infrastructure/http/client";
const url = (p: string) => "/projects/" + p + "/files";
export const roots = (p: string, t?: string) =>
  request(url(p) + "/roots" + query({ task_id: t }));
export const list = (p: string, root: string, path: string, t?: string, q?: string) =>
  request(url(p) + query({ root, path, task_id: t, query: q || undefined }));
export const download = (p: string, root: string, path: string, t?: string) =>
  "/api/v1" + url(p) + "/download" + query({ root, path, task_id: t });
/** 只读取选定来源对应的当前层阶段资产。 */
export const stageFiles=(p:string,t:string,role:string,run?:string,asset?:any,path='',q='')=>request(`/projects/${p}/tasks/${t}/stage-files`+query({role,run_id:asset?undefined:run,asset_id:asset?.asset_id,revision:asset?.revision,path:path||undefined,query:q||undefined}));
export const assetDownload=(p:string,ref:any)=>`/api/v1/projects/${p}/assets/${ref.asset_id}/content`+query({revision:ref.revision,member:ref.member,download:"true"});
export const fileDownload=(p:string,root:string,path:string,t?:string)=>download(p,root,path,t);
export const registerFile=(p:string,root:string,path:string,t?:string)=>request(`/projects/${p}/assets`,{root,path,task_id:t});
