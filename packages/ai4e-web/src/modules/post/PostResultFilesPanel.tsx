import {Alert,Button,Input,Select,Spin} from 'antd';
import {CloudUploadOutlined, ReloadOutlined, SearchOutlined} from '@ant-design/icons';
import {useEffect,useRef,useState} from 'react';
import {ArtifactFileTree,type ArtifactTreeFile} from '../files';
import {PostFilePreviewPanel} from './PostFilePreviewPanel';
import {inferenceBatchLabel} from '../inference';
import {resultFiles,taskRuns} from './api';
import type {ResultCatalog} from './model';

function toFile(row:any):ArtifactTreeFile{
 return {...row,id:row.id||((row.directory?'dir:':'file:')+row.tree_path),tree_path:row.tree_path||row.path,directory:!!row.directory};
}
function merge(old:ArtifactTreeFile[],next:ArtifactTreeFile[]){
 const seen=new Map(old.map(row=>[row.id,row]));
 for(const row of next)seen.set(row.id,row);
 return [...seen.values()];
}
function ancestors(path:string){
 const parts=path.split('/').filter(Boolean),rows:string[]=[];
 for(let i=0;i<parts.length-1;i++)rows.push(parts.slice(0,i+1).join('/'));
 return rows;
}
function isTrainRun(run:any){
 const stages=new Set(run?.stages||[]);
 const purpose=run?.metadata?.purpose;
 if(purpose==='post_metrics'||purpose==='inference'||stages.has('infer'))return false;
 return stages.has('train');
}
function trainPrefix(run:any){
 return '训练运行 · '+String(run?.id||'').slice(0,8);
}
function trainEmptyName(run?:any){
 if(run?.status==='failed')return '没有预测或网格（开训失败）';
 if(['queued','running','stopping'].includes(run?.status||''))return '训练尚未写出预测或网格';
 return '没有写出预测或网格';
}
function trainFolder(run:any):ArtifactTreeFile{
 const path=trainPrefix(run);
 return {id:'dir:'+path,name:path,tree_path:path,directory:true,batch_id:'train:'+run.id,run_id:run.id,status:run.status,modified_at:run.created_at,kind:'train'};
}
function emptyNote(run:any):ArtifactTreeFile{
 const name=trainEmptyName(run);
 const path=trainPrefix(run)+'/'+name;
 return {id:'dir:'+path,name,tree_path:path,directory:true,batch_id:'train:'+run.id,run_id:run.id,status:run.status,empty:true,kind:'train'};
}
function datasetPrefix(name:string){
 return '平台数据集 · '+name;
}
function mergeDatasetFolders(rows:ArtifactTreeFile[],datasets:any[],filters:{batch?:string;query?:string}){
 const extra:ArtifactTreeFile[]=[];
 for(const item of datasets){
  const name=String(item?.name||'').trim();
  if(!name||item?.status&&item.status!=='available')continue;
  const path=datasetPrefix(name);
  const id='dataset:'+name;
  if(filters.batch&&filters.batch!==id)continue;
  const q=(filters.query||'').toLowerCase();
  if(q&&!path.toLowerCase().includes(q)&&!name.toLowerCase().includes(q))continue;
  if(rows.some(r=>r.tree_path===path||r.batch_id===id))continue;
  extra.push({id:'dir:'+path,name:path,tree_path:path,directory:true,batch_id:id,kind:'dataset',status:'succeeded'});
 }
 return [...extra,...rows];
}
function mergeTrainFolders(rows:ArtifactTreeFile[],runs:any[],filters:{batch?:string;status?:string;run_id?:string;query?:string}){
 const extra:ArtifactTreeFile[]=[];
 for(const run of runs){
  if(!isTrainRun(run))continue;
  if(filters.status&&run.status!==filters.status)continue;
  if(filters.run_id&&run.id!==filters.run_id)continue;
  if(filters.batch&&filters.batch!==('train:'+run.id))continue;
  const path=trainPrefix(run);
  const q=(filters.query||'').toLowerCase();
  if(q&&!path.toLowerCase().includes(q)&&!String(run.id).toLowerCase().includes(q))continue;
  if(rows.some(r=>r.run_id===run.id||r.tree_path===path))continue;
  extra.push(trainFolder(run));
 }
 return [...extra,...rows];
}

