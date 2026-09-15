import { Alert, Button, Input, Modal, Select, Dropdown, Pagination, Empty } from "antd";
import { useState, useEffect, Fragment } from "react";
import { Link, useNavigate } from "react-router-dom";
import { fork, save, cases } from "./api";
import { WORKBENCH_STAGES, STAGE_SLUGS, stageDisplay, taskDisplay } from "./stages";
import { ActionButton } from "../../infrastructure/components/ActionButton";
import "./task-management.css";

const DATASETS: Record<string, string> = { shapenet_car: "ShapeNet-Car", nasa_crm: "NASA CRM" };
const MODELS: Record<string, string> = { abupt: "AB-UPT", transolver3: "Transolver-3" };
/** 选项只消费接口字段，不解析案例显示名。 */
function caseLabel(item: { dataset_id?: string; model_id?: string; variant?: string | null }) {
  const model = MODELS[item.model_id || ""] || item.model_id;
  const dataset = DATASETS[item.dataset_id || ""] || item.dataset_id;
  const suffix = item.variant === "surface" ? " 表面" : item.variant === "volume" ? " 体场" : "";
  return `${model} · ${dataset}${suffix}`;
}

/** new/fork 创建版本；编辑与归档不创建版本。 */
export function TaskManagement({
  project,
  rows,
  reload,
  runs, initialQuery="", loading=false,
}: {
  project: string;
  rows: any[];
  reload: () => void;
  runs: any[]; initialQuery?: string; loading?: boolean;
}) {
  const nav=useNavigate();
  const [choices,setChoices]=useState<any[]>([]),[saving,setSaving]=useState(false),[formError,setFormError]=useState("");
  const [caseError,setCaseError]=useState(""),[caseBusy,setCaseBusy]=useState(false);
  function loadCases(){
    setCaseBusy(true);setCaseError("");
    cases(project).then(setChoices).catch(e=>setCaseError(e.message)).finally(()=>setCaseBusy(false));
  }
  useEffect(()=>{loadCases()},[project]);
  const [edit, setEdit] = useState<any>(),
    [q, setQ] = useState(initialQuery),
    [filter, setFilter] = useState("all_active"),
    [error, setError] = useState("");
  const [sort,setSort]=useState("updated"),[page,setPage]=useState(1);
  useEffect(()=>{setQ(initialQuery);setPage(1)},[initialQuery]);
  useEffect(()=>setPage(1),[q,filter,sort]);
  const stepNames=WORKBENCH_STAGES;
  const short=(v:any)=>v?String(v).slice(0,8):"—";
  const date=(v:any)=>v?new Date(v).toLocaleDateString("zh-CN"):"—";
  const runKind=(task:any)=>taskDisplay(task).kind;
  const visible=rows.filter(t=>(t.name+" "+t.version_id+" "+(t.created_by||"")).includes(q)&&(filter==="all"||(filter==="all_active"?runKind(t)!=="archived":runKind(t)===filter))).sort((a,b)=>sort==="created"?String(a.created_at).localeCompare(String(b.created_at)):String(b.updated_at||b.created_at).localeCompare(String(a.updated_at||a.created_at)));
  const creating=!edit?.id;
  const caseReady=!caseError&&choices.length>0;
  async function archive(id:string,archived:boolean){try{await save(project,{archived},id);reload()}catch(e:any){setError(e.message)}}
  function openCreate(){setFormError("");setEdit({name:""})}
  async function persist(){
    if(saving)return;
    if(!edit?.name?.trim()){setFormError("请填写任务名称");return}
    if(creating&&!choices.some(c=>c.id===edit.case_id)){setFormError("请选择科研案例");return}
    setSaving(true);setFormError("");
    try{
      const result=edit.fork?await fork(project,edit.id,edit.name.trim()):await save(project,{name:edit.name.trim(),description:edit.description||"",...(!edit.id?{case_id:edit.case_id}:{})},edit.id);
      const enter=!edit.id||edit.fork;setEdit(undefined);reload();setError("");
      if(enter)nav(`/projects/${project}/tasks/${result.id}/rawprep`);
    }catch(e:any){setFormError(e.message)}finally{setSaving(false)}
  }
  return (
    <section className="task-management">
      <div className="tasktoolbar">
        <Input.Search aria-label="搜索任务" placeholder="⌕　搜索任务 / 版本 / 操作人" value={q} onChange={e=>setQ(e.target.value)}/><div className="toolbar-spacer"/>
        <Select virtual={false} aria-label="任务状态" value={filter} onChange={setFilter} options={[{value:"all_active",label:"全部状态"},{value:"succeeded",label:"流程已完成"},{value:"partial",label:"部分阶段完成"},{value:"stopped",label:"已停止"},{value:"running",label:"运行中"},{value:"draft",label:"草稿"},{value:"failed",label:"运行失败"},{value:"archived",label:"已归档"}]}/>
        <Select virtual={false} aria-label="任务排序" value={sort} onChange={setSort} options={[{value:"updated",label:"更新时间 ↓"},{value:"created",label:"创建时间 ↑"}]}/>
        <Button type="primary" onClick={openCreate}>新建任务</Button>
      </div>
      {error&&<Alert type="error" message={error}/>}
      <div className="taskpanel"><div className="tasktable-scroll"><table className="tasktable"><thead><tr><th>任务名称</th><th>版本</th><th>来源</th><th>基线版本</th><th>操作人</th><th>创建时间 / 更新时间</th><th>操作</th></tr></thead><tbody>
      {visible.slice((page-1)*10,page*10).map(t=>{
       const {kind,label:status}=taskDisplay(t);
       return <Fragment key={t.id}><tr><td><Link className="task-name" to={`/projects/${project}/tasks/${t.id}/rawprep`}>{t.name}</Link><span className={"statuspill "+(kind==="succeeded"?"success":kind==="running"?"running":kind==="failed"?"failed":"draft")}>{status}</span></td><td title={t.version_id}>{short(t.version_id)}</td><td title={t.parent_version_id||t.source_version_id}>{short(t.parent_version_id||t.source_version_id)}</td><td title={t.baseline_version_id}>{short(t.baseline_version_id)}</td><td>{t.created_by||"未记录"}</td><td><small>{date(t.created_at)} / {date(t.updated_at||t.created_at)}</small></td><td><div className="task-row-actions"><Link className="enter-workbench" to={`/projects/${project}/tasks/${t.id}/rawprep`}>进入工作台</Link><Link className="enter-workbench" to={`/projects/${project}/lineage?version=${t.version_id}`}>血缘</Link><Dropdown trigger={["click"]} menu={{items:[{key:"edit",label:"编辑任务"},{key:"fork",label:"派生任务",disabled:t.archived},{key:"archive",label:t.archived?"恢复任务":"归档任务"}],onClick:({key})=>{setFormError("");if(key==="edit")setEdit(t);else if(key==="fork")setEdit({...t,name:t.name+" 派生",fork:true});else void archive(t.id,!t.archived)}}}><Button className="task-more" aria-label={t.name+" 更多操作"}>更多 ⋯</Button></Dropdown></div></td></tr><tr><td colSpan={7} className="progresscell"><div className="ministeps">{stepNames.map((name,i)=>{const {finished,active,label}=stageDisplay(t,i);return <Link key={name} className={(finished?"done ":"")+(active?"current":"")} to={`/projects/${project}/tasks/${t.id}/${STAGE_SLUGS[i]}`} title={label} aria-label={t.name+" · "+name+" · "+label}><span>{finished?"✓":i+1}</span>{name}</Link>})}</div></td></tr></Fragment>
      })}</tbody></table></div>{!loading&&!visible.length&&<Empty description="当前项目尚无符合条件的任务"><Button type="primary" onClick={openCreate}>创建第一个任务</Button></Empty>}<div className="tasktable-foot"><p>来源是直接父版本；基线版本是研究比较基准。修改方案通过派生形成新任务，编辑与运行不增加版本。</p><Pagination size="small" current={page} pageSize={10} total={visible.length} onChange={setPage} showSizeChanger={false}/></div></div>
      <Modal classNames={{wrapper:"task-form-dialog"}} width={520} open={!!edit} title={edit?.fork?"派生任务":edit?.id?"编辑任务":"新建任务"} onCancel={()=>!saving&&setEdit(undefined)} destroyOnClose footer={<><Button autoInsertSpace={false} disabled={saving} onClick={()=>setEdit(undefined)}>取消</Button><ActionButton type="primary" loading={saving} disabled={creating&&!caseReady} onClick={persist}>{edit?.fork?"派生并进入原始处理":edit?.id?"保存":"创建并进入原始处理"}</ActionButton></>}>
        <div className="task-form">
          {formError&&<Alert type="error" message={formError}/>}
          <div className="task-form-item"><label htmlFor="task-name-input">任务名称</label><Input id="task-name-input" aria-label="任务名称" value={edit?.name} onChange={e=>setEdit({...edit,name:e.target.value})}/></div>
          {creating&&<div className="task-form-item"><label htmlFor="task-case-select">科研案例（必选）</label>{caseError?<><Alert type="error" message={caseError}/><Button aria-label="重试加载案例" loading={caseBusy} onClick={loadCases}>重试加载案例</Button></>:<Select virtual={false} id="task-case-select" aria-label="科研案例" placeholder="选择模型与数据集组合" value={edit?.case_id} onChange={case_id=>setEdit({...edit,case_id})} options={choices.map(c=>({value:c.id,label:caseLabel(c)}))}/>}<p>创建后进入原始数据处理，再选择该案例的数据来源。</p></div>}
          {edit?.fork?<p>继承来源任务的科研案例、配置与数据绑定；派生后可在原始数据处理阶段修改数据来源。</p>:<div className="task-form-item"><label htmlFor="task-description-input">任务描述</label><Input.TextArea id="task-description-input" aria-label="任务描述" placeholder="研究目的或方案说明" value={edit?.description} onChange={e=>setEdit({...edit,description:e.target.value})}/></div>}
        </div>
      </Modal>
    </section>
  );
}
