import { Alert } from "antd";
import { useEffect, useState } from "react";
import { Link, useParams, useNavigate, useSearchParams } from "react-router-dom";
import { UnavailablePanel } from "../../infrastructure/components/UnavailablePanel";
import { listProjects } from "../../modules/projects";
import { StageWorkbench } from "../../modules/stages";
import { TrainingMonitor } from "../../modules/executions";
import { RawprepWorkbench } from "../../modules/rawprep";
import { taskDetail, WORKBENCH_STAGES, STAGE_SLUGS, resolveStage, stageDisplay, taskDisplay } from "../../modules/tasks";
import "./task-workbench.css";
import { InferenceWorkspace } from "../../modules/inference";
import { PostResultsWorkspace } from "../../modules/post";

/** 工作台标题收成单行元信息；九步导航仍对照整合 HTML。 */
export function TaskWorkbenchPage() {
  const { p = "", t = "", step = "1" } = useParams();
  const slug=resolveStage(step), current=STAGE_SLUGS.indexOf(slug as typeof STAGE_SLUGS[number]);
  const navigate=useNavigate(), [params]=useSearchParams();
  const [task, setTask] = useState<any>(),
    [projectName, setProjectName] = useState(""),
    [error, setError] = useState("");
  useEffect(() => {
    let live=true;
    const read=()=>taskDetail(p,t).then(value=>{if(!live)return;setTask(value);setError('');localStorage.setItem('dojo.last-workbench',JSON.stringify({project:p,task:t,step:slug}))}).catch(e=>live&&setError(e.message));
    const changed=(event:Event)=>{const detail=(event as CustomEvent).detail;if(detail?.project===p&&detail?.task===t)void read()};
    void read();const timer=setInterval(read,8000);window.addEventListener('dojo:task-updated',changed);return()=>{live=false;clearInterval(timer);window.removeEventListener('dojo:task-updated',changed)};
  },[p,t]);
  useEffect(() => {
    listProjects()
      .then((rows) => setProjectName(rows.find((r: any) => r.id === p)?.name || ""))
      .catch(() => setProjectName(""));
  }, [p]);
  const status = taskDisplay(task).label;
  return (
    <section className="task-workbench">
      <div className="taskheading">
        <h1>
          <span className="taskheading-name">{task?.name || "任务工作台"}</span>
          <span className="statuspill draft">{status}</span>
          <span className="taskheading-meta">
            任务 ID：{task?.id?.slice(0, 8) || "—"}　 |　 项目：{projectName || "—"}　 |　负责人：{task?.created_by || "未记录"}　 |　版本 {task?.version_id?.slice(0, 8) || "—"} / 来源 {task?.parent_version_id?.slice(0, 8) || "—"} / 基线 {task?.baseline_version_id?.slice(0, 8) || "—"}
          </span>
        </h1>
      </div>
      <nav className="workbench-steps topsteps" aria-label="工作台步骤">
        {WORKBENCH_STAGES.map((title, i) => { const state=stageDisplay(task,i);return (
          <Link
            key={title}
            className={"topstep " + (i === current ? "active " : "") + (state.finished ? "done" : "")}
            title={state.label}
            aria-label={title+" · "+state.label}
            aria-current={i===current?"step":undefined}
            to={"/projects/" + p + "/tasks/" + t + "/" + STAGE_SLUGS[i]}
          >
            <span>{state.finished ? "✓" : i + 1}</span>
            <b>{title}</b>
          </Link>
        )})}
      </nav>
      {error && <Alert type="error" message={error} />}
      <div className="workbench-stage">
      {slug === "rawprep" ? (
        <RawprepWorkbench key={t} project={p} task={t} />
      ) : slug === "infer" ? (
        <InferenceWorkspace key={p+t} project={p} task={t} onOpenResult={(batch,run,sample,index,split)=>navigate(`/projects/${p}/tasks/${t}/post?`+new URLSearchParams({batch,run,sample,result:String(index),...(split?{split}:{})}))}/>
      ) : slug === "post" ? (
        <PostResultsWorkspace key={p+t} project={p} task={t} tab={params.get('tab')||undefined} batchId={params.get('batch')||undefined} resultIndex={Number(params.get('result')||0)} runId={params.get('run')||undefined} sample={params.get('sample')||undefined} split={params.get('split')||undefined}/>
      ) : slug === "train" ? (
        <TrainingMonitor key={p+t} project={p} task={t} initialRun={params.get("run") || undefined} />
      ) : current >= 2 && current <= 4 ? (
        <StageWorkbench key={t + step} project={p} task={t} stage={["", "", "trainprep", "model", "train"][current]} onStarted={(runId)=>navigate(`/projects/${p}/tasks/${t}/train?run=${runId}`)} />
      ) : (
        <div className="stage-toolbar" id="stage-handoff">
          <div className="stageheading">
            <h2>{WORKBENCH_STAGES[current] || "未开放阶段"}</h2>
            <p>{current === 0 ? "CAE 采样入口暂不开放，不能把模型采样移入此页。" : "任务报告入口本轮未开放，不提供编辑、发布或导出。"}</p>
          </div>
          <UnavailablePanel />
        </div>
      )}
      </div>
      <div className="stage-foot">
        {current > 0 ? (
          <Link to={"/projects/" + p + "/tasks/" + t + "/" + STAGE_SLUGS[current - 1]}>← 上一步</Link>
        ) : (
          <span />
        )}
        <div className="toolbar-spacer" />
        {current < STAGE_SLUGS.length - 1 ? (
          <Link className="next" to={"/projects/" + p + "/tasks/" + t + "/" + STAGE_SLUGS[current + 1]}>
            下一步 →
          </Link>
        ) : null}
      </div>
    </section>
  );
}
