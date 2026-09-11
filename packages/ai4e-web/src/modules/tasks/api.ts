import { request } from "../../infrastructure/http/client";
const url = (p: string) => "/projects/" + p + "/tasks";
export const list = (p: string) => request(url(p));
export const save = (p: string, v: unknown, id?: string) =>
  request(url(p) + (id ? "/" + id : ""), v, id ? "PATCH" : "POST");
export const fork = (p: string, t: string, name: string) =>
  request(url(p) + "/" + t + "/fork", { name });
export const detail = (p: string, t: string) => request(url(p) + "/" + t);
export const cases=(p:string)=>request(url(p)+'/cases');
export const configuration=(p:string,t:string)=>request(url(p)+"/"+t+"/configuration");
