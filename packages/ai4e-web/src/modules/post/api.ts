import { request } from '../../infrastructure/http/client';
export const registerSource=(p:string,t:string,root:string,path:string)=>request(`/projects/${p}/assets`,{root,path,task_id:t});
export const listScenes=(p:string)=>request(`/projects/${p}/scenes`);
export const saveScene=(p:string,scene:any,saved?:any)=>request(`/projects/${p}/scenes${saved?'/'+saved.scene_id:''}`,{scene,...(saved?{expected_revision:saved.revision}:{})},saved?'PUT':'POST');
export const postMetrics=(p:string,run:string)=>request(`/projects/${p}/runs/${run}/metrics`);
