import {Alert} from 'antd';
import {useEffect,useRef,useState} from 'react';
import {PhysFieldEmbed,type PhysicalWorkspaceHandle} from '../visualization';
import {registerFile,type ArtifactTreeFile} from '../files';
import {PostResultFilesPanel} from './PostResultFilesPanel';
import {usePostResults} from './usePostResults';
import './post.css';

const TABS=[{id:'files',label:'结果文件'},{id:'visualization',label:'三维物理场可视化'}] as const;
type PostTab=(typeof TABS)[number]['id'];
/** 只认现行两个页签；旧 `tab=metrics` 或未知值落到结果文件，避免空页。 */
function resolveTab(value?:string):PostTab{
 return TABS.some(item=>item.id===value)?value as PostTab:'files';
}
/** 任务级后处理组合，Tab切换只改变可见性，绝不关闭主三维会话。指标表在推理页，此处不再设页签。 */
export function PostResultsWorkspace({project,task,batchId,runId,sample,split,tab:initialTab}:{project:string;task:string;batchId?:string;runId?:string;sample?:string;split?:string;resultIndex?:number;tab?:string}){
 const start=resolveTab(initialTab),[tab,setTab]=useState<PostTab>(start),[opened,setOpened]=useState(start==='visualization'),[adding,setAdding]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[added,setAdded]=useState<string[]>([]);
 const data=usePostResults(project,task),workspace=useRef<PhysicalWorkspaceHandle>(null),pending=useRef<ArtifactTreeFile[]>(),live=useRef(true);
 useEffect(()=>{live.current=true;return()=>{live.current=false;};},[]);
 useEffect(()=>{if(!opened||!pending.current||!workspace.current)return;const files=pending.current;pending.current=undefined;void complete(files);},[opened]);
 async function complete(files:ArtifactTreeFile[]){try{const refs=await Promise.all(files.map(async f=>{if(f.ref?.asset_id)return {...f.ref,name:f.name};const ref=await registerFile(project,f.root||'project',f.source_path||f.path||'',task);return {...ref,name:f.name};}));const result=await workspace.current!.append(refs);if(live.current){setTab('visualization');setError('');setAdded(old=>Array.from(new Set([...old,...files.map(f=>f.id)])));setNotice(result.status==='already_added'?'选中的结果已在工作台中':`已加入 ${files.length} 个结果文件`);}}catch(e){if(live.current)setError((e as Error).message);}finally{if(live.current)setAdding(false);}}
 async function add(files:ArtifactTreeFile[]){if(adding)return;setAdding(true);if(!opened){pending.current=files;setOpened(true);}else await complete(files);}
 return <div className="post-three-tabs"><nav role="tablist" aria-label="后处理视图">{TABS.map(item=><button type="button" key={item.id} role="tab" id={'post-tab-'+item.id} aria-controls={'post-panel-'+item.id} aria-selected={tab===item.id} onClick={()=>{setTab(item.id);if(item.id==='visualization')setOpened(true);}}>{item.label}</button>)}</nav>{(error||data.error)&&<Alert type="error" message={error||data.error} showIcon/>}{notice&&<Alert type="success" message={notice} closable onClose={()=>setNotice('')}/>}{data.catalog.errors.length>0&&<Alert type="warning" message={`${data.catalog.errors.length} 个结果分支无法读取，其他结果仍可使用`} description={data.catalog.errors.map(e=>e.error).join('；')}/>}
 <section role="tabpanel" id="post-panel-files" aria-labelledby="post-tab-files" hidden={tab!=='files'}><PostResultFilesPanel project={project} task={task} catalog={{...data.catalog,files:data.catalog.files.map(f=>({...f,added:added.includes(f.id)}))}} busy={data.busy} refresh={data.refresh} onAdd={add} adding={adding} initialBatch={batchId} initialRun={runId} initialSample={sample} initialSplit={split} active={tab==='files'}/></section>
 <section role="tabpanel" id="post-panel-visualization" aria-labelledby="post-tab-visualization" hidden={tab!=='visualization'}>{opened&&<PhysFieldEmbed ref={workspace} sources={[]} scope={{project_id:project,task_id:task}} mode="post" active={tab==='visualization'} onError={e=>setError(e.message)}/>}</section>
 </div>;
}
