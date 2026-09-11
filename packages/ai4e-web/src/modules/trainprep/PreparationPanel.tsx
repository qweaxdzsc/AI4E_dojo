import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Checkbox, Input, InputNumber, Select, Table } from "antd";
import { type ReactNode, useState } from "react";
import { FileBrowser } from "../files";
import "./trainprep.css";

/** 数据准备三栏对照细节原型：数据集页签、处理方法卡、执行盒。 */
export function PreparationPanel({
  project,
  task,
  values,
  onChange,
  bindings,
  onExecute,
  onCheck,
  onSave,
  busy,
  dirty,
}: {
  project: string;
  task: string;
  values: any;
  onChange: (key: string, v: any) => void;
  bindings: ReactNode;
  onExecute: () => void;
  onCheck: () => void;
  onSave: () => void;
  busy: boolean;
  dirty: boolean;
}) {
  const [view, setView] = useState<"datasets" | "results">("datasets");
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({});
  const rows = Object.entries(values.domains || {}).flatMap(([domain, definition]) => {
    const d = definition as any;
    return [
      { id: domain + "/position", domain, role: "position", field: d.position },
      ...Object.entries(d.features || {}).map(([name, field]) => ({
        id: domain + "/features/" + name,
        domain,
        role: "features",
        name,
        field,
      })),
      ...Object.entries(d.targets || {}).map(([name, field]) => ({
        id: domain + "/targets/" + name,
        domain,
        role: "targets",
        name,
        field,
      })),
    ];
  });
  function update(row: any, field: string) {
    const domains = structuredClone(values.domains);
    if (row.role === "position") domains[row.domain].position = field;
    else domains[row.domain][row.role][row.name] = field;
    onChange("domains", domains);
  }
  const sampling = values.sampling || values.sample || {};
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
          <FileBrowser project={project} task={task} compact />
        </div>
      </section>
      <section className="prep-panel">
        <div className="prep-head">
          <div className="prep-head-title">
            <h2>处理方法</h2>
            <Button onClick={onSave} disabled={!dirty} loading={busy}>
              保存配置
            </Button>
          </div>
          <small>配置数据准备的各项处理方法，完成字段映射、归一化与落盘配置。</small>
        </div>
        <div className="prep-methods">
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, mapping: !old.mapping }))}>
                {collapsed.mapping ? "›" : "⌄"} 字段配置与映射
              </button>
              <div className="controls">
                <Button
                  onClick={() => {
                    const name = Object.keys(values.domains || {})[0];
                    if (!name) return;
                    const domains = structuredClone(values.domains);
                    domains[name].targets = {
                      ...domains[name].targets,
                      ["field_" + Object.keys(domains[name].targets || {}).length]: "",
                    };
                    onChange("domains", domains);
                  }}
                >
                  ＋ 增加字段
                </Button>
              </div>
            </div>
            {collapsed.mapping ? null : <Table
              size="small"
              pagination={false}
              rowKey="id"
              dataSource={rows}
              columns={[
                { title: "数据域", dataIndex: "domain" },
                { title: "用途", dataIndex: "role" },
                {
                  title: "字段",
                  render: (_, r) => <Input aria-label={r.id} value={r.field} onChange={(e) => update(r, e.target.value)} />,
                },
                {
                  title: "操作",
                  render: (_, r) =>
                    r.role !== "position" && (
                      <button
                        type="button"
                        className="prep-delete"
                        onClick={() => {
                          const domains = structuredClone(values.domains);
                          delete domains[r.domain][r.role][(r as any).name];
                          onChange("domains", domains);
                        }}
                      >
                        删除
                      </button>
                    ),
                },
              ]}
            />}
          </section>
          <section className="prep-section">
            <div className="section-title">
              <button type="button" className="headingtoggle" onClick={() => setCollapsed((old) => ({ ...old, norm: !old.norm }))}>
                {collapsed.norm ? "›" : "⌄"} 归一化与转换
              </button>
              <small>统计仅由训练分片拟合，均值、方差、极值不可手工填写。</small>
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
                      value={r.method}
                      options={["identity", "zscore", "minmax", "coordinate"].map((v) => ({
                        value: v,
                        label: v === "coordinate" ? "Min-Max（兼容坐标）" : v,
                      }))}
                      onChange={(method) =>
                        onChange("normalization", {
                          ...values.normalization,
                          fields: { ...values.normalization.fields, [r.name]: { ...values.normalization.fields[r.name], method } },
                        })
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
                  checked={values.normalization?.materialize}
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
        <small>确认配置无误后，启动数据准备处理任务。</small>
        <label htmlFor="prep-exec-count">执行数量</label>
        <InputNumber id="prep-exec-count" aria-label="执行数量" min={1} value={1} disabled />
        <label className="checkrow">
          <Checkbox checked disabled>
            执行全部
          </Checkbox>
          <span>
            执行全部<small>准备消费已选物理清单，不按示意文件数截取。</small>
          </span>
        </label>
        <Button className="prep-run" type="primary" loading={busy} disabled={dirty} onClick={onExecute}>
          ▶ 执行
        </Button>
        <p className="prep-note">输入不匹配时拒绝复用准备记录。并行线程固定为 1。</p>
        <Button disabled={dirty} loading={busy} onClick={onCheck}>
          检查配置与交接
        </Button>
      </section>
    </div>
  );
}
