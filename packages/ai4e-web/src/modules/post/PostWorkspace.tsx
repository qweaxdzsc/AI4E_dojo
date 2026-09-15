import type {ReactNode} from 'react';
import {PostResultsWorkspace} from './PostResultsWorkspace';

/** 历史阶段入口保留调用签名，统一进入任务级三个后处理页签。 */
export function PostWorkspace({project,task,run}: {
  project:string; task:string; run?:string; runs?:any[];
  onRun?:(id:string)=>void; values:any; onChange:(key:string,value:any)=>void;
  bindings:ReactNode; onExecute:()=>void; busy:boolean;
}) {
  return <PostResultsWorkspace key={project+':'+task} project={project} task={task} runId={run}/>;
}
