import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Checkbox, Input, InputNumber, Select, Table } from "antd";
import { type ReactNode, useState } from "react";
import { StageFiles } from "../files";
import "./trainprep.css";

const ROLE_LABELS: Record<string, string> = { position: "坐标", features: "特征", targets: "目标" };

/** 把模型或清单形状写成 (N, 3, 2, 3)；未知轴保留符号。 */
function formatShape(shape?: unknown, dim?: number) {
  const axes = Array.isArray(shape) && shape.length ? shape : dim != null ? ["N", dim] : null;
  return axes ? `(${axes.join(", ")})` : "—";
}

function asShape(item: any) {
  if (Array.isArray(item?.shape) && item.shape.length) return item.shape;
  return item?.dim != null ? ["N", item.dim] : null;
}

/** 点数轴可不同，其余特征轴必须一致。 */
function shapesCompatible(modelShape: unknown, dataShape: unknown) {
  if (!Array.isArray(modelShape) || !modelShape.length || !Array.isArray(dataShape) || !dataShape.length) return null;
  if (modelShape[0] === "N" || modelShape[0] === "n") {
    const tail = modelShape.slice(1);
    if (dataShape.length === tail.length && dataShape.every((axis, i) => axis === tail[i])) return true;
    return dataShape.length === tail.length + 1 && dataShape.slice(1).every((axis, i) => axis === tail[i]);
  }
  return modelShape.length === dataShape.length && modelShape.every((axis, i) => axis === dataShape[i]);
}

/** 从模型角色与数据集场构造匹配行；缺清单时仍展示已绑定名称。 */
function mappingRows(values: any, matching: any) {
  const roles = matching?.model_roles?.length
    ? matching.model_roles
    : Object.entries(values.domains || {}).flatMap(([domain, definition]) => {
        const d = definition as any;
        return [
          { id: domain + "/position", domain, role: "position", name: "position", shape: null, required: true },
          ...Object.entries(d.features || {}).map(([name]) => ({
            id: domain + "/features/" + name,
            domain,
            role: "features",
            name,
            shape: null,
            required: false,
          })),
          ...Object.entries(d.targets || {}).map(([name]) => ({
            id: domain + "/targets/" + name,
            domain,
            role: "targets",
            name,
            shape: null,
            required: true,
          })),
        ];
      });
  return roles.map((role: any) => {
    const selected =
      role.role === "position"
        ? values.domains?.[role.domain]?.position || ""
        : values.domains?.[role.domain]?.[role.role]?.[role.name] || "";
    const field = (matching?.dataset_fields || []).find(
      (item: any) => item.domain === role.domain && item.name === selected,
    ) || (selected ? { domain: role.domain, name: selected, shape: null } : null);
    const modelShape = asShape(role);
    const fieldShape = asShape(field);
    const compatible = shapesCompatible(modelShape, fieldShape);
    const match = !selected ? "empty" : compatible === false ? "mismatch" : compatible === null ? "unknown" : "ok";
    return { ...role, selected, modelShape, fieldShape, match };
  });
}

/** 按物理域归并，同一域只出现一次，不按角色列表的穿插顺序拆开。 */
function groupRows(rows: any[]) {
  const order: string[] = [];
  const grouped = new Map<string, any[]>();
  for (const row of rows) {
    if (!grouped.has(row.domain)) {
      grouped.set(row.domain, []);
      order.push(row.domain);
    }
    grouped.get(row.domain)!.push(row);
  }
  return order.map((domain) => ({ domain, rows: grouped.get(domain) || [] }));
}

function unifiedSpace(field: any) {
  return field.method === "coordinate" || field.unified_space;
}

function writeNormalization(
  onChange: (key: string, value: any) => void,
  values: any,
  name: string,
  method: string,
  unified: boolean,
  extra: Record<string, unknown> = {},
) {
  const field = {
    ...values.normalization.fields[name],
    ...extra,
    method: unified ? "coordinate" : method,
  };
  delete field.unified_space;
  onChange("normalization", {
    ...values.normalization,
    fields: {
      ...values.normalization.fields,
      [name]: field,
    },
  });
}

function parseSampleProgress(text = "") {
  const matches = [
    ...text.matchAll(/\[(?:[^\]]+\/)?批量前处理\/进度\][^\n]*完成=(\d+)[^\n]*总数=(\d+)/g),
  ];
  const last = matches.at(-1);
  return last ? { done: Number(last[1]), total: Number(last[2]) } : null;
}

