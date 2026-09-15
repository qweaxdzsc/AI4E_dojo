import { query, request } from '../../infrastructure/http/client';
export const registerSource=(p:string,t:string,root:string,path:string)=>request(`/projects/${p}/assets`,{root,path,task_id:t});
export const listScenes=(p:string)=>request(`/projects/${p}/scenes`);
export const saveScene=(p:string,scene:any,saved?:any)=>request(`/projects/${p}/scenes${saved?'/'+saved.scene_id:''}`,{scene,...(saved?{expected_revision:saved.revision}:{})},saved?'PUT':'POST');
export const postMetrics=(p:string,run:string)=>request(`/projects/${p}/runs/${run}/metrics`);
/** 任务目录与评价接口集中于本领域，不在组件中拼接地址。 */
const postBase=(p:string,t:string)=>`/projects/${p}/tasks/${t}/post`;
export const resultCatalog=(p:string,t:string)=>request(postBase(p,t)+'/results'+query({view:'catalog'}));
export const resultFiles=(p:string,t:string,params:{directory?:string;query?:string;batch?:string;run_id?:string;sample?:string;split?:string;status?:string}={})=>request(postBase(p,t)+'/results'+query({view:'files',...params}));
export const metricCatalog=(p:string,t:string)=>request(postBase(p,t)+'/metrics/catalog');
export const submitMetrics=(p:string,t:string,body:unknown)=>request(postBase(p,t)+'/metric-jobs',body);
export const metricJobs=(p:string,t:string)=>request(postBase(p,t)+'/metric-jobs');
export async function readMetrics(p:string,t:string,id:string){const path=postBase(p,t)+'/metric-jobs/'+id;const first=await request(path+'?limit=1000');const rows=[...first.rows];for(let offset=1000;offset<first.row_count;offset+=1000){const page=await request(path+`?offset=${offset}&limit=1000`);rows.push(...page.rows);}return {...first,rows};}
export const cancelMetrics=(p:string,t:string,id:string)=>request(postBase(p,t)+`/metric-jobs/${id}/cancel`,{});
export const exportMetrics=(p:string,t:string,id:string,body:unknown)=>request(postBase(p,t)+`/metric-jobs/${id}/exports`,body);
