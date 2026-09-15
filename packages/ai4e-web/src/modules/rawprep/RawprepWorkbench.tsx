import { DeleteOutlined, EditOutlined } from "@ant-design/icons";
import { Alert, Checkbox, Input, InputNumber, Select, Spin, Space } from "antd";
import { useCallback, useEffect, useRef, useState } from "react";
import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { ExecutionLog, listRuns } from "../executions";
import { getRun, readLog } from "../executions";
import { BoundDatasetFiles } from "./BoundDatasetFiles";
import { FieldExtractionEditor, type FieldChoice } from "./FieldExtractionEditor";
import {
  read,
  save,
  check,
  execute,
  trial,
  datasetCatalog,
  type DatasetBinding,
} from "./api";
import "./rawprep-workbench.css";

type Choice = { name: string; source_field: string; components: number };
type ActionKind = "refresh" | "check" | "trial" | "execute";
const ACTION_COPY: Record<
  ActionKind,
  { verb: string; running: string; done: string; fail: string }
> = {
  refresh: {
    verb: "刷新样本与字段",
    running: "刷新中",
    done: "已刷新",
    fail: "刷新失败",
  },
  check: {
    verb: "校验输入与配置",
    running: "校验中",
    done: "校验通过",
    fail: "校验失败",
  },
  trial: {
    verb: "按所选范围试跑",
    running: "试跑中",
    done: "试跑完成",
    fail: "试跑失败",
  },
  execute: {
    verb: "正式执行",
    running: "处理中",
    done: "已完成",
    fail: "失败",
  },
};
/** 从数据组件描述展示生效配置；浏览文件不改变样本执行范围，也不按 train/test 分片。 */
export function RawprepWorkbench({
  project,
  task,
}: {
  project: string;
  task: string;
}) {
  const [cfg, setCfg] = useState<any>(),
    [profile, setProfile] = useState<any>(),
    [binding, setBinding] = useState<DatasetBinding>(),
    [catalog, setCatalog] = useState<any>();
  const [scope, setScope] = useState<any>({ mode: "all", values: [] }),
    [dirty, setDirty] = useState(false),
    [busy, setBusy] = useState(false),
    [catalogBusy, setCatalogBusy] = useState(false),
    [error, setError] = useState(""),
    [notice, setNotice] = useState(""),
    [run, setRun] = useState<string>(),
    [resultRun, setResultRun] = useState<string>(),
    [progress, setProgress] = useState<any>(),
    [activity, setActivity] = useState<{ status: string; text?: string }>(),
    [activeAction, setActiveAction] = useState<ActionKind>(),
    [resultTick, setResultTick] = useState(0),
    [entryEdit, setEntryEdit] = useState<FieldChoice | null | undefined>(),
    [root, setRoot] = useState(""),
    [files, setFiles] = useState<string[]>([]),
    [processedName, setProcessedName] = useState("");
  const submitting = useRef(false),
    generation = useRef(0),
    requestKey = useRef(crypto.randomUUID());
  useEffect(() => {
    let live = true;
    Promise.all([read(project, task), listRuns(project, task)])
      .then(([c, r]: any) => {
        if (!live) return;
        setCfg(c);
        setProfile(c.profile);
        setProcessedName(c.processed_name || c.profile?.dataset_id || "");
        setRun(r.filter((v: any) => v.stages?.includes("rawprep")).at(-1)?.id);
        setResultRun(
          r
            .filter(
              (v: any) =>
                v.stages?.includes("rawprep") &&
                (v.operation_mode || "execute") === "execute",
            )
            .at(-1)?.id,
        );
      })
      .catch((e) => setError(e.message));
    return () => {
      live = false;
    };
  }, [project, task]);
  useEffect(() => {
    if (!resultRun) return;
    let live = true;
    Promise.all([getRun(project, resultRun), readLog(project, resultRun)])
      .then(([state, log]: any) => {
        if (live) setProgress({ status: state.status, text: log.text || "", kind: "execute" });
      })
      .catch(() => {});
    return () => {
      live = false;
    };
  }, [project, resultRun]);
  const receiveBinding = useCallback(
    (value: DatasetBinding, saved: boolean) => {
      setBinding(value);
      if (saved) {
        setCatalog(undefined);
        read(project, task)
          .then((c: any) => {
            setCfg(c);
            setProfile(c.profile);
            setProcessedName((old) => old || c.processed_name || c.profile?.dataset_id || "");
            setDirty(false);
            setNotice("数据绑定已保存，正在解析样本与字段");
          })
          .catch((e) => setError(e.message));
      }
    },
    [project, task],
  );
  const selection = useCallback((r: string, f: string[]) => {
    setRoot(r);
    setFiles(f);
  }, []);
  const raw = cfg?.rawprep;
  const legacy = !!raw?.extraction && raw.extraction.layout !== "fields";
  const choices: Choice[] = !raw
    ? []
    : raw.extraction?.layout === "fields"
      ? raw.extraction.entries.flatMap((e: any) =>
          e.outputs.map((o: any) => ({ name: o.name, ...o.members[0] })),
        )
      : (raw.save_fields || []).map((name: string) => ({
          name,
          source_field: name,
          components:
            profile?.outputs.find((o: any) => o.name === name)?.components || 1,
        }));
  function change(next: any) {
    setCfg((old: any) => ({ ...old, rawprep: next }));
    setDirty(true);
    setNotice("");
    requestKey.current = crypto.randomUUID();
  }
  function choose(next: Choice[], current = raw) {
    const standard = next.every(
      (c) =>
        c.name === c.source_field &&
        profile.outputs.some((o: any) => o.name === c.name),
    );
    const value = {
      ...current,
      save_fields: next.map((c) => c.name),
      statistics: {
        ...current.statistics,
        fields: (current.statistics?.fields || []).filter((n: string) =>
          next.some((c) => c.name === n),
        ),
        position_fields: (current.statistics?.position_fields || []).filter(
          (n: string) => next.some((c) => c.name === n),
        ),
      },
    };
    if (standard) delete value.extraction;
    else
      value.extraction = {
        layout: "fields",
        entries: [
          {
            id: "selected-fields",
            name: "逐场输出",
            source_selector: "dataset",
            outputs: next.map((c) => ({
              id: c.source_field,
              name: c.name,
              members: [
                {
                  source_field: c.source_field,
                  output_member: c.name,
                  components: c.components,
                },
              ],
            })),
          },
        ],
      };
    change(value);
  }
  function enabled(o: any, g = raw.geometry) {
    return (
      (!o.requires?.length ||
        o.requires.every(
          (k: string) => k in Object(g) || (Array.isArray(g) && g.includes(k)),
        )) &&
      (!o.requires_any?.length ||
        o.requires_any.some(
          (k: string) => k in Object(g) || (Array.isArray(g) && g.includes(k)),
        ))
    );
  }
  function isDerivedChoice(item: Choice) {
    return !!profile?.outputs.find(
      (output: any) =>
        output.requires?.length &&
        (output.source_field === item.source_field ||
          output.name === item.source_field ||
          output.name === item.name),
    );
  }
  function derivedChoices(g = raw.geometry): Choice[] {
    return (profile?.outputs || [])
      .filter(
        (item: any) =>
          item.requires?.length &&
          enabled(item, g) &&
          raw.sources.includes(item.domain),
      )
      .map((item: any) => {
        const existing = choices.find(
          (choice) =>
            choice.source_field === (item.source_field || item.name) ||
            choice.name === item.name,
        );
        return {
          name: existing?.name || item.name,
          source_field: item.source_field || item.name,
          components: item.components || 1,
        };
      });
  }
  function outputsOfGeometry(id: string) {
    const option = profile?.geometry?.find((item: any) => item.id === id);
    const declared = (
      Array.isArray(option?.output)
        ? option.output
        : option?.output
          ? [option.output]
          : []
    ).filter(Boolean);
    const items = profile?.outputs || [];
    if (declared.length) {
      return declared
        .map((name: string) =>
          items.find(
            (item: any) =>
              raw.sources.includes(item.domain) &&
              (item.name === name || item.source_field === name),
          ),
        )
        .filter(Boolean);
    }
    return items.filter(
      (item: any) =>
        raw.sources.includes(item.domain) &&
        item.requires?.length === 1 &&
        item.requires[0] === id,
    );
  }
  function renameDerived(source: string, name: string) {
    const next = name.trim().replace(/\.pt$/i, "");
    choose(
      choices.map((item) =>
        item.source_field === source || item.name === source
          ? { ...item, name: next || item.name }
          : item,
      ),
    );
  }
  function chooseExtracted(next: Choice[], current = raw) {
    choose(
      [...next.filter((item) => !isDerivedChoice(item)), ...derivedChoices(current.geometry)],
      current,
    );
  }
  const extracted = choices.filter((item) => !isDerivedChoice(item));
  function geometry(id: string, on: boolean) {
    const old = Array.isArray(raw.geometry)
      ? raw.geometry
      : Object.keys(raw.geometry);
    const option = profile.geometry.find((o: any) => o.id === id);
    const next = on
      ? [...old.filter((k: string) => !option.conflicts?.includes(k)), id]
      : old.filter((k: string) => k !== id);
    const filters = structuredClone(raw.filters);
    for (const f of profile.filters)
      if (f.requires?.some((k: string) => !next.includes(k)))
        filters[f.domain] = (filters[f.domain] || []).filter(
          (k: string) => k !== f.id,
        );
    const geometryValue = Object.fromEntries(
      next.map((k: string) => {
        const kept = Array.isArray(raw.geometry) ? undefined : raw.geometry[k];
        const defaults = Object.fromEntries(
          Object.entries(
            profile.geometry.find((item: any) => item.id === k)?.parameters || {},
          ).map(([key, param]: [string, any]) => [key, param.default]),
        );
        return [k, kept && Object.keys(kept).length ? kept : defaults];
      }),
    );
    choose(
      [
        ...choices.filter((c) => {
          if (isDerivedChoice(c)) return false;
          const def = profile.outputs.find((o: any) => o.name === c.source_field);
          return !def || enabled(def, next);
        }),
        ...derivedChoices(geometryValue),
      ],
      {
        ...raw,
        geometry: geometryValue,
        filters,
      },
    );
  }
  async function persist(force = false) {
    if (
      !force &&
      !dirty &&
      processedName.trim() === (cfg.processed_name || "")
    )
      return cfg;
    const name = processedName.trim();
    const current: any = await save(project, task, {
      revision: cfg.revision,
      rawprep: raw,
      ...(name ? { processed_name: name } : {}),
    });
    setCfg(current);
    if (current.processed_name) setProcessedName(current.processed_name);
    setDirty(false);
    return current;
  }
  async function refreshCatalog(revision = cfg?.revision) {
    if (!revision || binding?.status !== "valid") return;
    const current = ++generation.current;
    setCatalogBusy(true);
    try {
      const value: any = await datasetCatalog(project, task, {
        revision,
        sample_scope: { mode: "all", values: [] },
      });
      if (current === generation.current) {
        setCatalog(value);
      }
    } catch (e: any) {
      if (current === generation.current) setError(e.message);
    } finally {
      if (current === generation.current) setCatalogBusy(false);
    }
  }
  useEffect(() => {
    if (cfg?.revision && binding?.status === "valid")
      refreshCatalog(cfg.revision);
    return () => {
      generation.current++;
    };
  }, [cfg?.revision, binding?.revision, binding?.status]);
  function beginAction(kind: ActionKind) {
    const copy = ACTION_COPY[kind];
    setActiveAction(kind);
    setError("");
    setNotice("");
    setActivity({ status: copy.running, text: `[INFO] 开始${copy.verb}` });
    setProgress({ status: "running", text: "", kind });
    if (kind === "execute" || kind === "trial") setResultRun(undefined);
  }
  function finishAction(kind: ActionKind, status: "succeeded" | "failed", detail: string) {
    const copy = ACTION_COPY[kind];
    const label = status === "succeeded" ? copy.done : copy.fail;
    setActivity({ status: label, text: `[INFO] ${detail}` });
    setProgress((old: any) => ({
      ...(old || {}),
      status,
      kind,
      text: old?.text || "",
    }));
    if (status === "succeeded") setNotice(detail);
    else setError(detail);
  }
  async function action(kind: ActionKind | "save") {
    if (submitting.current) return;
    submitting.current = true;
    setBusy(true);
    if (kind !== "save") beginAction(kind);
    else {
      setError("");
      setNotice("");
    }
    try {
      const current = await persist(true);
      if (kind === "save") {
        setNotice("配置已保存，未创建新版本");
        return;
      }
      if (kind === "refresh") {
        await refreshCatalog(current.revision);
        finishAction(kind, "succeeded", "已按当前配置刷新样本与字段");
        return;
      }
      const sampleScope =
        scope.mode === "samples"
          ? { mode: "samples", values: scope.values }
          : { mode: "all", values: [] };
      const selectedCatalog: any = await datasetCatalog(project, task, {
        revision: current.revision,
        sample_scope: sampleScope,
      });
      if (selectedCatalog.errors?.length)
        throw Error(
          selectedCatalog.errors.map((e: any) => e.message).join("；"),
        );
      const body: any = {
        revision: current.revision,
        sample_scope: sampleScope,
        catalog_revision: selectedCatalog.revision,
        idempotency_key: requestKey.current,
      };
      if (kind === "check") {
        const result: any = await check(project, task, body);
        finishAction(
          kind,
          "succeeded",
          `校验通过：${result.sample_count} 个完整样本，${result.file_count} 个依赖文件`,
        );
      } else {
        const result: any = await (kind === "trial" ? trial : execute)(
          project,
          task,
          body,
        );
        setRun(result.id);
        setResultRun(result.id);
        setProgress({ status: result.status || "running", text: "", kind });
        setActivity({
          status: ACTION_COPY[kind].running,
          text: `[INFO] 已提交运行 ${result.id}`,
        });
        setNotice("已提交运行 " + result.id);
        requestKey.current = crypto.randomUUID();
      }
    } catch (e: any) {
      if (kind === "save") setError(e.message);
      else finishAction(kind, "failed", e.message);
    } finally {
      setBusy(false);
      submitting.current = false;
    }
  }
  if (!cfg || !profile)
    return error ? <Alert type="error" message={error} /> : <Spin />;
  const available = profile.outputs
    .filter((o: any) => raw.sources.includes(o.domain))
    .map((o: any) => {
      const actual = catalog?.fields?.find(
        (f: any) => f.field_id === o.raw_field || f.name === o.name,
      );
      return {
        ...o,
        dtype: actual?.dtype,
        unit: o.unit ?? actual?.unit,
        supported: actual?.supported ?? true,
      };
    });
  const scopeMode = scope.mode === "samples" ? "samples" : "all";
  const usableScope = scopeMode === "all" || scope.values.length > 0;
  const sampleCount =
    catalog?.samples.filter(
      (s: any) => scopeMode === "all" || scope.values.includes(s.key),
    ).length || 0;
  return (
    <>
      <div className="workbench-grid layout">
        <section className="data-panel bound-source-column" id="stage-handoff">
          <BoundDatasetFiles
            project={project}
            task={task}
            binding={binding}
            onBinding={receiveBinding}
            onSelection={selection}
            beforeSave={async () => (await persist()).revision}
            disabled={busy}
            run={resultRun}
            refresh={resultTick}
          />
        </section>
        <section className="settings-panel">
          <div className="panel-title">
            <b>处理设置</b>
            <Space>
              <Button
                disabled={busy}
                onClick={() => {
                  change(structuredClone(profile.defaults));
                  setNotice("已恢复案例默认，请保存配置");
                }}
              >
                恢复案例默认
              </Button>
              <Button disabled={!dirty || busy} onClick={() => action("save")}>
                保存配置
              </Button>
            </Space>
          </div>
          <div className="settings-body">
            <div className="processing-group setting">
              <h3>01　字段提取与保存</h3>
              <p>只配置从源文件提取的物理量或坐标；法向、SDF 等几何结果在下方派生项命名。</p>
              {catalogBusy && <Spin size="small" />}
              {!catalog && (
                <small>默认字段已显示，绑定后自动检查真实字段。</small>
              )}
              {catalog && (
                <small>
                  已检查 {catalog.inspection?.checked_samples?.length || 0}{" "}
                  个代表样本，执行前检查全部选中样本。
                </small>
              )}
              {legacy ? (
                <>
                  <Alert
                    type="info"
                    message="当前为历史字段容器，保持原有输出布局"
                  />
                  <div className="extraction-toolbar">
                    <Button
                      onClick={() =>
                        choose(
                          profile.outputs
                            .filter((o: any) => raw.save_fields?.includes(o.name))
                            .map((o: any) => ({
                              name: o.name,
                              source_field: o.name,
                              components: o.components,
                            })),
                        )
                      }
                    >
                      切换为逐场输出
                    </Button>
                    <small>已配置 {raw.extraction.entries.length} 个输出</small>
                  </div>
                  <div className="extraction-list" role="list" aria-label="字段提取配置">
                    {raw.extraction.entries.map((e: any) => (
                      <div className="extraction-card" role="listitem" key={e.id}>
                        <b title={e.name}>{e.name}</b>
                        <span className="extraction-meta">历史容器 · {(e.outputs || []).length} 个输出</span>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <>
                  <div className="extraction-toolbar">
                    <Button disabled={busy} onClick={() => setEntryEdit(null)}>
                      ＋ 添加字段提取
                    </Button>
                    <small title={`已配置 ${extracted.length} 个提取输出，格式固定 .pt`}>
                      {extracted.length} 个提取 · .pt
                    </small>
                  </div>
                  <div className="extraction-list" role="list" aria-label="字段提取配置">
                    {extracted.map((choice) => {
                      const meta =
                        profile.outputs.find(
                          (o: any) =>
                            o.name === choice.name ||
                            o.name === choice.source_field,
                        ) ||
                        available.find(
                          (o: any) =>
                            o.source_field === choice.source_field ||
                            o.name === choice.name,
                        );
                      const required = !!meta?.required;
                      const detail = [
                        meta?.domain,
                        meta?.association,
                        meta?.label || choice.source_field,
                        choice.components + " 分量",
                        required ? "必需" : "",
                      ]
                        .filter(Boolean)
                        .join(" · ");
                      return (
                        <div className="extraction-card" role="listitem" key={choice.name}>
                          <b title={choice.name + ".pt"}>{choice.name}.pt</b>
                          <span className="extraction-meta" title={detail}>{detail}</span>
                          <div className="extraction-actions">
                            <Button
                              type="text"
                              size="small"
                              disabled={busy}
                              icon={<EditOutlined />}
                              aria-label={"编辑 " + choice.name}
                              onClick={() => setEntryEdit(choice)}
                            />
                            <Button
                              type="text"
                              size="small"
                              danger
                              disabled={busy || required}
                              icon={<DeleteOutlined />}
                              aria-label={"删除 " + choice.name}
                              onClick={() =>
                                chooseExtracted(
                                  extracted.filter((c) => c.name !== choice.name),
                                )
                              }
                            />
                          </div>
                        </div>
                      );
                    })}
                    {!extracted.length && (
                      <p className="extraction-empty">尚未添加字段提取</p>
                    )}
                  </div>
                </>
              )}
            </div>
            <div className="setting">
              <h3>02　清洗与实体校验</h3>
              {profile.filters.length ? (
                profile.filters.map((f: any) => (
                  <p key={f.domain + f.id}>
                    <Checkbox
                      checked={raw.filters?.[f.domain]?.includes(f.id) || false}
                      disabled={
                        busy ||
                        f.requires?.some(
                          (k: string) => !enabled({ requires: [k] }),
                        )
                      }
                      onChange={(e) =>
                        change({
                          ...raw,
                          filters: {
                            ...raw.filters,
                            [f.domain]: e.target.checked
                              ? [...(raw.filters[f.domain] || []), f.id]
                              : (raw.filters[f.domain] || []).filter(
                                  (k: string) => k !== f.id,
                                ),
                          },
                        })
                      }
                    >
                      {f.label}
                    </Checkbox>
                  </p>
                ))
              ) : (
                <small>按数据集字段与实体契约校验，无额外清洗选项。</small>
              )}
            </div>
            <div className="setting">
              <h3>03　几何派生</h3>
              {profile.geometry.length ? (
                profile.geometry.map((g: any) => {
                  const on = Array.isArray(raw.geometry)
                    ? raw.geometry.includes(g.id)
                    : g.id in raw.geometry;
                  const outputs = outputsOfGeometry(g.id);
                  return (
                  <div className="geometry-row" key={g.id}>
                    <Checkbox
                      checked={on}
                      disabled={
                        busy ||
                        g.domains.some((d: string) => !raw.sources.includes(d))
                      }
                      onChange={(e) => geometry(g.id, e.target.checked)}
                    >
                      {g.label}
                    </Checkbox>
                    {!!outputs.length && (
                      <div className="geometry-names">
                        {outputs.map((item: any) => {
                          const current = choices.find(
                            (choice) =>
                              choice.source_field === (item.source_field || item.name) ||
                              choice.name === item.name,
                          );
                          return (
                            <Input
                              key={item.name}
                              size="small"
                              aria-label={"命名 " + (item.label || item.name)}
                              value={on ? current?.name || item.name : item.name}
                              disabled={busy || !on}
                              onChange={(e) =>
                                renameDerived(item.source_field || item.name, e.target.value)
                              }
                            />
                          );
                        })}
                      </div>
                    )}
                  </div>
                  );
                })
              ) : (
                <small>使用原始数据提供的几何字段。</small>
              )}
            </div>
            <div className="setting">
              <h3>04　落盘与交付</h3>
              {(profile.formats || ["pt", "zarr"]).map((item: string) => (
                <p key={item}>
                  <Checkbox
                    aria-label={item.toUpperCase()}
                    checked={selectedFormats(raw).includes(item)}
                    disabled={busy}
                    onChange={(e) => {
                      const next = e.target.checked
                        ? [...selectedFormats(raw), item]
                        : selectedFormats(raw).filter((v) => v !== item);
                      const value = { ...raw, formats: next };
                      delete value.format;
                      change(value);
                    }}
                  >
                    {item.toUpperCase()}
                  </Checkbox>
                </p>
              ))}
              {profile.vtkhdf && (
                <p>
                  <Checkbox
                    checked={raw.vtkhdf}
                    onChange={(e) =>
                      change({ ...raw, vtkhdf: e.target.checked })
                    }
                  >
                    VTKHDF · 网格与场关联
                  </Checkbox>
                </p>
              )}
            </div>
            <div className="setting">
              <h3>05　统计</h3>
              <Select
                aria-label="统计策略"
                value={raw.statistics.mode}
                options={profile.statistics_modes.map((v: string) => ({
                  value: v,
                  label: (
                    {
                      reference: "引用参考统计",
                      fit: "本次处理样本重算",
                      none: "不生成统计",
                    } as any
                  )[v],
                }))}
                onChange={(mode) =>
                  change({
                    ...raw,
                    statistics: {
                      ...raw.statistics,
                      mode,
                      fields:
                        mode === "fit"
                          ? choices.map((c) => c.name)
                          : raw.statistics.fields,
                    },
                  })
                }
              />
              <p>
                <small>
                  统计不包含未保存字段；新增或重命名字段请选择重算或不生成统计。
                </small>
              </p>
            </div>
          </div>
        </section>
        <section className="execution-panel">
          <div className="execution-head">
            <h2>执行配置</h2>
            <small>按数据集声明的样本名单处理，自动解析配套文件。</small>
          </div>
          <div className="executionbox">
            <label htmlFor="processed-dataset-name">平台数据集名称</label>
            <Input
              id="processed-dataset-name"
              aria-label="平台数据集名称"
              value={processedName}
              disabled={busy}
              placeholder="例如 shapenet_car 或 NASA_CRM"
              onChange={(e) => {
                setProcessedName(e.target.value);
                setDirty(true);
                setNotice("");
                requestKey.current = crypto.randomUUID();
              }}
            />
            <small>正式执行成功后，其他项目的数据准备可按此名称选用。</small>
            <h3>执行范围</h3>
            <Select
              aria-label="执行范围"
              value={scopeMode}
              options={[
                { value: "all", label: "全部声明样本" },
                { value: "samples", label: "指定样本" },
              ]}
              onChange={(mode) => {
                setScope({ mode, values: [] });
                requestKey.current = crypto.randomUUID();
              }}
            />
            {scopeMode === "samples" && (
              <Select
                mode="multiple"
                showSearch
                optionFilterProp="label"
                aria-label="执行样本选择"
                style={{ width: "100%" }}
                value={scope.values}
                options={(catalog?.samples || []).map((s: any) => ({
                  value: s.key,
                  label: s.sample_id,
                }))}
                onChange={(values) => {
                  setScope({ mode: "samples", values });
                  requestKey.current = crypto.randomUUID();
                }}
              />
            )}
            <small>不按 train/test 划分；分片在数据准备里选择。</small>
            <p>
              处理样本：<b>{sampleCount}</b> 个
            </p>
            <p>
              来源文件：{catalog?.sources?.length || 0} 个（按样本共享依赖）
            </p>
            <div className="runrow">
              <span>并行线程</span>
              <InputNumber
                aria-label="并行线程"
                min={1}
                max={64}
                precision={0}
                value={Number.isInteger(raw.workers) ? raw.workers : 1}
                disabled={busy}
                onChange={(value) => {
                  const workers =
                    Number.isInteger(value) && Number(value) >= 1
                      ? Number(value)
                      : 1;
                  change({ ...raw, workers });
                }}
              />
              <span>个</span>
            </div>
            <small>每个线程处理不同样本；1 为顺序执行。</small>
            <Button
              block
              type="primary"
              disabled={
                busy ||
                catalogBusy ||
                binding?.status !== "valid" ||
                !usableScope ||
                !processedName.trim() ||
                !selectedFormats(raw).length
              }
              loading={busy && activeAction === "execute"}
              onClick={() => action("execute")}
            >
              执行
            </Button>
            <Button
              block
              disabled={busy || binding?.status !== "valid"}
              loading={busy && activeAction === "refresh"}
              onClick={() => action("refresh")}
            >
              刷新样本与字段
            </Button>
            <Button
              block
              disabled={busy || !usableScope || binding?.status !== "valid"}
              loading={busy && activeAction === "check"}
              onClick={() => action("check")}
            >
              校验输入与配置
            </Button>
            <Button
              block
              disabled={busy || !usableScope || binding?.status !== "valid"}
              loading={busy && activeAction === "trial"}
              onClick={() => action("trial")}
            >
              按所选范围试跑
            </Button>
            {catalog?.errors?.length > 0 && (
              <Alert
                type="warning"
                message={`目录检查发现 ${catalog.errors.length} 项缺失，可修正来源或选择完整样本子集`}
              />
            )}
            {error && <Alert type="error" message={error} />}
            {notice && <Alert type="info" message={notice} />}
            {progress && <RawprepProgress snapshot={progress} />}
          </div>
        </section>
      </div>
      <ExecutionLog
        project={project}
        run={run}
        accumulate
        activity={activity}
        onSnapshot={(value) => {
          if (run !== resultRun) return;
          setProgress((old: any) => ({ ...value, kind: old?.kind || activeAction }));
          if (["succeeded", "failed", "stopped"].includes(value?.status)) {
            const kind = (activeAction || "execute") as ActionKind;
            const copy = ACTION_COPY[kind];
            setActivity({
              status:
                value.status === "succeeded"
                  ? copy.done
                  : value.status === "stopped"
                    ? "已停止"
                    : copy.fail,
            });
            if (value.status === "succeeded") setResultTick((n) => n + 1);
          }
        }}
      />
      {entryEdit !== undefined && (
        <FieldExtractionEditor
          project={project}
          task={task}
          root={
            root ||
            binding?.sources[binding?.binding_schema?.root_key || "root"]?.root ||
            ""
          }
          basePath={
            binding?.sources[binding?.binding_schema?.root_key || "root"]?.path ||
            ""
          }
          files={files}
          catalog={catalog}
          catalogBusy={catalogBusy}
          profile={profile}
          entry={entryEdit || undefined}
          onCancel={() => setEntryEdit(undefined)}
          onSave={(next) => {
            chooseExtracted(
              entryEdit
                ? extracted.map((c) => (c.name === entryEdit.name ? next : c))
                : [...extracted, next],
            );
            setEntryEdit(undefined);
          }}
        />
      )}
    </>
  );
}

function selectedFormats(raw: any): string[] {
  if (Array.isArray(raw?.formats) && raw.formats.length) return raw.formats;
  return raw?.format ? [raw.format] : ["pt"];
}

function parseSampleProgress(text = "") {
  const matches = [
    ...text.matchAll(/\[(?:[^\]]+\/)?批量前处理\/进度\][^\n]*完成=(\d+)[^\n]*总数=(\d+)/g),
  ];
  const last = matches.at(-1);
  return last ? { done: Number(last[1]), total: Number(last[2]) } : null;
}

/** 四个执行配置按钮共用进度条；没有完成数就不填百分比。 */
function RawprepProgress({
  snapshot,
}: {
  snapshot?: { status?: string; text?: string; kind?: ActionKind };
}) {
  const counts = parseSampleProgress(snapshot?.text);
  const status = snapshot?.status || "running";
  const kind = snapshot?.kind || "execute";
  const copy = ACTION_COPY[kind];
  const finished = ["succeeded", "failed", "stopped"].includes(status);
  const ratio =
    status === "succeeded"
      ? 100
      : counts && counts.total
        ? Math.min(100, Math.round((counts.done / counts.total) * 100))
        : null;
  const label =
    status === "succeeded"
      ? copy.done
      : status === "failed"
        ? copy.fail
        : status === "stopped"
          ? "已停止"
          : counts
            ? `${copy.running} ${counts.done}/${counts.total}`
            : copy.running;
  return (
    <section className="rawprep-progress" aria-label="处理进度">
      <div className="rawprep-progress-label">{label}</div>
      <div
        className={
          "rawprep-progress-track" + (ratio === null && !finished ? " indeterminate" : "")
        }
        role="progressbar"
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={ratio ?? undefined}
        aria-valuetext={label}
      >
        <div style={ratio === null ? undefined : { width: ratio + "%" }} />
      </div>
    </section>
  );
}
