import type {
  ConfigEdit,
  Selection,
} from "../../infrastructure/contracts/api.generated";
import { request } from "../../infrastructure/http/client";
const url = (p: string, t: string) =>
  "/projects/" + p + "/tasks/" + t + "/rawprep";
export const read = (p: string, t: string) => request(url(p, t));
export const save = (p: string, t: string, v: ConfigEdit & { processed_name?: string }) =>
  request(url(p, t), v, "PUT");
export const check = (p: string, t: string, v: Selection) =>
  request(url(p, t) + "/preflight", v);
export const execute = (p: string, t: string, v: Selection) =>
  request(url(p, t) + "/execute", v);
export const capabilities = () => request("/capabilities");

/** 样本身份来自数据集适配器，文件和样本数量分别显示。 */
export const datasetCatalog=(p:string,t:string,body:unknown)=>request(`/projects/${p}/tasks/${t}/rawprep/catalog`,body);

export const trial=(p:string,t:string,body:unknown)=>request(`/projects/${p}/tasks/${t}/rawprep/trial`,body);

export type DatasetBinding = {
  revision:string; dataset_id:string; label?:string; binding_mode:string; status:'unbound'|'valid'|'invalid';
  sources:Record<string,{root:string;path:string}>; errors:unknown[]; location?:string;
  binding_schema:{mode:string;root_key:string;description:string;slots:{key:string;label:string;kind:string;extensions?:string[]}[]};
};
export type PublicDataset = {
  dataset_id:string; label:string; description:string; binding_mode:string; compatible:boolean;
  instances:{id:string;label:string;sources:DatasetBinding['sources']}[];
};
export type PublicDatasetCatalog = {
  revision:string; current_dataset_id:string; model_id:string; datasets:PublicDataset[];
};
const bindingUrl=(p:string,t:string)=>`/projects/${p}/tasks/${t}/dataset`;
export const readBinding=(p:string,t:string)=>request<DatasetBinding>(bindingUrl(p,t));
export const listPublicDatasets=(p:string,t:string)=>request<PublicDatasetCatalog>(`/projects/${p}/tasks/${t}/datasets`);
export const saveBinding=(p:string,t:string,revision:string,body:{sources?:DatasetBinding['sources'];dataset_id?:string;instance_id?:string})=>request<DatasetBinding>(bindingUrl(p,t),{expected_revision:revision,...body},'PUT');
export const sourceRoots=(p:string,t:string)=>request(`/projects/${p}/files/roots?task_id=${encodeURIComponent(t)}`);
export const sourceFiles=(p:string,t:string,root:string,path:string)=>request(`/projects/${p}/files?`+new URLSearchParams({task_id:t,root,path}));
