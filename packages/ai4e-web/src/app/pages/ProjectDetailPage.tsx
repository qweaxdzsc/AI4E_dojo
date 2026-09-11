import { Alert } from "antd";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { ComparisonView } from "../../modules/comparisons";
import { listRuns } from "../../modules/executions";
import { ProjectFiles } from "../../modules/files";
import { LineageView } from "../../modules/lineage";
import { ProjectReport } from "../../modules/reports";
import { TaskManagement, listTasks } from "../../modules/tasks";
import { BatchShell } from "./BatchShell";

const PROJECT_TABS = [
  ["tasks", "任务管理"],
  ["lineage", "版本树"],
  ["compare", "版本比较"],
  ["report", "项目报告"],
  ["files", "文件管理"],
  ["batch", "批量运行"],
] as const;

export function ProjectDetailPage() {
  const { p = "", tab = "tasks" } = useParams(),
    nav = useNavigate();
  const [comparisonSeed,setComparisonSeed]=useState<any>();
  const [tasks, setTasks] = useState<any[]>([]),
    [runs, setRuns] = useState<any[]>([]),
    [error, setError] = useState(""),
    [ready, setReady] = useState(false);
  function reload() {
    Promise.all([listTasks(p), listRuns(p)])
      .then(([t, r]) => {
        setTasks(t);
        setRuns(r);
      })
      .catch((e) => setError(e.message));
  }
  useEffect(() => {
    setReady(false);
    Promise.all([listTasks(p), listRuns(p)])
      .then(([t, r]) => {
        setTasks(t);
        setRuns(r);
      })
      .catch((e) => setError(e.message))
      .finally(() => setReady(true));
  }, [p]);
  return (
    <>
      
      {error && <Alert type="error" message={error} />}
      <nav className="tabs projecttabs" aria-label="项目功能" role="tablist">
        {PROJECT_TABS.map(([key, label]) => (
          <button
            key={key}
            type="button"
            role="tab"
            aria-selected={tab === key}
            className={tab === key ? "active" : ""}
            onClick={() => nav("/projects/" + p + "/" + key)}
          >
            {label}
          </button>
        ))}
      </nav>
      {tab === "tasks" ? (
        <TaskManagement project={p} rows={tasks} runs={runs} reload={reload} loading={!ready} />
      ) : tab === "lineage" ? (
        <LineageView project={p} tasks={tasks} onCompare={(version,parameter)=>{setComparisonSeed((old:any)=>({mode:"versions",left:old?.right?version:old?.left||version,right:old?.right?undefined:old?.left?version:undefined,parameter}));nav("/projects/"+p+"/compare")}} />
      ) : tab === "compare" ? (
        <ComparisonView project={p} tasks={tasks} runs={runs} initialSelection={comparisonSeed} />
      ) : tab === "report" ? (
        <ProjectReport project={p} runs={runs} />
      ) : tab === "files" ? (
        <ProjectFiles project={p} tasks={tasks} />
      ) : (
        <BatchShell />
      )}
    </>
  );
}
