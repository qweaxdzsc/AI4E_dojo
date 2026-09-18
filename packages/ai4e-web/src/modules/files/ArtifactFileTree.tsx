import {Checkbox, Empty, Spin} from 'antd';
import {CaretDownOutlined, CaretRightOutlined, EyeOutlined, FileTextOutlined, FileImageOutlined, FileOutlined, FolderFilled, DeploymentUnitOutlined} from '@ant-design/icons';
import {useMemo, useState} from 'react';
import {artifactTree, loadedDirectories, selectableFiles, type ArtifactNode, type ArtifactTreeFile} from './artifactTree';
import './artifact-file-tree.css';

/** 原始处理与后处理共用树表；默认收起，点开再取下一层。emptyDescription 只改空态说明。 */
export function ArtifactFileTree({files,query='',selected=[],onSelection,onPreview,onVisualize,selectedFile,download,onExpand,loadingPaths=[],opened:openedProp,onOpened,selectable,emptyDescription}:{files:ArtifactTreeFile[];query?:string;selected?:string[];onSelection?:(ids:string[])=>void;onPreview:(file:ArtifactTreeFile)=>void;onVisualize?:(file:ArtifactTreeFile)=>void;selectedFile?:string;download?:(file:ArtifactTreeFile)=>string;onExpand?:(path:string)=>void|Promise<void>;loadingPaths?:string[];opened?:string[];onOpened?:(paths:string[])=>void;selectable?:(file:ArtifactTreeFile)=>boolean;emptyDescription?:string}) {
 const tree=useMemo(()=>artifactTree(files,query),[files,query]);
 const loaded=useMemo(()=>new Set(loadedDirectories(files)),[files]);
 const [localOpen,setLocalOpen]=useState<string[]>([]);
 const opened=openedProp??localOpen;
 const setOpened=onOpened??setLocalOpen;
 const accept=selectable||((file:ArtifactTreeFile)=>!!file.visualizable&&!file.directory);
 const leavesOf=(node:ArtifactNode)=>selectableFiles(node,accept);
 const toggle=(node:ArtifactNode,checked:boolean)=>{const ids=leavesOf(node).map(f=>f.id);onSelection?.(checked?Array.from(new Set([...selected,...ids])):selected.filter(id=>!ids.includes(id)));};
 const choices=tree.flatMap(leavesOf).map(f=>f.id),count=choices.filter(id=>selected.includes(id)).length;
 async function open(node:ArtifactNode){
  const next=opened.includes(node.path)?opened.filter(k=>k!==node.path):[...opened,node.path];
  setOpened(next);
  if(!opened.includes(node.path)&&onExpand&&!loaded.has(node.path)&&!query)await onExpand(node.path);
 }
 const render=(nodes:ArtifactNode[],depth=0):any=>nodes.flatMap(node=>{
  const f=node.file,leaves=leavesOf(node).map(v=>v.id),checked=leaves.filter(id=>selected.includes(id)).length;
  const expanded=!!query||opened.includes(node.path);
  const extension=f?.name.split('.').pop()?.toUpperCase()||'';
  const Icon=!f||f.directory?FolderFilled:f.visualizable?DeploymentUnitOutlined:/PNG|JPG|JPEG|GIF|WEBP/.test(extension)?FileImageOutlined:/JSON|TXT|LOG|CSV/.test(extension)?FileTextOutlined:FileOutlined;
  const folder=!f||!!f.directory;
  return [<tr key={node.key} className={(folder?'folderrow':'filerow')+(!folder&&selectedFile===f?.id?' selected':'')}>
   {onSelection&&<td className="artifact-select"><Checkbox aria-label={'选择 '+node.name} disabled={!leaves.length} checked={!!leaves.length&&checked===leaves.length} indeterminate={checked>0&&checked<leaves.length} onChange={e=>toggle(node,e.target.checked)}/></td>}
   <td className="artifact-name-cell"><button type="button" className="artifact-name" aria-label={node.name} style={{paddingLeft:depth*12}} title={node.path||node.name} aria-expanded={folder?expanded:undefined} onMouseDown={e=>{if(folder)e.preventDefault();}} onClick={()=>folder?void open(node):onPreview(f!)}>
    <span className="artifact-chevron">{folder&&(expanded?<CaretDownOutlined/>:<CaretRightOutlined/>)}</span><Icon className={folder?`artifact-folder ${depth===0?'root-folder':''}`:`artifact-file-icon ${f?.visualizable?'mesh-file':''}`}/><span>{node.name}</span>{loadingPaths.includes(node.path)&&<Spin size="small"/>}
   </button></td>
   <td className="artifact-type">{folder?'—':extension}</td>
   <td className="artifact-size">{folder||f?.size==null?'—':f.size<1024?f.size+' B':f.size<1048576?(f.size/1024).toFixed(1)+' KB':(f.size/1048576).toFixed(1)+' MB'}</td>
   <td className="artifact-modified" title={f?.modified_at?new Date(f.modified_at).toLocaleString('zh-CN',{hour12:false}):undefined}>{!f?.modified_at?'—':new Date(f.modified_at).toLocaleString('zh-CN',{hour12:false})}</td>
   <td className="artifact-operation">{!folder&&f&&<span className="artifact-actions"><button type="button" aria-label={'预览 '+f.name} onClick={()=>onPreview(f)}><EyeOutlined/>预览</button>{onVisualize&&<button type="button" disabled={!f.visualizable} title={!f.visualizable?'此文件没有明确的三维几何声明':f.added?'已加入工作台，可切换查看':undefined} onClick={()=>onVisualize(f)}>可视化</button>}{f.added&&<small>已加入</small>}{download&&<a href={download(f)} download={f.name}>下载</a>}</span>}</td>
  </tr>,...(folder&&expanded?render(node.children||[],depth+1):[])];
 });
 return <div className="artifact-tree-scroll"><table className="artifact-file-table"><thead><tr>{onSelection&&<th className="artifact-select"><Checkbox aria-label="选择全部可视化文件" disabled={!choices.length} checked={!!choices.length&&count===choices.length} indeterminate={count>0&&count<choices.length} onChange={e=>onSelection?.(e.target.checked?Array.from(new Set([...selected,...choices])):selected.filter(id=>!choices.includes(id)))}/></th>}<th className="artifact-name-cell">文件名</th><th className="artifact-type">类型</th><th className="artifact-size">大小</th><th className="artifact-modified">修改时间</th><th className="artifact-operation">操作</th></tr></thead><tbody>{render(tree)}</tbody></table>{!tree.length&&<Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={emptyDescription||"没有符合条件的结果文件"}/>}</div>;
}
