import {Alert,Button,Input,Select,Spin} from 'antd';
import {CloudUploadOutlined, ReloadOutlined, SearchOutlined} from '@ant-design/icons';
import {useEffect,useRef,useState} from 'react';
import {ArtifactFileTree,type ArtifactTreeFile} from '../files';
import {PostFilePreviewPanel} from './PostFilePreviewPanel';
import {resultFiles} from './api';
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

/** 左树右预览，目录筛选与指标和三维场景完全独立。 */
export function PostResultFilesPanel({project,task,catalog,busy,refresh,onAdd,adding,initialBatch,initialRun,initialSample,initialSplit,active}:{project:string;task:string;catalog:ResultCatalog;busy:boolean;refresh:()=>void;onAdd:(files:ArtifactTreeFile[])=>Promise<void>;adding:boolean;initialBatch?:string;initialRun?:string;initialSample?:string;initialSplit?:string;active:boolean}){
 const [batch,setBatch]=useState(initialBatch||''),[query,setQuery]=useState(''),[fixed,setFixed]=useState(!!initialRun||!!initialSample),[status,setStatus]=useState(''),[selected,setSelected]=useState<string[]>([]),[preview,setPreview]=useState<ArtifactTreeFile>(),[width,setWidth]=useState(40);
 const [files,setFiles]=useState<ArtifactTreeFile[]>([]),[searchFiles,setSearchFiles]=useState<ArtifactTreeFile[]|null>(null),[loading,setLoading]=useState<string[]>([]),[treeBusy,setTreeBusy]=useState(false),[opened,setOpened]=useState<string[]>([]),[error,setError]=useState(''),[tick,setTick]=useState(0);
 const container=useRef<HTMLDivElement>(null);
 const filters={batch:batch||undefined,status:status||undefined,run_id:fixed?initialRun:undefined,sample:fixed?initialSample:undefined,split:fixed?initialSplit:undefined};
 useEffect(()=>{if(!active)return;let live=true;setTreeBusy(true);setError('');resultFiles(project,task,{directory:'',...filters,query}).then(value=>{if(!live)return;const rows=(value.files||[]).map(toFile);if(query){setSearchFiles(rows);setOpened(rows.flatMap(f=>ancestors(f.tree_path)));}else{setFiles(rows);setSearchFiles(null);if(fixed&&initialSample)setOpened([...new Set(rows.flatMap(f=>[...ancestors(f.tree_path),...(f.directory?[f.tree_path]:[])]))]);}setSelected(old=>old.filter(id=>rows.some(r=>r.id===id)));}).catch(e=>live&&setError(e.message)).finally(()=>live&&setTreeBusy(false));return()=>{live=false};},[active,project,task,batch,status,query,fixed,initialRun,initialSample,initialSplit,tick]);
 async function expand(path:string){
  setLoading(old=>[...old,path]);
  try{
   const value=await resultFiles(project,task,{directory:path,...filters});
   setFiles(old=>merge(old,value.files.map(toFile)));
  }catch(e:any){setError(e.message)}
  finally{setLoading(old=>old.filter(item=>item!==path))}
 }
 const shown=(searchFiles??files).map(f=>({...f,added:f.added||false}));
 const chosen=shown.filter(f=>selected.includes(f.id)&&f.visualizable&&!f.directory);
 return <div className="post-result-files" ref={container} style={{gridTemplateColumns:`minmax(300px,${width}fr) 8px minmax(320px,${100-width}fr)`}}><section className="post-result-tree"><div className="post-file-filters"><Select aria-label="结果文件批次" value={batch} onChange={setBatch} options={[{value:'',label:'全部批次'},...catalog.batches.map(b=>({value:b.id,label:b.name||b.id.slice(0,12)}))]}/><Select aria-label="结果状态" value={status} onChange={setStatus} options={[{value:'',label:'全部状态'},{value:'succeeded',label:'成功'},{value:'partial',label:'部分完成'},{value:'failed',label:'失败'}]}/><Input prefix={<SearchOutlined/>} allowClear aria-label="搜索结果文件" placeholder="搜索文件名或路径…" value={query} onChange={e=>setQuery(e.target.value)}/></div><header><strong>文件列表</strong><span>共 {shown.filter(f=>!f.directory).length} 个文件</span><div className="post-file-actions"><Button aria-label={`批量加入三维物理场${chosen.length?` (${chosen.length})`:""}`} icon={<CloudUploadOutlined/>} type="primary" disabled={!chosen.length||adding} loading={adding} onClick={()=>void onAdd(chosen)}>批量加入三维物理场{chosen.length?` (${chosen.length})`:''}</Button><Button type="text" size="small" aria-label="刷新结果文件" title="刷新" icon={<ReloadOutlined/>} loading={busy||treeBusy} onClick={()=>{setFiles([]);setTick(n=>n+1);refresh();}}/></div></header>{initialRun&&<small className="post-file-location">固定来源：{initialRun.slice(0,12)}{initialSample&&` · ${initialSample}`} {initialSplit} <Button size="small" onClick={()=>setFixed(!fixed)}>{fixed?"显示此批次全部结果":"定位固定结果"}</Button></small>}{error&&<Alert type="error" message={error}/>}{preview&&!shown.some(f=>f.id===preview.id)&&<Alert type="warning" message="预览来源已变化或失效，请重新选择"/>}<Spin spinning={treeBusy}><ArtifactFileTree files={shown} query={query} selected={selected} onSelection={setSelected} selectedFile={preview?.id} onPreview={setPreview} onVisualize={f=>void onAdd([f])} onExpand={query?undefined:expand} loadingPaths={loading} opened={opened} onOpened={setOpened}/></Spin></section><div className="post-panel-divider" role="separator" aria-label="调整文件与预览宽度" tabIndex={0} onKeyDown={e=>{if(e.key==='ArrowLeft')setWidth(w=>Math.max(25,w-2));if(e.key==='ArrowRight')setWidth(w=>Math.min(65,w+2));}} onPointerDown={e=>e.currentTarget.setPointerCapture(e.pointerId)} onPointerMove={e=>{if(!e.currentTarget.hasPointerCapture(e.pointerId)||!container.current)return;const r=container.current.getBoundingClientRect();setWidth(Math.max(25,Math.min(65,(e.clientX-r.left)/r.width*100)));}}/>{active&&<PostFilePreviewPanel project={project} task={task} file={preview} onClose={()=>setPreview(undefined)}/>}</div>;
}
