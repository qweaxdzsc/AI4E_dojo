import { request } from "../../infrastructure/http/client";
export const list = (p: string) => request("/projects/" + p + "/lineage");
export const details=(p:string,id:string)=>request(`/projects/${p}/lineage/${id}`);
