import { Alert } from "antd";
import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { UnavailablePanel } from "../../infrastructure/components/UnavailablePanel";
import { listProjects } from "../../modules/projects";
import { StageWorkbench } from "../../modules/stages";
import { RawprepWorkbench } from "../../modules/rawprep";
import { configuration, taskDetail, WORKBENCH_STAGES } from "../../modules/tasks";
import "./task-workbench.css";

function recipeBadge(task: any, text: string) {
  const id = String(task?.case_id || "");
  if (id.includes("transolver")) return "Aero CFD / Transolver-3";
  if (id.includes("abupt")) return "Aero CFD / AB-UPT";
  if (id) return id;
  if (text.includes("transolver")) return "Aero CFD / Transolver-3";
  if (text.includes("nasa_crm") || text.includes("shapenet_car") || text.includes("abupt")) return "Aero CFD / AB-UPT";
  return "未绑定案例";
}

function scrollHandoff() {
  document.getElementById("stage-handoff")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

/** 工作台标题、八步与 Recipe 条对照整合 HTML；不复刻示意模板弹窗。 */
export function TaskWorkbenchPage() {
  const { p = "", t = "", step = "1" } = useParams();
  const current = Number(step);
  const [task, setTask] = useState<any>(),
    [projectName, setProjectName] = useState(""),
    [recipe, setRecipe] = useState("未绑定案例"),
    [error, setError] = useState("");
  useEffect(() => {
    taskDetail(p, t)
      .then((value) => {
        setTask(value);
        localStorage.setItem(
          "dojo.last-workbench",
          JSON.stringify({ project: p, task: t, step: current >= 0 && current <= 7 ? step : "1" }),
        );
      })
      .catch((e) => setError(e.message));
  }, [p, t, step, current]);
  useEffect(() => {
    listProjects()
      .then((rows) => setProjectName(rows.find((r: any) => r.id === p)?.name || ""))
      .catch(() => setProjectName(""));
  }, [p]);
  useEffect(() => {
    configuration(p, t)
      .then((cfg) => setRecipe(recipeBadge(task, JSON.stringify(cfg || {}))))
      .catch(() => setRecipe(recipeBadge(task, "")));
  }, [p, t, task]);
  const status = task?.archived ? "已归档" : "研究中";
  return (
    <section className="task-workbench">
      <div className="taskheading">
        <div>
          <h1>
            {task?.name || "任务工作台"} <span className="statuspill draft">{status}</span>
          </h1>
          <p>
            任务 ID：{task?.id?.slice(0, 8) || "—"}　 |　 项目：{projectName || "—"}　 |　负责人：{task?.created_by || "未记录"}　 |　版本 {task?.version_id?.slice(0, 8) || "—"} / 来源 {task?.parent_version_id?.slice(0, 8) || "—"} / 基线 {task?.baseline_version_id?.slice(0, 8) || "—"}
          </p>
        </div>
        <div className="taskheading-actions">
          <div className="recipestrip">
            <span className="badge blue">{recipe}</span>
            <span>可复制 Recipe</span>
            <span className="recipeflow">原始处理 → 训练准备 → 训练 → 后处理</span>
            <button type="button" onClick={scrollHandoff}>
              输入输出交接
            </button>
          </div>
          <Link className="switch-task" to="/workbench?choose=1">
            切换任务
          </Link>
          <Link className="return-task" to={"/projects/" + p + "/tasks"}>
            返回任务管理
          </Link>
        </div>
      </div>
      <nav className="workbench-steps topsteps" aria-label="工作台步骤">
        {WORKBENCH_STAGES.map((title, i) => (
          <Link
            key={title}
            className={"topstep " + (i === current ? "active" : i < current ? "done" : "")}
            to={"/projects/" + p + "/tasks/" + t + "/" + i}
          >
            <span>{i < current ? "✓" : i + 1}</span>
            <b>{title}</b>
          </Link>
        ))}
      </nav>
      {error && <Alert type="error" message={error} />}
      {step === "1" ? (
        <RawprepWorkbench key={t} project={p} task={t} />
      ) : current >= 2 && current <= 6 ? (
        <StageWorkbench key={t + step} project={p} task={t} stage={["", "", "trainprep", "model", "train", "execution", "post"][current]} />
      ) : (
        <div className="stage-toolbar" id="stage-handoff">
          <div className="stageheading">
            <h2>{WORKBENCH_STAGES[current] || "未开放阶段"}</h2>
            <p>{current === 0 ? "CAE 采样入口暂不开放，不能把模型采样移入此页。" : "任务报告入口本轮未开放，不提供编辑、发布或导出。"}</p>
          </div>
          <UnavailablePanel />
        </div>
      )}
      <div className="stage-foot">
        {current > 0 ? (
          <Link to={"/projects/" + p + "/tasks/" + t + "/" + (current - 1)}>← 上一步</Link>
        ) : (
          <span />
        )}
        <div className="toolbar-spacer" />
        {current < 7 ? (
          <Link className="next" to={"/projects/" + p + "/tasks/" + t + "/" + (current + 1)}>
            下一步 →
          </Link>
        ) : null}
      </div>
    </section>
  );
}
