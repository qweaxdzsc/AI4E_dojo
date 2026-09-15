import {Button,Select} from 'antd';
import {FullscreenOutlined} from '@ant-design/icons';
import {useEffect,useState} from 'react';
import {VtkViewport} from '../../infrastructure/rendering/vtk/Viewport';
import {transform,bufferUrl} from './api';
import type {Source} from './model';
/** 单文件紧凑预览，复用Vis转换与既有视口；不创建主工作台来源。 */
export function PhysicalFilePreview({source}:{source:Source}){
 const [data,setData]=useState<any>(),[error,setError]=useState(''),[field,setField]=useState(''),[component,setComponent]=useState('magnitude'),[command,setCommand]=useState<any>();
 useEffect(()=>{const c=new AbortController();setData(undefined);setError('');setField('');transform(source,[],c.signal).then(setData).catch(e=>{if(!c.signal.aborted)setError(e.message);});return()=>c.abort();},[source.asset_id,source.revision,source.block]);
 if(error)return <div role="alert">{error}</div>;if(!data)return <p role="status">正在读取网格…</p>;
 const active=data.fields?.find((f:any)=>f.field_id===field);
 return <div className="post-compact-mesh"><div className="post-preview-controls"><label>着色物理量<Select aria-label="预览着色物理量" popupMatchSelectWidth={320} getPopupContainer={trigger=>trigger.parentElement!} value={field} onChange={setField} options={[{value:'',label:'纯色'},...(data.fields||[]).map((f:any)=>({value:f.field_id,label:f.name}))]}/></label><Select className="preview-component" aria-label="预览分量" value={component} onChange={setComponent} options={[{value:'magnitude',label:active?.components>1?'模长':'标量'},...Array.from({length:active?.components>1?active.components:0},(_,i)=>({value:String(i),label:String(i)}))]}/><Button aria-label="适合窗口" icon={<FullscreenOutlined/>} onClick={()=>setCommand({kind:'reset',id:Date.now()})}>适合窗口</Button></div><div className="post-preview-canvas"><VtkViewport manifest={data} url={(path:string)=>bufferUrl(source,data.display_ref,path)} field={field} component={component} representation="surface" opacity={1} command={command} onError={(e:Error)=>setError(e.message)}/></div></div>;
}
