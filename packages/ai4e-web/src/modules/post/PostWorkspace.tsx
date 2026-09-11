import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Checkbox, Input, InputNumber, Select } from "antd";
import { useCallback, useEffect, useState } from "react";
import type { ReactNode } from "react";
import { FileBrowser } from "../files";
import { VisualizationWorkspace } from "../visualization";
import { PostMetricCharts } from "./PostMetricCharts";
import { listScenes, postMetrics, registerSource, saveScene } from "./api";
import "./post.css";

const FLAG_LABELS: Record<string, string> = {
  evaluate: "评价指标",
  save_predictions: "保存预测",
  export_vtk: "导出网格",
  query: "完整网格查询",
};
const TABS = [
  { key: "metrics", label: "指标数据" },
  { key: "charts", label: "图表" },
  { key: "visualization", label: "结果可视化" },
] as const;

function metricRows(metric: any) {
  const evaluation = metric?.evaluation?.metrics || metric?.evaluation || {};
  const rows: any[] = [];
  for (const [name, value] of Object.entries(evaluation)) {
    if (typeof value === "number") rows.push({ name, value });
    else if (value && typeof value === "object") {
      if ("value" in value) rows.push({ name, ...(value as object) });
      else
        for (const key of ["mse", "mae", "relative_l2"])
          if (typeof (value as any)[key] === "number")
            rows.push({ name: name + " / " + key, value: (value as any)[key] });
    }
  }
  return rows;
}

function firstNumber(evaluation: any, key: string) {
  const metrics = evaluation?.metrics || evaluation || {};
  for (const value of Object.values(metrics)) {
    if (typeof (value as any)?.[key] === "number") return (value as any)[key];
    if (key === "relative_l2" && typeof value === "number") return value;
  }
  return undefined;
}

