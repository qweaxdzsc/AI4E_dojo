/** 独立与宿主共用物理工作台，React 仅承载任务与资产表单。 */
import {useEffect,useRef,useState} from 'react';
import {useLocation} from 'react-router-dom';
import {Alert,Button,Modal,Select,Space} from 'antd';
import {SaveVisualizationDialog,ExportStatus} from '../../visIO/index.js';
import {apiArtifacts,apiUpload} from '../../dataAssets/index.js';
import {listenToFrame,respondToFrame} from '../../../infrastructure/embed/communicator.js';
import {usePhysField} from '../hooks/usePhysField.js';
import {physApi,viewUrl} from '../api.js';
import {AnimationExportDialog} from '../components/AnimationExportDialog.jsx';
import {ConfigurationDialog} from '../components/ConfigurationDialog.jsx';
import {ResultImportDialog} from '../components/ResultImportDialog.jsx';
import {recordingController} from '../recording.js';
import './PhysFieldWorkspacePage.css';

/** 页面负责组合；物理对象工具、属性和视图全部由 Trame 提供。 */
export default function PhysFieldWorkspacePage() {
 const location=useLocation(),params=new URLSearchParams(location.search),model=usePhysField(params);
 const frame=useRef(null),recorder=useRef(null),recordingAsset=useRef(null),requests=useRef(new Map());
 const [saving,setSaving]=useState(false),[recording,setRecording]=useState(false),[dialog,setDialog]=useState(''),[snapshot,setSnapshot]=useState(null),[activeView,setActiveView]=useState(0),[items,setItems]=useState([]),[renderer,setRenderer]=useState('local');
 const [dismissedExport,setDismissedExport]=useState(null);
 const host=params.get('host')==='dojo';
 const toggleRecording=recordingController({frame,recorder,recordingAsset,model,setRecording});
 const hostCall=(type,body={})=>new Promise((resolve,reject)=>{
   const request_id=crypto.randomUUID();const timer=setTimeout(()=>{requests.current.delete(request_id);reject(new Error('宿主请求超时'));},90000);
   requests.current.set(request_id,{resolve,reject,timer});window.parent.postMessage({type,request_id,...body},window.location.origin);
 });
 useEffect(()=>{
   const receive=event=>{if(event.origin!==window.location.origin||event.source!==window.parent||event.data?.type!=='ai4e-vis:host-response')return;
     const pending=requests.current.get(event.data.request_id);if(!pending)return;clearTimeout(pending.timer);requests.current.delete(event.data.request_id);event.data.error?pending.reject(new Error(event.data.error)):pending.resolve(event.data.result);
   };
   window.addEventListener('message',receive);return()=>{window.removeEventListener('message',receive);for(const p of requests.current.values()){clearTimeout(p.timer);p.reject(new Error('工作区已关闭'));}requests.current.clear();};
 },[]);
 useEffect(()=>{
   if(!model.session)return;
   const receive=event=>{
     if(event.origin!==window.location.origin||event.source!==window.parent||event.data?.type!=='ai4e-vis:visibility'||typeof event.data.request_id!=='string'||typeof event.data.visible!=='boolean')return;
     model.visibility(event.data.visible).catch(model.fail);
     frame.current?.contentWindow?.postMessage(event.data,window.location.origin);
   };
   window.addEventListener('message',receive);
   window.parent.postMessage({type:'ai4e-vis:ready'},window.location.origin);
   return()=>window.removeEventListener('message',receive);
 },[model.context,model.session?.session_id]);
 useEffect(()=>listenToFrame(frame,async message=>{
   try {
     const action=message.type.replace('ai4e-vis:','');setActiveView(message.payload?.view??0);
     if(action==='save')setSaving(true);
     else if(action==='record')await toggleRecording();
     else if(action==='import'){const sources=host?await hostCall('ai4e-vis:source-list'):(await apiArtifacts()).items;setItems(sources.map(x=>({...x,id:x.id||x.asset_id||x.artifact_id})));setDialog('import');}
     else {if(['export','export_csv','animation'].includes(action))setSnapshot(await model.snapshot());setDialog(action);}
     respondToFrame(frame,message.request_id,{status:'accepted'});
   }catch(e){model.fail(e);respondToFrame(frame,message.request_id,{status:'failed',error:e.message});}
 }),[model.session,model.asset,model.context,recording]);
 useEffect(()=>()=>{if(recorder.current?.state==='recording')recorder.current.stop();},[]);
 if(!model.context)return <Alert type="info" message="请从项目任务打开，或通过独立启动配置提供保存目标和数据来源。"/>;
 return <section className="phys-workspace-shell">
   {!model.session&&<Space style={{padding:16}}><Select aria-label="渲染方式" value={renderer} onChange={setRenderer} options={[{value:'local',label:'本地渲染'},{value:'remote',label:'远程渲染'}]}/><Button type="primary" loading={model.busy} onClick={()=>model.open(undefined,renderer)}>新建工作区</Button><Select showSearch optionFilterProp="label" aria-label="已保存可视化" placeholder="重新打开" style={{width:240}} options={model.assets.map(a=>({value:a.visualization_id,label:`${a.name} · r${a.revision}`}))} onChange={id=>model.open(id)}/></Space>}
   {model.error&&<Alert closable type="error" message={model.error}/>}
   {recording&&<Alert message="正在录制实际操作" action={<Button onClick={toggleRecording}>停止录制</Button>}/>}
   <div className="phys-output-toast" hidden={!model.output || dismissedExport===model.output?.export_id}><button className="phys-output-dismiss" aria-label="关闭导出提示" onClick={()=>setDismissedExport(model.output?.export_id)}>×</button><ExportStatus output={model.output} onCancel={model.cancel} fileUrl={name=>physApi.download(model.context,model.output.visualization_id,model.output.export_id,name)}/></div>
   {model.session&&<iframe ref={frame} title="三维物理场 Trame 工作台" src={viewUrl(model.context,model.session.session_id,model.session.secret)} style={{border:0,width:'100%',flex:1,minHeight:0,height:'100%',display:'block'}}/>}
   <SaveVisualizationDialog open={saving} target={model.target} initialName={model.asset?.name} onCancel={()=>setSaving(false)} onSave={async name=>{if(await model.save(name))setSaving(false);}}/>
   <AnimationExportDialog open={['animation','export','export_csv'].includes(dialog)} animation={dialog==='animation'} formatHint={dialog==='export_csv'?'csv':'png'} times={snapshot?.times||[]} views={snapshot?.spec?.views||[]} activeView={activeView} onCancel={()=>setDialog('')} onExport={async options=>{if(await model.needsSave()){setDialog('');setSaving(true);return;}await model.export(options);setDialog('');}}/>
   <ConfigurationDialog open={dialog==='configuration'} onCancel={()=>setDialog('')} onApply={async spec=>{await model.apply(spec);setDialog('');}}/>
   <ResultImportDialog open={dialog==='import'} items={items} onUpload={host?undefined:async file=>{try{const result=await apiUpload(file);const item=result.artifact||result;const value={...item,id:item.artifact_id||item.id};setItems(old=>[...old.filter(x=>x.id!==value.id),value]);return value;}catch(e){model.fail(e);return null;}}} onCancel={()=>setDialog('')} onImport={async(id,member)=>{try{const item=items.find(x=>x.id===id);if(host)await hostCall('ai4e-vis:source-append',{sources:[{ref:{...item,...(member?{member}:{}),asset_id:item.asset_id||id}}]});else await physApi.append(model.context,model.session.session_id,id,member);setDialog('');}catch(e){model.fail(e);}}}/>
   <Modal open={dialog==='open'} title="打开已保存配置" onCancel={()=>setDialog('')} footer={null} destroyOnHidden maskClosable><Select showSearch optionFilterProp="label" aria-label="打开配置资产" style={{width:'100%'}} options={model.assets.map(a=>({value:a.visualization_id,label:`${a.name} · r${a.revision}`}))} onChange={async id=>{if(host)await hostCall('ai4e-vis:session-open',{visualization_id:id});else await model.open(id);setDialog('');}}/></Modal>
 </section>;
}
