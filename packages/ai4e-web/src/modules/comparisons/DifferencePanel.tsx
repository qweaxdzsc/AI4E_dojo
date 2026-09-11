import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import {Alert, Card, Select, Space} from "antd";
import {useCallback,useState} from 'react';
import {FileBrowser} from '../files';
import {VisualizationWorkspace} from '../visualization';
import {registerDifferenceInput,submitDifference,comparisonConfiguration,waitDifference} from './api';
/** 固定运行比较的差值由算法校验身份和单位后生成，前端不插值。 */
export function DifferencePanel({project,saved,runs}:{project:string;saved:any;runs:any[]}){
 const [root,setRoot]=useState(''),[files,setFiles]=useState<string[]>([]),[choice,setChoice]=useState<Record<string,string>>({}),[result,setResult]=useState<any>(),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const task=runs.find(r=>r.id===saved.selection.left)?.task_id;
 const selection=useCallback((root:string,files:string[])=>{setRoot(root);setFiles(files)},[]);
 async function calculate(){setBusy(true);setError('');try{const refs=await Promise.all(['left','left_metadata','right','right_metadata'].map(key=>registerDifferenceInput(project,root,choice[key],task)));const cfg=await comparisonConfiguration(project,task);const operation=await submitDifference(project,saved.comparison_id,{task_id:task,expected_revision:cfg.revision,inputs:[{asset_ref:refs[0],metadata_ref:refs[1]},{asset_ref:refs[2],metadata_ref:refs[3]}],idempotency_key:crypto.randomUUID()});setResult(await waitDifference(project,operation));}catch(e:any){setError(e.message)}finally{setBusy(false)}}
 return <Card title="同身份字段差值"><p>选择两次固定运行的字段与同样本清单。身份、坐标、拓扑、归属和单位全部一致时才计算 A − B。</p><div className="difference-inputs"><FileBrowser project={project} task={task} onSelection={selection}/><div>{[['left','对象 A 字段'],['left_metadata','对象 A 样本 manifest'],['right','对象 B 字段'],['right_metadata','对象 B 样本 manifest']].map(([key,label])=><div key={key}><label>{label}</label><Select style={{width:'100%',marginBottom:12}} value={choice[key]} options={files.map(value=>({value,label:value}))} onChange={value=>setChoice({...choice,[key]:value})}/></div>)}<Button type="primary" loading={busy} disabled={!task||['left','left_metadata','right','right_metadata'].some(key=>!choice[key])} onClick={calculate}>校验并计算差值</Button></div></div>{error&&<Alert type="error" message={error}/>} {result&&<VisualizationWorkspace sources={result.result_refs.slice(0,1)} mode="comparison" onError={e=>setError(e.message)}/>}</Card>
}