/** 后处理宿主组织真实指标、受控文件和持久化场景。 */
export function PostWorkspace({
  project,
  task,
  run,
  runs = [],
  onRun,
  values,
  onChange,
  bindings,
  onExecute,
  busy,
}: {
  project: string;
  task: string;
  run?: string;
  runs?: any[];
  onRun?: (id: string) => void;
  values: any;
  onChange: (key: string, v: any) => void;
  bindings: ReactNode;
  onExecute: () => void;
  busy: boolean;
}) {
  const [tab, setTab] = useState("visualization");
  const [metric, setMetric] = useState<any>();
  const [root, setRoot] = useState("");
  const [files, setFiles] = useState<string[]>([]);
  const [sources, setSources] = useState<any[]>([]);
  const [scenes, setScenes] = useState<any[]>([]);
  const [saved, setSaved] = useState<any>();
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [query, setQuery] = useState("");
  useEffect(() => {
    listScenes(project)
      .then(setScenes)
      .catch((e) => setError(e.message));
    if (run)
      postMetrics(project, run)
        .then(setMetric)
        .catch((e) => setError(e.message));
  }, [project, run]);
  const selection = useCallback((nextRoot: string, nextFiles: string[]) => {
    setRoot(nextRoot);
    setFiles(nextFiles);
  }, []);
  async function add() {
    try {
      const refs = await Promise.all(files.map((path) => registerSource(project, task, root, path)));
      setSources(refs.map((r, i) => ({ ...r, name: files[i] })));
      setSaved(undefined);
      setError("");
    } catch (e: any) {
      setError(e.message);
    }
  }
  async function persist(scene: any) {
    try {
      const result = await saveScene(project, scene, saved);
      setSaved(result);
      setScenes(await listScenes(project));
      setNotice("场景已保存，固定数据修订");
    } catch (e: any) {
      setError(e.message);
    }
  }
  const rows = metricRows(metric).filter((row) => row.name.toLowerCase().includes(query.trim().toLowerCase()));
  const evaluation = metric?.evaluation;
  const kpis = [
    { label: "相对 L2", value: firstNumber(evaluation, "relative_l2") },
    { label: "MSE", value: firstNumber(evaluation, "mse") },
    { label: "推理时间", value: undefined },
    { label: "峰值显存", value: undefined },
  ];
  return (
    <div className={"post-workspace" + (tab !== "visualization" ? " data-open" : "")}>
      <section className={"post-shell" + (tab !== "visualization" ? " data-active" : "")}>
        <div className="post-config">
          <label>
            后处理运行
            <Select
              aria-label="后处理运行"
              style={{ width: 220 }}
              value={run}
              options={runs.map((r) => ({ value: r.id, label: r.id.slice(0, 8) + " · " + r.status }))}
              onChange={onRun}
            />
          </label>
          {bindings}
          {"split" in values && (
            <label>
              分片
              <Input aria-label="后处理分片" value={values.split ?? ""} onChange={(e) => onChange("split", e.target.value)} />
            </label>
          )}
          {"sample_indices" in values && (
            <label>
              样本索引
              <Input
                aria-label="后处理样本索引"
                value={(values.sample_indices || []).join(",")}
                onChange={(e) =>
                  onChange(
                    "sample_indices",
                    e.target.value
                      .split(/[,\s]+/)
                      .filter(Boolean)
                      .map(Number)
                      .filter((n) => !Number.isNaN(n)),
                  )
                }
              />
            </label>
          )}
          {"query_chunk_size" in values && (
            <label>
              分块大小
              <InputNumber aria-label="查询块大小" value={values.query_chunk_size} min={1} onChange={(v) => onChange("query_chunk_size", v)} />
            </label>
          )}
          <div className="post-config-flags">
            {["evaluate", "save_predictions", "export_vtk", "query"]
              .filter((k) => k in values)
              .map((k) => (
                <Checkbox key={k} checked={values[k]} onChange={(e) => onChange(k, e.target.checked)}>
                  {FLAG_LABELS[k]}
                </Checkbox>
              ))}
            <Button type="primary" loading={busy} onClick={onExecute}>
              运行后处理
            </Button>
          </div>
        </div>
        <p className="post-note">评估 / 预测 / 网格分别记录进度，部分失败不展示为完整成功。检查与保存使用当前任务已写入配置。</p>
        <nav className="post-tabs" aria-label="后处理视图">
          {TABS.map((item) => (
            <button
              key={item.key}
              type="button"
              role="tab"
              aria-selected={tab === item.key}
              className={tab === item.key ? "active" : ""}
              onClick={() => setTab(item.key)}
            >
              {item.label}
            </button>
          ))}
        </nav>
        {error && <Alert type="error" message={error} />}
        {notice && <Alert type="success" message={notice} />}
        {tab === "metrics" && (
          <section className="post-data-tab">
            <div className="metric-filterbar">
              <input aria-label="搜索指标" placeholder="搜索指标名称…" value={query} onChange={(e) => setQuery(e.target.value)} />
              <small>仅当前运行真实评价</small>
            </div>
            <div className="metric-table-scroll">
              <table className="metric-data-table">
                <thead>
                  <tr>
                    <th>指标名称</th>
                    <th>真实值</th>
                    <th>单位</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  {rows.length ? (
                    rows.map((row) => (
                      <tr key={row.name}>
                        <td>{row.name}</td>
                        <td>{row.value}</td>
                        <td>{row.unit ?? "未声明"}</td>
                        <td>{metric?.status || "尚无记录"}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="metric-empty" colSpan={4}>
                        {run ? "当前运行尚无符合筛选的真实评价" : "选择后处理运行后显示真实指标"}
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
            <footer className="metric-pagination">
              <span>共 {rows.length} 条数据</span>
              <small>不复刻示意多模型对照表</small>
            </footer>
          </section>
        )}
        {tab === "charts" && (
          <section className="post-charts-tab">
            <div className="post-kpis">
              {kpis.map((item) => (
                <div key={item.label} className="post-kpi">
                  <div className="kpi-main">
                    <span>{item.label}</span>
                    <strong>{item.value == null ? "尚无记录" : Number(item.value).toPrecision(4)}</strong>
                  </div>
                </div>
              ))}
            </div>
            <PostMetricCharts evaluation={evaluation} run={run} />
            <section className="model-performance">
              <div className="chart-card-head">
                <h3>模型性能汇总表</h3>
              </div>
              <table className="metric-data-table">
                <thead>
                  <tr>
                    <th>指标名称</th>
                    <th>真实值</th>
                    <th>单位</th>
                    <th>状态</th>
                  </tr>
                </thead>
                <tbody>
                  {metricRows(metric).length ? (
                    metricRows(metric).map((row) => (
                      <tr key={row.name}>
                        <td>{row.name}</td>
                        <td>{row.value}</td>
                        <td>{row.unit ?? "未声明"}</td>
                        <td>{metric?.status || "尚无记录"}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td className="metric-empty" colSpan={4}>
                        尚无当前运行的真实评价汇总
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </section>
            <div className="post-chart-note">推理耗时与峰值显存未写入产物时保持不可用，不填演示数。</div>
          </section>
        )}
        {tab === "visualization" && (
          <>
            <div className="post-viz-toolbar">
              <Select
                aria-label="保存的场景"
                placeholder="恢复场景"
                style={{ width: 240 }}
                options={scenes.map((s) => ({ value: s.scene_id, label: s.scene_id.slice(0, 8) }))}
                value={saved?.scene_id}
                onChange={(id) => {
                  const value = scenes.find((s) => s.scene_id === id);
                  setSaved(value);
                  setSources(value.scene.sources);
                }}
              />
              <Button onClick={add} disabled={!files.length}>
                将所选文件加入场景
              </Button>
            </div>
            <div className="post-visualization-layout">
              <section className="post-pane">
                <div className="post-pane-header">
                  <span className="fileheading">结果文件</span>
                </div>
                <FileBrowser compact project={project} task={task} onSelection={selection} />
                {sources.length > 0 && (
                  <div className="post-source-list">
                    {sources.map((s) => (
                      <button key={s.asset_id} type="button" className="active">
                        {s.name || s.asset_id}
                      </button>
                    ))}
                  </div>
                )}
              </section>
              {sources.length ? (
                <VisualizationWorkspace
                  key={sources.map((s) => s.asset_id).join(",") + (saved?.scene_id || "")}
                  scope={{ project_id: project, task_id: task }}
                  sources={sources}
                  scene={saved?.scene}
                  mode="post"
                  onSceneChange={persist}
                  onError={(e) => setError(e.message)}
                />
              ) : (
                <>
                  <section className="post-pane">
                    <div className="post-pane-header">可视化资产</div>
                    <div className="empty-record">加入真实文件后显示管线与属性</div>
                  </section>
                  <section className="post-pane">
                    <div className="post-pane-header">三维可视化窗口</div>
                    <div className="empty-record">选择真实网格或字段文件，加入三维场景</div>
                  </section>
                </>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
