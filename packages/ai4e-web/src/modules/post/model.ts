import type {ArtifactTreeFile} from '../files';
/** 后处理固定结果身份；不包含服务器绝对路径。 */
export interface FieldChoice {id:string;domain:string;field:string;component:string;association:string;label:string;default:boolean;unit?:string}
export interface PostResult {id:string;revision:string;batch_id:string;run_id:string;sample:string;split?:string;checkpoint:any;fields:FieldChoice[];evaluable:boolean;evaluation_error?:string;status:string}
export interface ResultCatalog {items:PostResult[];files:ArtifactTreeFile[];batches:{id:string;name?:string;status:string;created_at?:string}[];errors:any[];total:number}
export interface MetricJob {id:string;run_id:string;status:string;created_at:string;completed:number;total:number;failed:number;rows:any[];row_count:number;request:any;error?:string}
export const finished=(s:string)=>['succeeded','partial','failed','canceled','interrupted'].includes(s);
export const jobLabel=(s:string)=>({pending:'等待计算',running:'计算中',succeeded:'计算完成',partial:'部分完成',failed:'失败',canceled:'已取消',interrupted:'已中断'}[s]||s);
