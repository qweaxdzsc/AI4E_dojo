import { request } from '../../infrastructure/http/client';
const base = (p:string,t:string) => `/projects/${p}/tasks/${t}`;
/** 阶段配置只保存用户选择。 */
export const readStage=(p:string,t:string,s:string)=>request(base(p,t)+`/configuration?stage=${s}`);
export const saveStage=(p:string,t:string,s:string,revision:string,values:unknown)=>request(base(p,t)+'/configuration',{stage:s,expected_revision:revision,values},'PUT');
export const runStage=async(p:string,t:string,s:string,revision:string,mode:string,selection:any={})=>{const result=await request(base(p,t)+`/stages/${s}/operations`,{expected_revision:revision,mode,selection,inputs:Object.values(selection.bindings||{}),idempotency_key:crypto.randomUUID()});return mode==='check'?await waitOperation(p,result):result;};
export const traceModel=async(p:string,t:string,revision:string,bindings:Record<string,any>={})=>{let value=await request(base(p,t)+'/model-inspections',{expected_revision:revision,mode:'check',selection:{bindings},inputs:Object.values(bindings),idempotency_key:crypto.randomUUID()});while(['queued','running'].includes(value.status)){await new Promise(r=>setTimeout(r,300));value=await request(`/projects/${p}/operations/${value.operation_id}`);}if(value.status!=='succeeded')throw new Error(value.error?.message||value.status);return value;};
export const modelAssetUrl=(p:string,value:any)=>`/api/v1/projects/${p}/assets/${value.result_refs[0].asset_id}/content?member=${encodeURIComponent(value.result.member)}&revision=${value.result_refs[0].revision}`;
export const resumeRun=(p:string,r:string)=>request(`/projects/${p}/runs/${r}/resume`,{});

export const stageInputs=(p:string,t:string)=>request(base(p,t)+"/stage-inputs");

export async function waitOperation(p:string,value:any){while(['queued','running'].includes(value.status)){await new Promise(r=>setTimeout(r,300));value=await request(`/projects/${p}/operations/${value.operation_id}`);}if(value.status!=='succeeded')throw new Error(value.error?.message||value.status);return value.result;}
