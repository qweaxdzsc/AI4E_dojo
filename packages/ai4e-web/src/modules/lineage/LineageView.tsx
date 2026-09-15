import { useEffect, useMemo, useState } from "react";
import { Alert, Button, Input, Modal } from "antd";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { ActionButton } from "../../infrastructure/components/ActionButton";
import { forkTask, WORKBENCH_STAGES, STAGE_SLUGS } from "../tasks";
import { details, list } from "./api";
import { displayValue, flattenEntries, valueType } from "./flatten";
import { connectorPath, layoutTree, NODE_H, NODE_W } from "./layout";
import "./lineage.css";

const STAGE_API: Record<number, string> = { 1: "rawprep", 2: "trainprep", 3: "model", 4: "train", 5: "train", 6: "infer", 7: "post" };
const GROUPS = ["输入", "输出", "参数"] as const;
const ORIGIN: Record<string, string> = { template: "模板创建", fork: "派生创建", run: "运行产物创建" };

function short(v?: string) {
  return v ? String(v).slice(0, 8) : "—";
}

/** 版本树按真实父版本画节点与连线，右侧只展示创建快照、来源与固定运行。 */
export function LineageView({
  project,
  tasks = [],
  onCompare,
}: {
  project: string;
  tasks?: any[];
  onCompare?: (version: string, parameter?: string) => void;
}) {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const [rows, setRows] = useState<any[]>([]);
  const [selected, setSelected] = useState<any>();
  const [detail, setDetail] = useState<any>();
  const [error, setError] = useState("");
  const [zoom, setZoom] = useState(1);
  const [step, setStep] = useState(4);
  const [group, setGroup] = useState<(typeof GROUPS)[number]>("参数");
  const [picked, setPicked] = useState<string[]>([]);
  const [forking, setForking] = useState<any>();
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState("");
  useEffect(() => {
    list(project)
      .then((records) => {
        setRows(records);
        const wanted = params.get("version");
        const first = records.find((v: any) => v.id === wanted) || records[0];
        setSelected(first);
      })
      .catch((e) => setError(e.message));
  }, [project, params]);
  useEffect(() => {
    setDetail(undefined);
    setPicked([]);
    if (!selected) return;
    details(project, selected.id)
      .then(setDetail)
      .catch((e) => setError(e.message));
  }, [project, selected]);
  const name = (v: any) => tasks.find((t) => t.id === v?.task_id)?.name || v?.task_id || "未命名任务";
  const layout = useMemo(
    () => layoutTree(rows.map((v) => ({ id: v.id, parent: v.parent_version_id }))),
    [rows],
  );
  const stage = detail?.stages?.find((s: any) => s.stage === STAGE_API[step]);
  const rowsForGroup = useMemo(() => {
    if (!selected) return [];
    if (group === "输入") {
      return Object.entries(selected.assets || {}).map(([key, asset]: any) => ({
        key,
        value: asset?.source?.path || asset?.path || asset?.id || key,
      }));
    }
    if (group === "输出") {
      const copied = Object.entries(selected.copied_outputs || {}).map(([key, asset]: any) => ({
        key,
        value: asset?.path || asset?.id || key,
      }));
      const runs = (stage?.runs || []).map((run: any) => ({
        key: "固定运行/" + run.run_id.slice(0, 8),
        value: run.status + " · " + run.operation_mode,
      }));
      return copied.concat(runs);
    }
    return flattenEntries(stage?.configuration);
  }, [selected, stage, group]);
  function addParameter(path: string) {
    const api = STAGE_API[step];
    if (!selected || !api) return;
    onCompare?.(selected.id, api + "." + path);
  }
  function addPicked() {
    if (!picked.length) {
      setError("请先勾选输入、输出或参数");
      return;
    }
    picked.forEach(addParameter);
    setPicked([]);
  }
  async function persistFork() {
    if (saving || !forking?.name?.trim()) {
      setFormError("请填写任务名称");
      return;
    }
    setSaving(true);
    setFormError("");
    try {
      const result = await forkTask(project, forking.task_id, forking.name.trim());
      setForking(undefined);
      nav(`/projects/${project}/tasks/${result.id}/rawprep`);
    } catch (e: any) {
      setFormError(e.message);
    } finally {
      setSaving(false);
    }
  }
  return (
    <section className="lineage-view">
      {error && <Alert type="error" message={error} />}
      <div className="toolbar treeactions">
        <div className="toolbar-spacer" />
        <Button
          type="primary"
          disabled={!selected}
          onClick={() => selected && setForking({ task_id: selected.task_id, name: name(selected) + " 派生" })}
        >
          ⑂　基于选中任务 Fork
        </Button>
      </div>
      <div className="cols treecols">
        <section className="panel tree">
          <div className="toolbar">
            <h2>版本血缘图</h2>
            <div className="toolbar-spacer" />
            <Button onClick={() => setZoom((z) => Math.min(1.5, z + 0.15))}>＋ 放大</Button>
            <Button onClick={() => setZoom((z) => Math.max(0.6, z - 0.15))}>－ 缩小</Button>
            <Button onClick={() => setZoom(1)}>重置</Button>
          </div>
          <div className="treecanvas">
            <div className="tree-zoom" style={{ width: layout.width, height: layout.height, transform: `scale(${zoom})` }}>
              <svg viewBox={`0 0 ${layout.width} ${layout.height}`} width={layout.width} height={layout.height} aria-label="任务版本血缘">
                <defs>
                  <marker id="lineage-arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto">
                    <path d="M0 0 L8 4 L0 8z" fill="#829aca" />
                  </marker>
                </defs>
                <g stroke="#829aca" fill="none" markerEnd="url(#lineage-arrow)">
                  {rows
                    .filter((v) => v.parent_version_id && layout.boxes.some((b) => b.id === v.parent_version_id))
                    .map((v) => {
                      const parent = layout.boxes.find((b) => b.id === v.parent_version_id)!;
                      const child = layout.boxes.find((b) => b.id === v.id)!;
                      return <path key={v.id} d={connectorPath(parent, child)} />;
                    })}
                </g>
              </svg>
              {layout.boxes.map((box) => {
                const version = rows.find((v) => v.id === box.id);
                if (!version) return null;
                const active = selected?.id === version.id;
                return (
                  <button
                    key={version.id}
                    type="button"
                    className={"tree-node" + (active ? " selected" : "")}
                    style={{ left: box.x, top: box.y, width: NODE_W, height: NODE_H }}
                    aria-label={"选择任务 " + version.id}
                    onClick={() => setSelected(version)}
                  >
                    <i className="dot" />
                    <b>
                      {short(version.id)} · {name(version).slice(0, 10)}
                    </b>
                    <small>
                      来源：{short(version.parent_version_id)} / 基线 {short(version.baseline_version_id)}
                    </small>
                  </button>
                );
              })}
            </div>
          </div>
          <div className="note">ⓘ　节点 = 一个任务的版本；线 = 真实来源关系。右侧只检查所选任务。</div>
        </section>
        <aside className="panel treeinspector">
          {selected ? (
            <>
              <span className="badge blue">选中任务：{short(selected.id)}</span>
              <h2>{name(selected)}</h2>
              <p>
                版本　<b>{short(selected.id)}</b>　来源　<b>{short(selected.parent_version_id)}</b>　基线　
                <b>{short(selected.baseline_version_id)}</b>
              </p>
              <div className="origin-pills">
                <span>创建版本 · {ORIGIN[selected.source?.kind] || selected.source?.kind || "已登记"}</span>
                <span className="current">当前工作目录 · 不在此页冒充</span>
                <span>固定运行 · {stage?.runs?.length || 0} 条</span>
              </div>
              <div className="note">
                ⓘ　参数来源：创建快照 · {detail?.revision ? String(detail.revision).slice(0, 12) : "读取中"}。创建记录、当前目录与固定运行分开。
              </div>
              <label>
                工作台阶段{" "}
                <select aria-label="血缘任务阶段" value={step} onChange={(e) => setStep(Number(e.target.value))}>
                  {WORKBENCH_STAGES.map((title, i) => (
                    <option key={title} value={i}>
                      {i + 1}. {title}
                    </option>
                  ))}
                </select>
              </label>
              <div className="tabs compact" role="tablist">
                {GROUPS.map((item) => (
                  <button
                    key={item}
                    type="button"
                    role="tab"
                    aria-selected={group === item}
                    className={group === item ? "active" : ""}
                    onClick={() => {
                      setGroup(item);
                      setPicked([]);
                    }}
                  >
                    {item}
                  </button>
                ))}
              </div>
              <div className="parameterlist">
                <table>
                  <thead>
                    <tr>
                      <th>选择</th>
                      <th>参数名称</th>
                      <th>类型</th>
                      <th>参数值</th>
                      <th />
                    </tr>
                  </thead>
                  <tbody>
                    {rowsForGroup.map((row) => (
                      <tr key={row.key}>
                        <td>
                          <input
                            aria-label={"选择 " + row.key}
                            type="checkbox"
                            checked={picked.includes(row.key)}
                            onChange={(e) =>
                              setPicked((old) => (e.target.checked ? [...old, row.key] : old.filter((k) => k !== row.key)))
                            }
                          />
                        </td>
                        <td>{row.key}</td>
                        <td>{valueType(row.value)}</td>
                        <td>{displayValue(row.value)}</td>
                        <td>
                          {group === "参数" && STAGE_API[step] && (
                            <Button size="small" onClick={() => addParameter(row.key)}>
                              加入比较
                            </Button>
                          )}
                        </td>
                      </tr>
                    ))}
                    {!rowsForGroup.length && (
                      <tr>
                        <td colSpan={5}>{STAGE_API[step] ? "该分组暂无创建记录" : "此阶段未开放创建快照"}</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
              <div className="stack">
                <ActionButton type="primary" onClick={addPicked}>
                  添加选中项到对比参数
                </ActionButton>
                <Button onClick={() => selected && onCompare?.(selected.id)}>
                  前往版本比较 →
                </Button>
                <Link to={"/projects/" + project + "/tasks/" + selected.task_id + "/" + STAGE_SLUGS[step]}>
                  <Button>进入此任务当前阶段</Button>
                </Link>
              </div>
              <small>从版本树勾选输入、输出或参数，加入真实比较；不把当前目录当作创建历史。</small>
            </>
          ) : (
            <p>选择一个版本查看来源与参数</p>
          )}
        </aside>
      </div>
      <Modal
        classNames={{ wrapper: "task-form-dialog" }}
        width={520}
        open={!!forking}
        title="派生任务"
        onCancel={() => !saving && setForking(undefined)}
        footer={
          <>
            <Button disabled={saving} onClick={() => setForking(undefined)}>
              取消
            </Button>
            <ActionButton type="primary" loading={saving} onClick={persistFork}>
              派生并进入原始处理
            </ActionButton>
          </>
        }
      >
        <div className="task-form">
          {formError && <Alert type="error" message={formError} />}
          <div className="task-form-item">
            <label htmlFor="lineage-fork-name">任务名称</label>
            <Input id="lineage-fork-name" aria-label="任务名称" value={forking?.name} onChange={(e) => setForking({ ...forking, name: e.target.value })} />
          </div>
          <p>继承来源任务的科研案例、配置与数据绑定；派生后可在原始数据处理阶段修改数据来源。</p>
        </div>
      </Modal>
    </section>
  );
}
