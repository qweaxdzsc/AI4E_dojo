import { query, request } from "../../infrastructure/http/client";
const url = (p: string) => "/projects/" + p + "/runs";
export const list = (p: string, t?: string) =>
  request(url(p) + query({ task_id: t }));
export const get = (p: string, r: string) => request(url(p) + "/" + r);
export const stop = (p: string, r: string) =>
  request(url(p) + "/" + r + "/stop", {});
export const subscribe = (p: string, r: string) =>
  new EventSource("/api/v1" + url(p) + "/" + r + "/events");

export const metrics=(p:string,r:string)=>request(url(p)+'/'+r+'/metrics');
export const resume=(p:string,r:string)=>request(url(p)+'/'+r+'/resume',{});

/** 下载读取完整受控日志，不使用前端筛选后的片段。 */
export const readLog=(p:string,r:string)=>request(url(p)+'/'+r+'/log');
