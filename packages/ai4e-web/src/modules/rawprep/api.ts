import type {
  ConfigEdit,
  Selection,
} from "../../infrastructure/contracts/api.generated";
import { request } from "../../infrastructure/http/client";
import { invalidateStageInputs, stageInputs } from "../stages";
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

const catalogLoads = new Map<
  string,
  { value?: any; pending?: Promise<any>; at?: number }
>();
const CATALOG_TTL_MS = 10_000;
function catalogKey(p: string, t: string, body: unknown) {
  return `${p}:${t}:${JSON.stringify(body)}`;
}
/** 样本身份来自数据集适配器；同任务在途目录合并，短时复用，避免进页重复拉起检查进程。 */
export const datasetCatalog = (p: string, t: string, body: unknown) => {
  const key = catalogKey(p, t, body);
  const current = catalogLoads.get(key);
  if (
    current?.value &&
    current.at &&
    Date.now() - current.at < CATALOG_TTL_MS
  )
    return Promise.resolve(current.value);
  if (current?.pending) return current.pending;
  const pending = request(`/projects/${p}/tasks/${t}/rawprep/catalog`, body)
    .then((value) => {
      catalogLoads.set(key, { value, at: Date.now() });
      return value;
    })
    .catch((error) => {
      catalogLoads.delete(key);
      throw error;
    });
  catalogLoads.set(key, { pending });
  return pending;
};
/** 保存、换绑或正式执行后丢掉短时目录缓存。 */
export const invalidateDatasetCatalog = (p: string, t: string) => {
  for (const key of [...catalogLoads.keys()])
    if (key.startsWith(`${p}:${t}:`)) catalogLoads.delete(key);
};

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
/** 处理结果页选用已登记平台数据集；复用阶段工作台的在途合并与短时缓存。 */
export const listProcessedInputs = stageInputs;
export { invalidateStageInputs };
