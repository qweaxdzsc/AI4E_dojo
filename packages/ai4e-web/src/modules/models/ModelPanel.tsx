import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Card, Input, InputNumber, Select, Table } from "antd";
import type { ReactNode } from "react";
import { useState } from "react";
import { ConfigurationField } from "../../infrastructure/components/ConfigurationField";
import "./model.css";
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
}: {
  capabilities?: any;
  values: any;
  onChange: (key: string, v: any) => void;
  trace: any;
  traceUrl?: string;
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
}) {
  const selectedModel = modelOptions.find((item) => item.id === selectedCase);
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
                placeholder="选择模型"
                loading={modelsLoading}
                disabled={busy || modelsLoading || Boolean(modelError)}
                options={modelOptions.map((item) => ({
                  value: item.id,
                  label: item.name,
                }))}
                onChange={onModelChange}
              />
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
              <label>我保存的模型</label>
              <Select
                allowClear
                aria-label="我保存的模型"
                value={selectedPreset}
                placeholder="未使用导出预设"
                disabled={busy || modelsLoading}
                options={presets.map((item: any) => ({
                  value: item.id,
                  label: item.name,
                }))}
                onChange={(value) => onPresetChange?.(value)}
              />
              <label>结构版本</label>
              <Select
                aria-label="结构版本"
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
                aria-label="导出模型名称"
                placeholder="导出名称"
                value={exportName}
                disabled={busy || exportBusy}
                onChange={(e) => setExportName(e.target.value)}
              />
              <Button
                disabled={busy || exportBusy || !exportName.trim()}
                loading={exportBusy}
                onClick={() => onExport?.(exportName.trim())}
              >
                导出模型
              </Button>
            </div>
            <p>
              换模型将恢复目标官方预设或导出配置的训练默认值，并解除旧准备和权重选择；数据绑定与研究版本保持。
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
        {trace && traceUrl ? (
          <>
            <p>
              参数量 {trace.result.parameter_count?.toLocaleString()} ·{" "}
              {trace.result.model_type}
            </p>
            <iframe
              title="真实模型结构"
              sandbox="allow-scripts"
              src={traceUrl}
            />
          </>
        ) : (
          <div className="empty-record">
            TorchVista 模型结构
            <br />
            <small>
              {canTrace
                ? "将按最近一次可用物理来源跟踪实际模型"
                : "请先完成原始处理后再生成真实结构"}
            </small>
          </div>
        )}
      </Card>
    </div>
  );
}
