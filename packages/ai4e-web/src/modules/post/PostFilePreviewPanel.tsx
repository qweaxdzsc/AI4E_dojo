import {Button,Empty,Tooltip} from 'antd';
import {CloseOutlined,DownloadOutlined,ExpandOutlined,CompressOutlined,FileSearchOutlined} from '@ant-design/icons';
import {useEffect,useState} from 'react';
import {fileDownload,registerFile,type ArtifactTreeFile} from '../files';
import {FilePreviewContent} from '../previews';
/** 预览标题、视口和底部交付工具分区；放大和关闭保持选择与主会话。 */
export function PostFilePreviewPanel({file,project,task,onClose}:{file?:ArtifactTreeFile;project:string;task:string;onClose:()=>void}){
 const [expanded,setExpanded]=useState(false),[asset,setAsset]=useState<any>(),[error,setError]=useState('');
 useEffect(()=>{let live=true;setAsset(undefined);setError('');if(!file||file.directory)return;if(file.ref?.asset_id){setAsset(file.ref);return;}
  const path=file.source_path||file.path;if(!file.root||!path){setError('缺少受控文件路径');return;}
  registerFile(project,file.root,path,task).then(v=>live&&setAsset(v)).catch(e=>live&&setError(e.message));
  return()=>{live=false};
 },[project,task,file?.id,file?.root,file?.source_path,file?.path,file?.ref?.asset_id]);
 const href=file&&(file.root&&(file.source_path||file.path)?fileDownload(project,file.root,file.source_path||file.path||'',task):file.ref?`/api/v1/projects/${project}/assets/${file.ref.asset_id}/content?revision=${file.ref.revision}&download=true`:'');
 return <section className={'post-file-preview'+(expanded?' maximized':'')} aria-label="文件预览">
  <header><strong>文件预览</strong><span className="post-preview-filename" title={file?.tree_path}>{file?.name||''}</span><Tooltip title={expanded?'还原预览':'放大预览'}><Button type="text" aria-label="放大文件预览" icon={expanded?<CompressOutlined/>:<ExpandOutlined/>} onClick={()=>setExpanded(v=>!v)}/></Tooltip><Button type="text" aria-label="关闭文件预览" icon={<CloseOutlined/>} onClick={()=>{setExpanded(false);onClose();}}/></header>
  <div className="post-preview-body">{error?<div role="alert">{error}</div>:file?(/\.(png|jpe?g|webp|gif)$/i.test(file.name)&&href?<img src={href} alt={file.name}/>:asset?<FilePreviewContent key={file.id} asset={asset} scope={{project_id:project,task_id:task}} compact/>:<p role="status">读取文件…</p>):<Empty image={<FileSearchOutlined style={{fontSize:45,color:'#a7bee0'}}/>} description="选择左侧文件进行预览"/>}</div>
  <footer>{file?<><span>{file.name.split(".").pop()?.toUpperCase()}{file.size!=null&&` · ${(file.size/1024).toFixed(1)} KB`}</span><Button icon={<ExpandOutlined/>} onClick={()=>setExpanded(v=>!v)}>{expanded?'还原':'放大'}</Button><Button icon={<DownloadOutlined/>} href={href} download={file.name}>下载文件</Button></>:<span>网格、数组、文本和图片均可在此查看</span>}</footer>
 </section>;
}
