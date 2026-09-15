import {Alert,Input} from 'antd';
import {useEffect,useState} from 'react';
import {ArtifactFileTree,fileDownload,StageFiles} from '../files';
import type {ArtifactTreeFile} from '../files';
import {FilePreviewDialog} from '../previews';
import {DatasetBindingPanel} from './DatasetBindingPanel';
import {list as listFiles} from '../files/api';
import {type DatasetBinding} from './api';

function toInput(row:any,root:string,base:string):ArtifactTreeFile{
 const rel=base&&String(row.path).startsWith(base+'/')?String(row.path).slice(base.length+1):String(row.path||row.name);
 return {...row,id:root+':'+row.path,name:row.name,tree_path:rel,directory:!!row.directory,root,source_path:row.path,path:row.path};
}
function merge(old:ArtifactTreeFile[],next:ArtifactTreeFile[]){
 const seen=new Map(old.map(row=>[row.id,row]));
 for(const row of next)seen.set(row.id,row);
 return [...seen.values()];
}

/** 执行选择被已保存绑定限制；NASA保留跨根稳定引用，绝不自动补齐缺件。 */
export function BoundDatasetFiles({project,task,binding,onBinding,onSelection,disabled=false,beforeSave,run,refresh=0}:{project:string;task:string;binding?:DatasetBinding;onBinding:(binding:DatasetBinding,saved:boolean)=>void;onSelection:(root:string,files:string[])=>void;disabled?:boolean;beforeSave?:()=>Promise<string>;run?:string;refresh?:number}){
 const fileBindings=binding?.binding_mode==='files',base=binding?.sources[binding?.binding_schema?.root_key||'root'],first=base;
 const [view,setView]=useState('inputs');
 const [rows,setRows]=useState<ArtifactTreeFile[]>([]),[selected,setSelected]=useState<string[]>([]),[query,setQuery]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false),[preview,setPreview]=useState<any>(),[generation,setGeneration]=useState(0),[loading,setLoading]=useState<string[]>([]);
 useEffect(()=>{setSelected([]);setRows([]);setQuery('')},[base?.root,base?.path,binding?.status]);
 useEffect(()=>{
  const visible=boundVisible.filter(r=>!r.directory);
  const chosen=visible.filter(r=>selected.includes(r.id));
  onSelection(first?.root||'',(chosen.length?chosen:visible).map(r=>r.source_path||r.path||'').filter(Boolean));
 },[selected,first?.root,rows,binding]);
 useEffect(()=>{let live=true;if(view!=='inputs'||fileBindings||!base||binding?.status!=='valid')return;setBusy(true);listFiles(project,base.root,base.path||'',task,query).then(v=>{if(!live)return;setRows(v.map((row:any)=>toInput(row,base.root,base.path||'')));setError('')}).catch(e=>live&&setError(e.message)).finally(()=>live&&setBusy(false));return()=>{live=false}},[project,task,base?.root,base?.path,generation,fileBindings,binding?.status,view,query,refresh]);
 async function expand(path:string){
  if(!base)return;
  setLoading(old=>[...old,path]);
  try{
   const folder=[base.path,path].filter(Boolean).join('/');
   const value=(await listFiles(project,base.root,folder,task)).map((row:any)=>toInput(row,base.root,base.path||''));
   setRows(old=>merge(old,value));
  }catch(e:any){setError(e.message)}
  finally{setLoading(old=>old.filter(item=>item!==path))}
 }
 const boundFiles:ArtifactTreeFile[]=fileBindings?(binding?.binding_schema.slots.map(s=>s.key)||[]).filter(k=>binding?.sources[k]).map(k=>{const s=binding!.sources[k];const name=s.path.split('/').at(-1)||s.path;return {id:s.root+'::'+s.path,name,tree_path:name,directory:false,root:s.root,source_path:s.path,path:s.path};}):rows;
 const boundVisible=boundFiles;
 return <DatasetBindingPanel project={project} task={task} onBinding={onBinding} disabled={disabled} beforeSave={beforeSave}>{({action,notices,dialogs})=><div className="bound-dataset-files"><div className="data-panel-head"><div className="data-panel-head-main"><div className="dataset-tabs" role="tablist" aria-label="数据视图"><button type="button" role="tab" aria-selected={view==='inputs'} onClick={()=>setView('inputs')}>原始数据处理</button><button type="button" role="tab" aria-selected={view==='artifacts'} onClick={()=>setView('artifacts')}>处理结果</button></div></div><div className="data-panel-head-actions"><button type="button" className="refreshfiles" disabled={busy||(view==='inputs'&&(fileBindings||binding?.status!=='valid'))} onClick={()=>setGeneration(g=>g+1)} aria-label="刷新数据文件">↻ 刷新</button>{action}</div></div>{view==='artifacts'?<div className="data-panel-body artifact-body"><Input.Search className="file-search" aria-label="搜索绑定文件" placeholder="搜索文件名或路径…" value={query} onChange={e=>setQuery(e.target.value)}/>{error&&<Alert type="error" message={error}/>}<StageFiles project={project} task={task} role="inputs" run={run} query={query} compact emptyHint={run?'该来源尚无对应阶段文件':'请选择固定输入或运行'}/></div>:<div className="data-panel-body">{notices}<Input.Search className="file-search" aria-label="搜索绑定文件" placeholder="搜索文件名或路径…" value={query} onChange={e=>setQuery(e.target.value)}/>{binding?.status!=='valid'?null:<><button type="button" className="link" disabled={!query.trim()} onClick={()=>setSelected(old=>Array.from(new Set([...old,...boundFiles.filter(r=>!r.directory).map(r=>r.id)])))}>选择匹配文件</button>{error&&<Alert type="error" message={error}/>}{busy&&!boundFiles.length?null:<ArtifactFileTree files={boundFiles} selected={selected} onSelection={setSelected} selectable={file=>!file.directory} onPreview={row=>setPreview({root:row.root,path:row.source_path||row.path,name:row.name})} onExpand={fileBindings||query?undefined:expand} loadingPaths={loading} download={row=>fileDownload(project,row.root||'',row.source_path||row.path||'',task)}/>}</>}</div>}{dialogs}{preview&&<FilePreviewDialog project={project} task={task} file={preview} onClose={()=>setPreview(undefined)}/>}</div>}</DatasetBindingPanel>;
}
