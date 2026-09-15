/** 任务表与工作台共用名称和真实状态，浏览位置不参与判断。 */
export const WORKBENCH_STAGES = ['数据采样','原始处理','数据准备','模型设置','训练设置','训练运行','推理','后处理','报告'] as const;
export const STAGE_SLUGS=['sampling','rawprep','trainprep','model','training','train','infer','post','report'] as const;
const keys=STAGE_SLUGS;
const legacy=['sampling','rawprep','trainprep','model','training','train','post','report'];
/** 旧数字地址保持原阶段含义，新生成地址全部使用稳定标识。 */
export function resolveStage(value:string){return /^\d+$/.test(value)?legacy[Number(value)]||'rawprep':STAGE_SLUGS.find(s=>s===value)||'rawprep';}
const labels:Record<string,string>={not_run:'未运行',unchecked:'未检查',succeeded:'运行成功',running:'运行中',pending:'等待执行',queued:'等待执行',stopping:'正在停止',failed:'失败',stopped:'已停止',canceled:'已取消',interrupted:'已中断',stale:'检查失效',unknown:'无法确认',unavailable:'未开放',available:'有可用结果',partial:'部分交付',capturing:'固定输入'};
/** 只有正式阶段成功或当前修订检查通过才展示成功标识。 */
export function stageDisplay(task:any,index:number){
 if(!task) return {status:'reading',finished:false,active:false,label:'读取中'};
 const check=index===3||index===4;const summary=task?.stage_summary?.stages||task?.stage_summary||{};
 const fact=index===0||index===8?{status:'unavailable'}:summary[keys[index]];
 const status=fact?.status||(check?'unchecked':'not_run');
 return {status,finished:status==='succeeded',active:['running','pending','queued','stopping','capturing'].includes(status),label:check&&status==='succeeded'?'检查通过':labels[status]||'无法确认',reference:fact?.run_id||fact?.operation_id};
}
/** 单次阶段成功不能称全流程完成；保留部分完成与未知历史事实。 */
export function taskDisplay(task:any){
 if(!task) return {kind:'reading',label:'读取中'};
 if(task?.archived)return {kind:'archived',label:'已归档'};
 const stages=[1,2,5,6].map(i=>stageDisplay(task,i));
 if(stages.some(s=>s.active))return {kind:'running',label:'运行中'};
 if(stages.some(s=>s.status==='failed'))return {kind:'failed',label:'运行失败'};
 if(stages.every(s=>s.finished))return {kind:'succeeded',label:'流程已完成'};
 if(stages.some(s=>s.finished))return {kind:'partial',label:'部分阶段完成'};
 if(stages.some(s=>['stopped','canceled','interrupted'].includes(s.status)))return {kind:'stopped',label:'已停止'};
 if(stages.some(s=>s.status==='unknown'))return {kind:'unknown',label:'状态待核对'};
 return {kind:'draft',label:'尚未运行'};
}
