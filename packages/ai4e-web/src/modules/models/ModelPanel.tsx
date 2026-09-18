import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Card, Input, InputNumber, Select, Table } from "antd";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { ConfigurationField } from "../../infrastructure/components/ConfigurationField";
import { fitModelGraphViewport } from "./graphViewport";
import { selectableGraphViews, selectedGraphMember } from "./graphViews";
import "./model.css";
const modelLabels: Record<string, string> = {
  abupt: "AB-UPT",
  transolver3: "Transolver-3",
};
const labels: Record<string, string> = {
  n_hidden: "隐藏层宽度",
  n_layers: "网络层数",
  n_head: "注意力头数",
  mlp_ratio: "前馈网络宽度倍率",
  slice_num: "切片数量",
  space_dim: "空间输入维度",
  fun_dim: "条件输入维度",
  out_dim: "预测输出维度",
  unified_pos: "统一位置编码",
  gradient_checkpointing: "梯度检查点",
  dim: "特征维度",
  depth: "网络深度",
  num_heads: "注意力头数",
  hidden_dim: "隐藏特征维度",
  num_blocks: "模块数量",
  seed: "随机种子",
  stride: "采样步长",
  chunk_count: "查询分块数",
  random_stream: "随机流",
  num_surface_inputs: "表面输入点数",
  num_surface_queries: "表面查询点数",
  num_volume_inputs: "体场输入点数",
  num_volume_queries: "体场查询点数",
  num_anchors: "锚点数量",
};
/** 模型配置与真实结构并列；采样与损失跟随当前模型字段，无对应配置则不展示，不提供权重加载。 */
export function ModelPanel({
  capabilities,
  values,
  onChange,
  trace,
  traceUrl,
  graphUrl,
  onTrace,
  busy,
  canTrace = true,
  bindings,
  modelOptions = [],
  presets = [],
  selectedCase,
  selectedVariant,
  selectedPreset,
  onModelChange,
  onVariantChange,
  onPresetChange,
  onExport,
  exportBusy,
  modelError,
  modelsLoading,
  onRetryModels,
  officialCombos = [],
  selectedCombo,
  comboLocked,
  onLoadCombo,
}: {
  capabilities?: any;
  values: any;
  onChange: (key: string, v: any) => void;
  trace: any;
  traceUrl?: string;
  graphUrl?: (member?: string) => string | undefined;
  onTrace: () => void;
  busy: boolean;
  canTrace?: boolean;
  bindings?: ReactNode;
  modelOptions?: any[];
  presets?: any[];
  selectedCase?: string;
  selectedVariant?: string;
  selectedPreset?: string;
  onModelChange?: (id: string) => void;
  onVariantChange?: (id: string) => void;
  onPresetChange?: (id?: string) => void;
  onExport?: (name: string) => void;
  exportBusy?: boolean;
  modelError?: string;
  modelsLoading?: boolean;
  onRetryModels?: () => void;
  officialCombos?: { id: string; name: string }[];
  selectedCombo?: string;
  comboLocked?: boolean;
  onLoadCombo?: (id: string) => void;
}) {
  const [graphHtml, setGraphHtml] = useState<string>();
  const [graphError, setGraphError] = useState<string>();
  const views = selectableGraphViews(trace?.result);
  const viewKey = views.map((item) => item.id + ":" + item.member).join("|");
  const [viewId, setViewId] = useState(
    () => String(trace?.result?.default_view || views[0]?.id || ""),
  );
  useEffect(() => {
    setViewId(String(trace?.result?.default_view || views[0]?.id || ""));
  }, [trace?.operation_id, trace?.result?.default_view, viewKey]);
  const graphMember = selectedGraphMember(trace?.result, viewId);
  const resolvedUrl = graphUrl?.(graphMember) || traceUrl;
  useEffect(() => {
    if (busy || !resolvedUrl) {
      setGraphHtml(undefined);
      setGraphError(undefined);
      return;
    }
    const controller = new AbortController();
    setGraphHtml(undefined);
    setGraphError(undefined);
    fetch(resolvedUrl, { signal: controller.signal })
      .then((response) => {
        if (!response.ok) throw new Error("结构图加载失败");
        return response.text();
      })
      .then((html) => {
        if (!controller.signal.aborted) setGraphHtml(fitModelGraphViewport(html));
      })
      .catch((error: Error) => {
        if (error.name !== "AbortError") setGraphError(error.message || "结构图加载失败");
      });
    return () => controller.abort();
  }, [resolvedUrl, busy]);
  const fetchingGraph = Boolean(!busy && resolvedUrl && !graphHtml && !graphError);
  const graphLoading = busy || fetchingGraph;
  const graphLoadingText = busy
    ? "正在生成模型结构…"
    : "正在载入结构图…";
  const currentView = views.find((item) => item.id === viewId);
  const graphNodes = currentView?.graph_nodes ?? trace?.result?.graph_nodes;
  const selectedModel = modelOptions.find((item) => item.id === selectedCase);
  const pickerOptions = modelOptions.length
    ? modelOptions.map((item) => ({
        value: item.id,
        label: item.name,
      }))
    : selectedCase
      ? [
          {
            value: selectedCase,
            label: modelLabels[selectedCase] || selectedCase,
          },
        ]
      : [];
  const [exportName, setExportName] = useState("");
  const losses = values.supervision?.length
    ? values.supervision
    : capabilities?.losses?.terms || [];
  const lossesLocked = capabilities?.losses?.configurable === false;
  const samplingConstraints = capabilities?.sampling?.constraints || {};
  const sampling: any[] = [];
  function walk(value: any, path: string[] = []) {
    for (const [key, child] of Object.entries(value || {})) {
      if (child && typeof child === "object" && !Array.isArray(child))
        walk(child, [...path, key]);
      else if (["string", "number", "boolean"].includes(typeof child))
        sampling.push({ path: [...path, key], value: child });
    }
  }
  walk(values.sampling);
  return (
    <div className="model-layout">
      <Card title="模型参数设置" className="model-settings">
        <details className="model-section" open>
          <summary>模型选择与版本</summary>
          <div className="model-section-body">
            <div className="model-picker">
              <label>模型类型</label>
              <Select
                aria-label="模型类型"
                value={selectedCase}
                placeholder={modelsLoading ? "正在加载可选择的模型" : "选择模型"}
                loading={modelsLoading}
                disabled={busy || Boolean(modelError) || !modelOptions.length}
                options={pickerOptions}
                onChange={onModelChange}
              />
              {officialCombos.length ? (
                <>
                  <label>数据集-模型组合</label>
                  <Select
                    aria-label="模型设置组合"
                    placeholder="选择官方配置"
                    value={selectedCombo}
                    disabled={busy || comboLocked}
                    options={officialCombos.map((item) => ({
                      value: item.id,
                      label: item.name,
                    }))}
                    onChange={(id) => onLoadCombo?.(id)}
                  />
                </>
              ) : null}
              {selectedModel?.variants?.length ? (
                <>
                  <label>应用变体</label>
                  <Select
                    aria-label="应用变体"
                    value={selectedVariant}
                    disabled={busy || modelsLoading}
                    options={selectedModel.variants.map((item: any) => ({
                      value: item.id,
                      label: item.name,
                    }))}
                    onChange={onVariantChange}
                  />
                </>
              ) : null}
              <label>已导出的模型配置</label>
              <Select
                allowClear
                aria-label="已导出的模型配置"
                value={selectedPreset}
                placeholder={
                  modelsLoading && !presets.length
                    ? "正在加载已导出配置"
                    : "未选用已导出配置"
                }
                disabled={busy || (modelsLoading && !presets.length)}
                options={presets.map((item: any) => ({
                  value: item.id,
                  label: item.name,
                }))}
                onChange={(value) => onPresetChange?.(value)}
              />
              <p className="model-field-help">
                本项目里用「导出模型配置」保存过的参数组合，不含权重。选中后只替换本页参数，点保存才写入任务。
              </p>
              <label>当前参数来源</label>
              <Select
                aria-label="当前参数来源"
                value={selectedModel?.structure_version?.id}
                disabled
                options={
                  selectedModel
                    ? [
                        {
                          value: selectedModel.structure_version.id,
                          label: selectedModel.structure_version.name,
                        },
                      ]
                    : []
                }
              />
              <p className="model-field-help">
                只表示当前模型参数来自官方案例默认，还是来自某份已导出的配置；此处不能切换。
              </p>
            </div>
            {modelError && (
              <Alert
                type="error"
                message="模型选项加载失败"
                description={modelError}
                action={
                  <Button onClick={onRetryModels} disabled={busy}>
                    重试模型选项
                  </Button>
                }
              />
            )}
            <div className="model-export">
              <Input
                aria-label="导出模型配置名称"
                placeholder="配置名称"
                value={exportName}
                disabled={busy || exportBusy}
                onChange={(e) => setExportName(e.target.value)}
              />
              <Button
                disabled={busy || exportBusy || !exportName.trim()}
                loading={exportBusy}
                onClick={() => onExport?.(exportName.trim())}
              >
                导出模型配置
              </Button>
            </div>
            <p>
              导出的是当前模型、训练和准备参数，不是权重文件。换模型将恢复目标官方预设或导出配置的训练默认值，并解除旧准备和权重选择；数据绑定与研究版本保持。
            </p>
          </div>
        </details>
        <details className="model-section" open>
          <summary>主干参数</summary>
          <div className="model-section-body">
            <div className="configuration-grid">
              {Object.entries(values.parameters || {})
                .filter(([, v]) =>
                  ["number", "string", "boolean"].includes(typeof v),
                )
                .map(([key, value]) => (
                  <ConfigurationField
                    key={key}
                    label={labels[key] || key}
                    help={key}
                    value={value}
                    onChange={(v) =>
                      onChange("parameters", { ...values.parameters, [key]: v })
                    }
                  />
                ))}
            </div>
          </div>
        </details>
        {Object.keys(values.data_specs?.domains || {}).length > 0 && (
          <details className="model-section" open>
            <summary>输入输出绑定</summary>
            <div className="model-section-body">
              {Object.entries(values.data_specs?.domains || {}).map(
                ([domain, definition]) => (
                  <div key={domain}>
                    <b>{domain}</b>
                    {Object.entries((definition as any).output_dims || {}).map(
                      ([field, dim]) => (
                        <ConfigurationField
                          key={field}
                          label={field + " 输出维度"}
                          value={dim}
                          onChange={(v) =>
                            onChange("data_specs", {
                              ...values.data_specs,
                              domains: {
                                ...values.data_specs.domains,
                                [domain]: {
                                  ...values.data_specs.domains[domain],
                                  output_dims: {
                                    ...values.data_specs.domains[domain]
                                      .output_dims,
                                    [field]: v,
                                  },
                                },
                              },
                            })
                          }
                        />
                      ),
                    )}
                  </div>
                ),
              )}
            </div>
          </details>
        )}
        <details className="model-section" open>
          <summary>学习目标与损失</summary>
          <div className="model-section-body">
            {lossesLocked ? (
              <p>
                固定等权 MSE
                {capabilities?.losses?.reason
                  ? ` · ${capabilities.losses.reason}`
                  : ""}
              </p>
            ) : null}
            {losses.length > 0 ? (
              <Table<any>
                rowKey="name"
                pagination={false}
                dataSource={losses}
                columns={[
                  { title: "目标字段", dataIndex: "target" },
                  {
                    title: "损失函数",
                    render: (_, row) => (
                      <Select
                        value={row.loss}
                        disabled={lossesLocked}
                        options={["mse", "mae", "huber", "relative_l2"].map(
                          (value) => ({ value, label: value }),
                        )}
                        onChange={(loss) =>
                          onChange(
                            "supervision",
                            losses.map((v: any) =>
                              v.name === row.name ? { ...v, loss } : v,
                            ),
                          )
                        }
                      />
                    ),
                  },
                  {
                    title: "权重",
                    render: (_, row) => (
                      <InputNumber
                        value={row.weight}
                        min={0}
                        disabled={lossesLocked}
                        onChange={(weight) =>
                          onChange(
                            "supervision",
                            losses.map((v: any) =>
                              v.name === row.name ? { ...v, weight } : v,
                            ),
                          )
                        }
                      />
                    ),
                  },
                ]}
              />
            ) : null}
          </div>
        </details>
        {sampling.length > 0 ? (
          <details className="model-section" open>
            <summary>模型采样</summary>
            <div className="model-section-body">
              <div className="sampling-grid">
                {sampling.map((row) => (
                  <ConfigurationField
                    key={row.path.join(".")}
                    label={row.path
                      .map((k: string) => labels[k] || k)
                      .join(" / ")}
                    help={"model.sampling." + row.path.join(".")}
                    value={row.value}
                    disabled={Boolean(
                      samplingConstraints[row.path.at(-1)]?.readOnly,
                    )}
                    onChange={(v) => {
                      const sample = structuredClone(values.sampling);
                      let node = sample;
                      row.path
                        .slice(0, -1)
                        .forEach((k: string) => (node = node[k]));
                      node[row.path.at(-1)] = v;
                      onChange("sampling", sample);
                    }}
                  />
                ))}
              </div>
            </div>
          </details>
        ) : null}
      </Card>
      <Card
        className="model-visualization"
        title="模型可视化"
        extra={
          <Button
            type="primary"
            loading={busy}
            disabled={!canTrace}
            onClick={onTrace}
          >
            生成真实模型结构
          </Button>
        }
      >
        {bindings}
        {views.length > 1 ? (
          <div className="model-graph-views" role="group" aria-label="结构图档位">
            {views.map((item) => (
              <Button
                key={item.id}
                type={item.id === viewId ? "primary" : "default"}
                disabled={busy}
                onClick={() => setViewId(item.id)}
              >
                {item.label}
              </Button>
            ))}
          </div>
        ) : null}
        <div
          className="model-graph-host"
          role="status"
          aria-live="polite"
          aria-busy={graphLoading}
        >
          {graphLoading ? (
            <>
              <p className="model-graph-status">{graphLoadingText}</p>
              <div className="model-graph-placeholder" aria-hidden="true">
                <span />
                <span />
                <span />
              </div>
            </>
          ) : resolvedUrl ? (
            <>
              <p>
                参数量 {trace?.result?.parameter_count?.toLocaleString()} ·{" "}
                {trace?.result?.model_type}
                {typeof graphNodes === "number"
                  ? ` · ${graphNodes.toLocaleString()} 个模块节点`
                  : ""}
              </p>
              <p className="model-graph-hint">
                滚轮缩放，拖动画布。官方两档结构图按宽度显示，按钮只切换已生成的页。
              </p>
              {graphError ? (
                <iframe
                  title="真实模型结构"
                  sandbox="allow-scripts"
                  src={resolvedUrl}
                />
              ) : graphHtml ? (
                <iframe
                  title="真实模型结构"
                  sandbox="allow-scripts"
                  srcDoc={graphHtml}
                />
              ) : (
                <div className="model-graph-placeholder" aria-hidden="true">
                  <span />
                  <span />
                  <span />
                </div>
              )}
            </>
          ) : (
            <div className="empty-record">
              TorchVista 模型结构
              <br />
              <small>
                {canTrace
                  ? "将按最近一次可用物理来源跟踪实际模型，一次生成阶段主干和阶段压缩块"
                  : "请先完成原始处理后再生成真实结构"}
              </small>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