/** 左树右预览；训练 run 即使没有写出预测/网格也保留文件夹。目录筛选与指标和三维场景完全独立。 */
export function PostResultFilesPanel({project,task,catalog,busy,refresh,onAdd,adding,initialBatch,initialRun,initialSample,initialSplit,active}:{project:string;task:string;catalog:ResultCatalog;busy:boolean;refresh:()=>void;onAdd:(files:ArtifactTreeFile[])=>Promise<void>;adding:boolean;initialBatch?:string;initialRun?:string;initialSample?:string;initialSplit?:string;active:boolean}){
 const [batch,setBatch]=useState(initialBatch||''),[query,setQuery]=useState(''),[fixed,setFixed]=useState(!!initialRun||!!initialSample),[status,setStatus]=useState(''),[selected,setSelected]=useState<string[]>([]),[preview,setPreview]=useState<ArtifactTreeFile>(),[width,setWidth]=useState(40);
 const [files,setFiles]=useState<ArtifactTreeFile[]>([]),[searchFiles,setSearchFiles]=useState<ArtifactTreeFile[]|null>(null),[loading,setLoading]=useState<string[]>([]),[treeBusy,setTreeBusy]=useState(false),[opened,setOpened]=useState<string[]>([]),[error,setError]=useState(''),[tick,setTick]=useState(0),[trains,setTrains]=useState<any[]>([]),[datasets,setDatasets]=useState<any[]>([]);
 const container=useRef<HTMLDivElement>(null);
 const trainsRef=useRef<any[]>([]);
 const filters={batch:batch||undefined,status:status||undefined,run_id:fixed?initialRun:undefined,sample:fixed?initialSample:undefined,split:fixed?initialSplit:undefined};
 useEffect(()=>{if(!active)return;let live=true;setTreeBusy(true);setError('');Promise.all([resultFiles(project,task,{directory:'',...filters,query}),taskRuns(project,task).catch(()=>[])]).then(([value,runs])=>{if(!live)return;const list=Array.isArray(runs)?runs:[];const datasetRows=(Array.isArray(value.files)?value.files:[]).filter((item:any)=>item?.directory&&item?.kind==='dataset');const mine=datasetRows.map((item:any)=>({name:String(item.tree_path||item.name||'').replace(/^平台数据集 · /,''),status:'available',origin_task:task}));trainsRef.current=list;setTrains(list);setDatasets(mine);const rows:ArtifactTreeFile[]=mergeDatasetFolders(mergeTrainFolders((value.files||[]).map(toFile),list,{...filters,query}),mine,{...filters,query});if(query){setSearchFiles(rows);setOpened(rows.flatMap(f=>ancestors(f.tree_path)));}else{setFiles(rows);setSearchFiles(null);if(fixed&&initialSample)setOpened([...new Set(rows.flatMap(f=>[...ancestors(f.tree_path),...(f.directory?[f.tree_path]:[])]))]);}setSelected(old=>old.filter(id=>rows.some(r=>r.id===id)));}).catch(e=>live&&setError(e.message)).finally(()=>live&&setTreeBusy(false));return()=>{live=false};},[active,project,task,batch,status,query,fixed,initialRun,initialSample,initialSplit,tick]);
 async function expand(path:string){
  setLoading(old=>[...old,path]);
  try{
   const value=await resultFiles(project,task,{directory:path,...filters});
   let next=(value.files||[]).map(toFile);
   if(!next.length&&path.startsWith('训练运行 ·')){
    const run=trainsRef.current.find(r=>trainPrefix(r)===path)||{id:path.replace(/^训练运行 · /,''),status:'succeeded'};
    next=[emptyNote(run)];
   }
   if(!next.length&&path.startsWith('平台数据集 ·')){
    next=[{id:'dir:'+path+'/没有可对照的样本',name:'没有可对照的样本',tree_path:path+'/没有可对照的样本',directory:true,empty:true,kind:'dataset'}];
   }
   setFiles(old=>merge(old,next));
  }catch(e:any){setError(e.message)}
  finally{setLoading(old=>old.filter(item=>item!==path))}
 }
 const shown=(searchFiles??files).map(f=>({...f,added:f.added||false}));
 const chosen=shown.filter(f=>selected.includes(f.id)&&f.visualizable&&!f.directory);
 const batchOptions=[{value:'',label:'全部批次'}];
 const seen=new Set<string>();
 for(const item of catalog.batches){batchOptions.push({value:item.id,label:inferenceBatchLabel(item)});seen.add(item.id);}
 for(const run of trains.filter(isTrainRun)){const id='train:'+run.id;if(seen.has(id))continue;batchOptions.push({value:id,label:trainPrefix(run)});seen.add(id);}
 for(const item of datasets){const name=String(item?.name||'').trim();if(!name)continue;const id='dataset:'+name;if(seen.has(id))continue;batchOptions.push({value:id,label:datasetPrefix(name)});seen.add(id);}
 const folders=shown.filter(f=>f.directory).length,fileCount=shown.filter(f=>!f.directory).length;
 return <div className="post-result-files" ref={container} style={{gridTemplateColumns:`minmax(300px,${width}fr) 8px minmax(320px,${100-width}fr)`}}><section className="post-result-tree"><div className="post-file-filters"><Select aria-label="结果文件批次" value={batch} onChange={setBatch} options={batchOptions}/><Select aria-label="结果状态" value={status} onChange={setStatus} options={[{value:'',label:'全部状态'},{value:'succeeded',label:'成功'},{value:'partial',label:'部分完成'},{value:'stopped',label:'已停止'},{value:'failed',label:'失败'}]}/><Input prefix={<SearchOutlined/>} allowClear aria-label="搜索结果文件" placeholder="搜索文件名或路径…" value={query} onChange={e=>setQuery(e.target.value)}/></div><header><strong>文件列表</strong><span>共 {folders+fileCount} 项 · {folders} 个文件夹 · {fileCount} 个文件</span><div className="post-file-actions"><Button aria-label={`批量加入三维物理场${chosen.length?` (${chosen.length})`:""}`} icon={<CloudUploadOutlined/>} type="primary" disabled={!chosen.length||adding} loading={adding} onClick={()=>void onAdd(chosen)}>批量加入三维物理场{chosen.length?` (${chosen.length})`:''}</Button><Button type="text" size="small" aria-label="刷新结果文件" title="刷新" icon={<ReloadOutlined/>} loading={busy||treeBusy} onClick={()=>{setFiles([]);setTick(n=>n+1);refresh();}}/></div></header>{initialRun&&<small className="post-file-location">固定来源：{initialRun.slice(0,12)}{initialSample&&` · ${initialSample}`} {initialSplit} <Button size="small" onClick={()=>setFixed(!fixed)}>{fixed?"显示此批次全部结果":"定位固定结果"}</Button></small>}{error&&<Alert type="error" message={error}/>}{preview&&!shown.some(f=>f.id===preview.id)&&<Alert type="warning" message="预览来源已变化或失效，请重新选择"/>}<Spin spinning={treeBusy}><ArtifactFileTree files={shown} query={query} selected={selected} onSelection={setSelected} selectedFile={preview?.id} onPreview={setPreview} onVisualize={f=>void onAdd([f])} onExpand={query?undefined:expand} loadingPaths={loading} opened={opened} onOpened={setOpened} emptyDescription={query?"没有符合条件的结果文件":"暂无训练运行、平台数据集或推理固定结果"}/></Spin></section><div className="post-panel-divider" role="separator" aria-label="调整文件与预览宽度" tabIndex={0} onKeyDown={e=>{if(e.key==='ArrowLeft')setWidth(w=>Math.max(25,w-2));if(e.key==='ArrowRight')setWidth(w=>Math.min(65,w+2));}} onPointerDown={e=>e.currentTarget.setPointerCapture(e.pointerId)} onPointerMove={e=>{if(!e.currentTarget.hasPointerCapture(e.pointerId)||!container.current)return;const r=container.current.getBoundingClientRect();setWidth(Math.max(25,Math.min(65,(e.clientX-r.left)/r.width*100)));}}/>{active&&<PostFilePreviewPanel project={project} task={task} file={preview} onClose={()=>setPreview(undefined)}/>}</div>;
}
