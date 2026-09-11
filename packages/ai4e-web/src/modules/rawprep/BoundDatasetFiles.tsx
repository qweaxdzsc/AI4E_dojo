import {Alert,Checkbox,Input,Spin} from 'antd';
import {useEffect,useState} from 'react';
import {FileBrowser} from '../files';
import {FilePreviewDialog} from '../previews';
import {DatasetBindingPanel} from './DatasetBindingPanel';
import {sourceFiles,type DatasetBinding} from './api';

function formatSize(bytes?:number){
 if(typeof bytes!=='number'||!Number.isFinite(bytes))return '—';
 if(bytes<1024)return bytes+' B';
 if(bytes<1048576)return (bytes/1024).toFixed(1)+' KB';
 return (bytes/1048576).toFixed(1)+' MB';
}
function formatTime(value?:string){
 if(!value)return '—';
 const time=new Date(value);
 if(Number.isNaN(time.getTime()))return '—';
 const pad=(n:number)=>String(n).padStart(2,'0');
 return `${time.getFullYear()}-${pad(time.getMonth()+1)}-${pad(time.getDate())} ${pad(time.getHours())}:${pad(time.getMinutes())}`;
}
function fileType(name:string,directory?:boolean){
 if(directory)return 'DIR';
 const ext=name.split('.').pop();
 return ext&&ext!==name?ext.toUpperCase():'—';
}

/** 执行选择被已保存绑定限制；NASA保留跨根稳定引用，绝不自动补齐缺件。 */
export function BoundDatasetFiles({project,task,binding,onBinding,onSelection,disabled=false}:{project:string;task:string;binding?:DatasetBinding;onBinding:(binding:DatasetBinding,saved:boolean)=>void;onSelection:(root:string,files:string[])=>void;disabled?:boolean}){
 const nasa=binding?.dataset_id==='nasa_crm',base=binding?.sources.root,first=nasa?binding?.sources.train_h5:base;
 const [view,setView]=useState('inputs');
 const [path,setPath]=useState(base?.path||''),[rows,setRows]=useState<any[]>([]),[selected,setSelected]=useState<string[]>([]),[query,setQuery]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false),[preview,setPreview]=useState<any>(),[generation,setGeneration]=useState(0);
 useEffect(()=>{setPath(base?.path||'');setSelected([]);setRows([]);setQuery('')},[base?.root,base?.path,binding?.status]);
 useEffect(()=>{onSelection(first?.root||'',selected)},[selected,first?.root]);
 useEffect(()=>{let live=true;if(view!=='inputs'||nasa||!base||binding?.status!=='valid')return;setBusy(true);sourceFiles(project,task,base.root,path).then(v=>{if(live){setRows(v);setError('')}}).catch(e=>live&&setError(e.message)).finally(()=>live&&setBusy(false));return()=>{live=false}},[project,task,base?.root,path,generation,nasa,binding?.status,view]);
 const shown=nasa?['train_h5','test_h5','connectivity_h5'].filter(k=>binding?.sources[k]).map(k=>{const s=binding!.sources[k];return{...s,name:s.path.split('/').at(-1)||s.path,key:s.root+'::'+s.path,directory:false}}):rows.map(r=>({...r,root:base?.root,key:r.path}));
 return <DatasetBindingPanel project={project} task={task} onBinding={onBinding} disabled={disabled}>{({action,notices,dialogs})=><div className="bound-dataset-files"><div className="data-panel-head"><div className="data-panel-head-main"><div className="dataset-tabs" role="tablist" aria-label="数据视图"><button type="button" role="tab" aria-selected={view==='inputs'} onClick={()=>setView('inputs')}>原始数据处理</button><button type="button" role="tab" aria-selected={view==='artifacts'} onClick={()=>setView('artifacts')}>处理结果</button></div>{view==='inputs'&&<span className="selection-label">（已选中文件：<b>{selected.length}</b>）</span>}</div><div className="data-panel-head-actions"><button type="button" className="refreshfiles" disabled={busy||(view==='inputs'&&(nasa||binding?.status!=='valid'))} onClick={()=>setGeneration(g=>g+1)} aria-label="刷新数据文件">↻ 刷新</button>{action}</div></div>{view==='artifacts'?<div className="data-panel-body artifact-body"><FileBrowser key={generation} project={project} task={task} compact/></div>:<div className="data-panel-body"><div className="directory-info"><span>{binding?.status==='valid'?(nasa?'已绑定 NASA 文件':'已绑定目录 / '+(base?.path||'数据根目录')):'尚未选择处理目录'}</span>{notices}</div>{binding?.status!=='valid'?<Alert type="info" message="绑定有效数据来源后选择处理文件"/>:<><Input.Search className="file-search" aria-label="搜索绑定文件" placeholder="搜索文件名或路径…" value={query} onChange={e=>setQuery(e.target.value)}/>{!nasa&&<div className="breadcrumb"><button type="button" className="crumb-up" disabled={path===(base?.path||'')} onClick={()=>setPath(path.split('/').slice(0,-1).join('/'))}>↑ 上级</button><span>{path||'数据根目录'}</span></div>}{error&&<Alert type="error" message={error}/>}{busy?<Spin/>:<div className="tree"><table className="filetable"><thead><tr><th>文件名</th><th>类型</th><th>大小</th><th>修改时间</th><th>操作</th></tr></thead><tbody>{shown.filter(r=>r.name.toLowerCase().includes(query.toLowerCase())).map(r=><tr key={r.key} className={r.directory?'folderrow':'filerow'}><td>{!r.directory&&<Checkbox aria-label={'选择 '+r.name} checked={selected.includes(r.key)} onChange={e=>setSelected(old=>e.target.checked?[...old,r.key]:old.filter(k=>k!==r.key))}/>}<button type="button" className="link" onClick={()=>r.directory?setPath(r.path):setPreview({root:r.root,path:r.path})}>{r.directory?<span className="foldericon"/>:<span className="docicon"/>}{r.name}</button></td><td>{fileType(r.name,r.directory)}</td><td>{formatSize(r.size)}</td><td className="modifiedtime">{formatTime(r.modified_at)}</td><td>{!r.directory&&<button type="button" className="preview-link" aria-label={'预览 '+r.name} onClick={()=>setPreview({root:r.root,path:r.path})}>预览</button>}</td></tr>)}{!shown.filter(r=>r.name.toLowerCase().includes(query.toLowerCase())).length&&<tr><td colSpan={5} className="empty-files">此目录没有内容</td></tr>}</tbody></table></div>}</>}</div>}{dialogs}{preview&&<FilePreviewDialog project={project} task={task} file={preview} onClose={()=>setPreview(undefined)}/>}</div>}</DatasetBindingPanel>;
}
