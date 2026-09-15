import {Alert, Button, Empty, Modal, Spin} from 'antd';
import {type ReactNode,useEffect,useState} from 'react';
import {ActionButton} from '../../infrastructure/components/ActionButton';
import {listPublicDatasets,readBinding,saveBinding,type DatasetBinding,type PublicDataset,type PublicDatasetCatalog} from './api';
import './dataset-binding.css';

/** 绑定只选 contrib 公开数据集及其本机完整副本，不手填路径。 */
export function DatasetBindingPanel({project,task,onBinding,disabled=false,beforeSave,children}:{project:string;task:string;onBinding:(binding:DatasetBinding,saved:boolean)=>void;disabled?:boolean;beforeSave?:()=>Promise<string>;children?:(ui:{action:ReactNode;notices:ReactNode;dialogs:ReactNode})=>ReactNode}){
 const [value,setValue]=useState<DatasetBinding>(),[catalog,setCatalog]=useState<PublicDatasetCatalog>(),[datasetId,setDatasetId]=useState(''),[instanceId,setInstanceId]=useState(''),[open,setOpen]=useState(false),[busy,setBusy]=useState(false),[error,setError]=useState('');
 useEffect(()=>{let live=true;readBinding(project,task).then(v=>{if(!live)return;setValue(v);onBinding(v,false)}).catch(e=>live&&setError(e.message));return()=>{live=false}},[project,task]);
 async function edit(){setError('');setBusy(true);try{const [v,list]=await Promise.all([readBinding(project,task),listPublicDatasets(project,task)]);setValue(v);setCatalog(list);const current=list.datasets.find(d=>d.dataset_id===(v.dataset_id||list.current_dataset_id));setDatasetId(current?.dataset_id||'');setInstanceId(current?.instances[0]?.id||'');onBinding(v,false);setOpen(true)}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 async function save(){if(!value||busy||!datasetId||!instanceId)return;setBusy(true);setError('');try{const revision=beforeSave?await beforeSave():value.revision;const v=await saveBinding(project,task,revision,{dataset_id:datasetId,instance_id:instanceId});setValue(v);setOpen(false);onBinding(v,true)}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 const selected=catalog?.datasets.find(d=>d.dataset_id===datasetId);
 const instance=selected?.instances.find(i=>i.id===instanceId);
 const action=<ActionButton className="addfile" aria-label="配置数据来源" disabled={disabled} loading={busy} onClick={edit}>{value?.status==='unbound'?'绑定数据':'修改绑定'}</ActionButton>;
 const notices=<>{value?.status==='invalid'&&<Alert type="warning" message="来源失效，请重新选择" description={value.errors.map(e=>typeof e==='string'?e:JSON.stringify(e)).join('；')}/>}{error&&<Alert type="error" message={error}/>}{disabled&&<small>当前操作进行中，请稍候。</small>}</>;
 const dialogs=<Modal open={open} title="选择公开数据集" onCancel={()=>!busy&&setOpen(false)} footer={<><Button disabled={busy} onClick={()=>setOpen(false)}>取消</Button><ActionButton type="primary" loading={busy} disabled={!selected?.compatible||!instance} onClick={save}>保存数据绑定</ActionButton></>} width={680}><p>名单来自 contrib 公开数据集；选中后接入该集处理方式与平台已登记的本机地址。</p>{error&&<Alert type="error" message={error}/>}{!catalog?<Spin/>:<div className="public-datasets">{catalog.datasets.map(dataset=><DatasetChoice key={dataset.dataset_id} dataset={dataset} selected={datasetId===dataset.dataset_id} instanceId={datasetId===dataset.dataset_id?instanceId:''} onSelect={(id,copy)=>{setDatasetId(id);setInstanceId(copy)}}/>)}</div>}</Modal>;
 if(children)return <>{children({action,notices,dialogs})}</>;
 return <div className="dataset-binding-panel"><div className="panel-title"><b>数据来源</b>{action}</div>{notices}{dialogs}</div>;
}

function DatasetChoice({dataset,selected,instanceId,onSelect}:{dataset:PublicDataset;selected:boolean;instanceId:string;onSelect:(datasetId:string,instanceId:string)=>void}){
 const available=dataset.compatible&&dataset.instances.length>0;
 return <div className={'public-dataset'+(selected?' selected':'')+(available?'':' disabled')}>
  <button type="button" className="public-dataset-pick" disabled={!available} aria-pressed={selected} onClick={()=>onSelect(dataset.dataset_id,dataset.instances[0]?.id||'')}>
   <b>{dataset.label}</b>
   <small>处理方式：{dataset.description}</small>
   {!dataset.compatible&&<small>当前模型没有对应登记案例</small>}
   {dataset.compatible&&!dataset.instances.length&&<small>本机未找到完整副本</small>}
  </button>
  {selected&&dataset.instances.length>1&&<div className="public-dataset-copies">{dataset.instances.map(item=><label key={item.id}><input type="radio" name={'copy-'+dataset.dataset_id} checked={instanceId===item.id} onChange={()=>onSelect(dataset.dataset_id,item.id)}/>{item.label}</label>)}</div>}
  {selected&&dataset.instances.length===1&&<small className="public-dataset-location">本机地址：{dataset.instances[0].label}</small>}
 </div>;
}
