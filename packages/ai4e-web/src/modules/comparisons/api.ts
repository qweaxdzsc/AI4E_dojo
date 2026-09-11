import { request } from "../../infrastructure/http/client";
export const compare = (p: string, v: unknown) =>
  request("/projects/" + p + "/compare", v);
export const listSaved=(p:string)=>request(`/projects/${p}/comparisons`);
export const saveComparison=(p:string,v:unknown)=>request(`/projects/${p}/comparisons`,v);
export const registerDifferenceInput=(p:string,root:string,path:string,task_id:string)=>request(`/projects/${p}/assets`,{root,path,task_id});
export const comparisonConfiguration=(p:string,t:string)=>request(`/projects/${p}/tasks/${t}/configuration`);
export const submitDifference=(p:string,id:string,body:unknown)=>request(`/projects/${p}/comparisons/${id}/differences`,body);
export async function waitDifference(p:string,value:any){while(['queued','running'].includes(value.status)){await new Promise(r=>setTimeout(r,300));value=await request(`/projects/${p}/operations/${value.operation_id}`);}if(value.status!=='succeeded')throw new Error(value.error?.message||value.status);return value;}