function PrepProgress({ snapshot }: { snapshot?: { status?: string; text?: string } }) {
  const counts = parseSampleProgress(snapshot?.text);
  const status = snapshot?.status || "running";
  const finished = ["succeeded", "failed", "stopped"].includes(status);
  const ratio =
    status === "succeeded"
      ? 100
      : counts && counts.total
        ? Math.min(100, Math.round((counts.done / counts.total) * 100))
        : null;
  const label =
    status === "succeeded"
      ? "已完成"
      : status === "failed"
        ? "失败"
        : status === "stopped"
          ? "已停止"
          : counts
            ? `处理中 ${counts.done}/${counts.total}`
            : "处理中";
  return (
    <section className="rawprep-progress" aria-label="处理进度">
      <div className="rawprep-progress-label">{label}</div>
      <div
        className={"rawprep-progress-track" + (ratio === null && !finished ? " indeterminate" : "")}
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

/** 数据准备三栏：模型角色与物理场下拉匹配，统计与采样不手填。 */
export function PreparationPanel({
  project,
  task,
  values,
  onChange,
  bindings,
  onExecute,
  onCheck,
  onSave,
  onLoadCombo,
  busy,
  dirty,
  resultRun,
  inputAsset,
  datasetName,
  capabilities,
  emptyHint,
  progress,
}: {
  project: string;
  task: string;
  values: any;
  onChange: (key: string, v: any) => void;
  bindings: ReactNode;
  onExecute: () => void;
  onCheck: () => void;
  onSave: () => void;
  onLoadCombo?: (caseId: string) => void;
  busy: boolean;
  dirty: boolean;
  run?: string;
  resultRun?: string;
  inputAsset?: any;
  datasetName?: string;
  capabilities?: any;
  emptyHint?: string;
  progress?: { status?: string; text?: string };
}) {
  const [view, setView] = useState<"datasets" | "results">("datasets");
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const matching = capabilities?.field_matching;
  const rows = mappingRows(values, matching);
  function assign(row: any, field?: string) {
    const domains = structuredClone(values.domains || {});
    domains[row.domain] ||= { position: "", features: {}, targets: {} };
    if (row.role === "position") domains[row.domain].position = field || "";
    else {
      domains[row.domain][row.role] ||= {};
      if (field) domains[row.domain][row.role][row.name] = field;
      else delete domains[row.domain][row.role][row.name];
    }
    onChange("domains", domains);
  }
  const sampling = values.sampling || values.sample || {};
  const splitCap = capabilities?.split;
  const splitDefaults = splitCap?.defaults || { train: 0, test: 0, eval: 0 };
  const splitCounts = {
    train: Number(values.split?.counts?.train ?? splitDefaults.train ?? 0),
    test: Number(values.split?.counts?.test ?? splitDefaults.test ?? 0),
    eval: Number(values.split?.counts?.eval ?? splitDefaults.eval ?? 0),
  };
  const splitMethod = values.split?.method || "original";
  const splitSeed = Number(values.split?.seed ?? 0);
  const scopeSamples = Array.isArray(values.split?.samples) ? values.split.samples : null;
  const scopeMode = scopeSamples ? "samples" : "all";
  const splitTotal = scopeSamples ? scopeSamples.length : Number(splitCap?.total ?? 0);
  const splitSum = splitCounts.train + splitCounts.test + splitCounts.eval;
  const splitInvalid =
    (scopeMode === "samples" && !scopeSamples?.length) ||
    (splitTotal > 0 &&
      (splitSum !== splitTotal || splitCounts.train < 1 || (splitMethod !== "original" && splitMethod !== "random")));
  function writeSplit(next: {
    method?: string;
    seed?: number;
    counts?: { train: number; test: number; eval: number };
    samples?: string[] | null;
  }) {
    const method = next.method ?? splitMethod;
    const counts = next.counts ?? splitCounts;
    const samples = next.samples === undefined ? scopeSamples : next.samples;
    onChange("split", {
      method,
      seed: next.seed ?? splitSeed,
      counts: method === "original" && !samples ? { ...splitDefaults } : counts,
      ...(samples == null ? {} : { samples }),
    });
  }
  return (
    <div className="prepare-layout prep-layout preparation-layout">
      <section className="prep-panel">
        <div className="prep-head">
          <div className="prep-tabs" role="tablist" aria-label="数据准备视图">
            <button type="button" role="tab" aria-selected={view === "datasets"} className={view === "datasets" ? "active" : ""} onClick={() => setView("datasets")}>
              数据集
            </button>
            <button type="button" role="tab" aria-selected={view === "results"} className={view === "results" ? "active" : ""} onClick={() => setView("results")}>
              处理结果
            </button>
          </div>
          <div className="dataset-caption">
            <span>已处理的数据集，用于数据准备和模型训练。</span>
          </div>
        </div>
        <div className="prep-files">
          {view === "datasets" ? bindings : null}
          <StageFiles
            project={project}
            task={task}
            role={view === "datasets" ? "inputs" : "preparation"}
            asset={view === "datasets" ? inputAsset : undefined}
            run={view === "results" ? resultRun : undefined}
            emptyHint={
              view === "datasets"
                ? emptyHint
                : resultRun
                  ? undefined
                  : "准备运行完成后在此查看产物"
            }
          />
        </div>
      </section>
      <section className="prep-panel">
        <div className="prep-head">
          <div className="prep-head-title">
            <h2>处理方法</h2>
            <Button onClick={onSave} disabled={busy} loading={busy}>
              保存配置
            </Button>
          </div>
          <small>左侧是模型输入，右侧是数据集字段；同域且张量形状相容才可匹配。</small>
          {capabilities?.preparation_combos?.options?.length ? (
            <label className="prep-combo">
              数据集-模型组合
              <Select
                aria-label="数据准备组合"
                value={capabilities.preparation_combos.current_id || undefined}
                disabled={busy}
                options={capabilities.preparation_combos.options.map((item: any) => ({
                  value: item.id,
                  label: item.name,
                }))}
                onChange={(id) => onLoadCombo?.(id)}
              />
            </label>
          ) : null}
        </div>
        <div className="prep-methods">
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, mapping: !old.mapping }))}>
                {collapsed.mapping ? "›" : "⌄"} 字段配置与映射
              </button>
              <small>{matching?.source === "manifest" ? "形状来自已绑定物理清单" : "尚未绑定清单时用案例声明的场与形状"}</small>
            </div>
            {collapsed.mapping ? null : (
              <div className="prep-bind-list">
                <div className="prep-bind-legend">
                  <span className="prep-bind-legend-model">模型输入</span>
                  <span className="prep-bind-legend-data">数据集字段</span>
                </div>
                {groupRows(rows).map(({ domain, rows: group }) => (
                  <section key={domain} className="prep-bind-group">
                    <header className="prep-bind-domain">{domain}</header>
                    {group.map((r: any) => {
                      const options = [
                        ...(matching?.dataset_fields || []).filter((item: any) => item.domain === r.domain),
                        ...(r.selected && !(matching?.dataset_fields || []).some((item: any) => item.domain === r.domain && item.name === r.selected)
                          ? [{ domain: r.domain, name: r.selected, shape: r.fieldShape }]
                          : []),
                      ];
                      return (
                        <article key={r.id} className={`prep-bind prep-bind-${r.match}`}>
                          <span className="prep-bind-role">{ROLE_LABELS[r.role] || r.role}</span>
                          <div className="prep-bind-model">
                            <span className="prep-bind-name">{r.name}</span>
                            <code className="prep-shape">{formatShape(r.modelShape)}</code>
                          </div>
                          <span className={`prep-match prep-match-${r.match}`} aria-label={r.id + "-match"}>
                            {r.match === "ok" ? "=" : r.match === "mismatch" ? "≠" : r.match === "empty" ? "→" : "?"}
                          </span>
                          <Select
                            allowClear
                            aria-label={r.id}
                            placeholder="选择物理场"
                            value={r.selected || undefined}
                            popupMatchSelectWidth={false}
                            options={options.map((item: any) => {
                              const shape = asShape(item);
                              return {
                                value: item.name,
                                label: (
                                  <span className="prep-option">
                                    <span>{item.name}</span>
                                    <code>{formatShape(shape)}</code>
                                  </span>
                                ),
                                disabled: shapesCompatible(r.modelShape, shape) === false,
                              };
                            })}
                            onChange={(field) => assign(r, field)}
                          />
                        </article>
                      );
                    })}
                  </section>
                ))}
              </div>
            )}
          </section>
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, split: !old.split }))}>
                {collapsed.split ? "›" : "⌄"} 训练分片
              </button>
              <small>全部已处理样本重新划分；官方名单不改，结果写入这次准备记录。</small>
            </div>
            {collapsed.split ? null : (
              <div className="prep-split">
                <div className="prep-split-grid">
                  <label className="prep-split-field">
                    <span>全部样本</span>
                    <InputNumber aria-label="全部样本数" value={splitTotal} disabled />
                  </label>
                  <label className="prep-split-field">
                    <span>训练</span>
                    <InputNumber
                      aria-label="训练分片数量"
                      min={0}
                      value={splitCounts.train}
                      disabled={!splitTotal}
                      onChange={(value) =>
                        writeSplit({
                          method: "random",
                          counts: { ...splitCounts, train: Number(value ?? 0) },
                        })
                      }
                    />
                  </label>
                  <label className="prep-split-field">
                    <span>测试</span>
                    <InputNumber
                      aria-label="测试分片数量"
                      min={0}
                      value={splitCounts.test}
                      disabled={!splitTotal}
                      onChange={(value) =>
                        writeSplit({
                          method: "random",
                          counts: { ...splitCounts, test: Number(value ?? 0) },
                        })
                      }
                    />
                  </label>
                  <label className="prep-split-field">
                    <span>评价</span>
                    <InputNumber
                      aria-label="评价分片数量"
                      min={0}
                      value={splitCounts.eval}
                      disabled={!splitTotal}
                      onChange={(value) =>
                        writeSplit({
                          method: "random",
                          counts: { ...splitCounts, eval: Number(value ?? 0) },
                        })
                      }
                    />
                  </label>
                </div>
                <div className="prep-split-grid">
                  <label className="prep-split-field">
                    <span>抽取方法</span>
                    <Select
                      aria-label="抽取方法"
                      value={splitMethod}
                      disabled={!splitTotal}
                      options={[
                        { value: "original", label: "保持原划分" },
                        { value: "random", label: "随机" },
                      ]}
                      onChange={(method) => writeSplit({ method })}
                    />
                  </label>
                  {splitMethod === "random" ? (
                    <label className="prep-split-field">
                      <span>随机种子</span>
                      <InputNumber
                        aria-label="分片随机种子"
                        value={splitSeed}
                        disabled={!splitTotal}
                        onChange={(value) => writeSplit({ seed: Number(value ?? 0) })}
                      />
                    </label>
                  ) : null}
                </div>
                {splitInvalid ? (
                  <p className="prep-split-error" role="alert">
                    {splitCounts.train < 1
                      ? "训练分片至少需要 1 个样本。"
                      : `三个分片数量之和必须等于全部样本 ${splitTotal}。`}
                  </p>
                ) : (
                  <p className="prep-note">test / eval 可为 0。数据转换只拟合训练分片。</p>
                )}
              </div>
            )}
          </section>
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, norm: !old.norm }))}>
                {collapsed.norm ? "›" : "⌄"} 数据转换
              </button>
              <small>先归一化，再乘 scale；统计仅由训练分片拟合，均值、方差、极值不可手工填写。</small>
            </div>
            {collapsed.norm ? null : <Table
              size="small"
              pagination={false}
              rowKey="name"
              dataSource={Object.entries(values.normalization?.fields || {}).map(([name, field]) => ({ name, ...(field as any) }))}
              columns={[
                { title: "字段名称", dataIndex: "name" },
                {
                  title: "归一化方法",
                  render: (_, r) => (
                    <Select
                      aria-label={"归一化方法 " + r.name}
                      value={r.method === "coordinate" ? "minmax" : r.method}
                      disabled={Boolean(unifiedSpace(r))}
                      options={["identity", "zscore", "minmax"].map((v) => ({
                        value: v,
                        label: v === "identity" ? "恒等" : v === "zscore" ? "标准化" : "最小最大",
                      }))}
                      onChange={(method) =>
                        writeNormalization(onChange, values, r.name, method, unifiedSpace(r))
                      }
                    />
                  ),
                },
                {
                  title: "统一空间",
                  render: (_, r) => (
                    <Checkbox
                      aria-label={"统一空间 " + r.name}
                      checked={unifiedSpace(r)}
                      onChange={(e) =>
                        writeNormalization(
                          onChange,
                          values,
                          r.name,
                          r.method === "coordinate" ? "minmax" : r.method,
                          e.target.checked,
                        )
                      }
                    />
                  ),
                },
                {
                  title: "scale",
                  render: (_, r) => (
                    <InputNumber
                      aria-label={"scale " + r.name}
                      value={r.scale ?? 1}
                      min={Number.MIN_VALUE}
                      onChange={(value) =>
                        writeNormalization(
                          onChange,
                          values,
                          r.name,
                          r.method === "coordinate" ? "minmax" : r.method,
                          unifiedSpace(r),
                          { scale: value == null ? 1 : value },
                        )
                      }
                    />
                  ),
                },
              ]}
            />}
          </section>
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, sample: !old.sample }))}>
                {collapsed.sample ? "›" : "⌄"} 采样策略
              </button>
              <small>采样在模型设置中配置；此处只读冻结声明。</small>
            </div>
            {collapsed.sample ? null : (
              <p className="prep-readonly">{sampling.method || sampling.mode || "由模型设置写入准备记录，本页不提供采样编辑。"}</p>
            )}
          </section>
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, delivery: !old.delivery }))}>
                {collapsed.delivery ? "›" : "⌄"} 落盘与交付
              </button>
              <small>准备记录保存生效采样声明，过期记录不能被训练复用。</small>
            </div>
            {collapsed.delivery ? null : (
              <label className="prep-check">
                <Checkbox
                  checked={values.normalization?.materialize !== false}
                  onChange={(e) => onChange("normalization", { ...values.normalization, materialize: e.target.checked })}
                >
                  保存归一化副本
                </Checkbox>
              </label>
            )}
          </section>
        </div>
      </section>
      <section className="prep-panel prep-execution">
        <h2>执行配置</h2>
        <small>按已选平台数据集的样本名单准备，划分在中栏设置。</small>
        <label htmlFor="prep-dataset-name">平台数据集名称</label>
        <Input
          id="prep-dataset-name"
          aria-label="平台数据集名称"
          value={datasetName || ""}
          disabled
          placeholder="请先在左侧选择平台数据集"
        />
        <h3>执行范围</h3>
        <Select
          aria-label="执行范围"
          value={scopeMode}
          disabled={!inputAsset}
          options={[
            { value: "all", label: "全部已处理样本" },
            { value: "samples", label: "指定样本" },
          ]}
          onChange={(mode) =>
            writeSplit({
              method: mode === "samples" ? "random" : "original",
              samples: mode === "samples" ? [] : null,
              counts: mode === "samples" ? { train: 0, test: 0, eval: 0 } : splitDefaults,
            })
          }
        />
        {scopeMode === "samples" ? (
          <Select
            mode="multiple"
            showSearch
            optionFilterProp="label"
            aria-label="执行样本选择"
            disabled={!inputAsset}
            value={scopeSamples || []}
            options={(splitCap?.samples || []).map((item: any) => ({
              value: item.id,
              label: item.id,
            }))}
            onChange={(samples) =>
              writeSplit({
                method: "random",
                samples,
                counts: { train: samples.length, test: 0, eval: 0 },
              })
            }
          />
        ) : null}
        <p className="prep-note">
          处理样本：<b>{splitTotal}</b> 个。train / test / eval 在中栏划分。
        </p>
        <p className="prep-note">并行线程：1</p>
        <Button className="prep-run" type="primary" loading={busy} disabled={busy || !inputAsset || splitInvalid} onClick={onExecute}>
          ▶ 执行
        </Button>
        {!inputAsset ? (
          <p className="prep-note">请先选择平台数据集再执行。</p>
        ) : splitInvalid ? (
          <p className="prep-note">
            {scopeMode === "samples" && !scopeSamples?.length
              ? "请选择至少一个已处理样本。"
              : "请先把训练、测试和评价数量加总为执行范围内的样本，且训练至少 1 个。"}
          </p>
        ) : (
          <p className="prep-note">输入不匹配时拒绝复用准备记录。</p>
        )}
        <Button disabled={busy} loading={busy} onClick={onCheck}>
          检查配置与交接
        </Button>
        {resultRun && <PrepProgress snapshot={progress} />}
      </section>
    </div>
  );
}
