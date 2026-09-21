import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Card, Checkbox, Radio, Select } from "antd";
import { ConfigurationField } from "../../infrastructure/components/ConfigurationField";
import "./training.css";

const labels: Record<string, string> = {
  validation_interval: "验证间隔",
  validation_unit: "评估间隔单位",
  loss_x_axis: "Loss 横轴",
  parameter_group_policy: "参数分组策略",
  scheduler_unit: "调度更新单位",
  min_lr_ratio: "最小学习率比例",
  snapshot: "保存代码快照",
  log_every_updates: "更新日志间隔",
  optimizer: "优化器",
  learning_rate: "学习率",
  weight_decay: "权重衰减",
  precision: "训练精度",
  accumulate: "梯度累积",
  gradient_clip: "梯度裁剪",
  scheduler: "学习率调度",
  warmup_ratio: "预热比例",
  min_lr: "最小学习率",
  max_epochs: "训练轮数",
  batch_size: "批次大小",
  device: "执行设备",
  num_workers: "数据加载进程",
  ema_decay: "EMA 衰减",
  ema_save_every: "EMA 保存周期",
  log_every: "日志轮次间隔",
  test_repeat: "测试重复评估次数",
  evaluation_split: "测试分片",
  evaluation_enabled: "启用测试评估",
  export_predictions: "写出预测",
  export_vtk: "写出网格",
  export_split: "写出分片",
  training_split: "训练切片",
  save_on_interrupt: "中断保存检查点",
};

const SLICE_ORDER = ["train", "test", "eval"] as const;
const SLICE_LABELS: Record<string, string> = {
  train: "训练集",
  test: "测试集",
  eval: "评价集",
};

function normalizeSlice(name: string | undefined) {
  if (name === "validation") return "eval";
  return SLICE_ORDER.includes(name as (typeof SLICE_ORDER)[number]) ? name : "train";
}

function preparationSlices(item: any) {
  const listed = Array.isArray(item?.slices) ? item.slices : null;
  return SLICE_ORDER.map((name) => {
    const row = listed?.find((slice: any) => slice?.name === name);
    return {
      name,
      label: String(row?.label || SLICE_LABELS[name]),
      count: listed ? Number(row?.count ?? 0) : null,
      method: row?.method,
      seed: row?.seed,
    };
  });
}

function sliceOptionLabel(slice: { label: string; count: number | null }) {
  return slice.count == null ? slice.label : `${slice.label}（${slice.count}）`;
}

function preparedDatasetLabel(item: any) {
  const name = String(item?.processed_name || "").trim();
  if (name) return name;
  const fallback = String(item?.name || "").trim();
  if (fallback && !/\.json$/i.test(fallback) && fallback !== "已绑定来源不可用")
    return fallback;
  return "未命名数据集";
}

function checkpointLabel(item: any) {
  return (item.run_id?.slice(0, 8) || "固定来源") + " / " + (item.name || "检查点");
}

/** 训练设置按优化、控制、EMA、诊断及开训选择分组，只呈现已有配置能力。 */
export function TrainingPanel({
  capabilities,
  values,
  onChange,
  onCheck,
  onSave,
  onStart,
  busy,
  officialCombos = [],
  selectedCombo,
  onLoadCombo,
  preparations = [],
  selectedPreparation,
  onPreparation,
  checkpoints = [],
  selectedCheckpoint,
  onCheckpoint,
  trainMode = "restart",
  onTrainMode,
}: {
  capabilities?: any;
  values: any;
  onChange: (key: string, v: any) => void;
  onCheck: () => void;
  onSave: () => void;
  onStart: () => void;
  busy: boolean;
  officialCombos?: { id: string; name: string }[];
  selectedCombo?: string;
  onLoadCombo?: (id: string) => void;
  preparations?: any[];
  selectedPreparation?: any;
  onPreparation?: (ref: any) => void;
  checkpoints?: any[];
  selectedCheckpoint?: any;
  onCheckpoint?: (ref: any) => void;
  trainMode?: "restart" | "continue";
  onTrainMode?: (mode: "restart" | "continue") => void;
}) {
  const fields = (keys: string[]) =>
    keys
      .filter(
        (k) =>
          k in values &&
          !(
            values.scheduler_unit === "epoch" &&
            ["scheduler", "min_lr", "warmup_ratio"].includes(k)
          ),
      )
      .map((key) => (
        <ConfigurationField
          key={key}
          label={labels[key] || key}
          help={"train." + key}
          value={values[key]}
          options={capabilities?.training_options?.[key]}
          disabled={
            capabilities?.training_constraints?.[key]?.readOnly ||
            ([
              "optimizer",
              "precision",
              "device",
              "scheduler",
              "scheduler_unit",
              "parameter_group_policy",
              "evaluation_split",
            ].includes(key) &&
              !capabilities?.training_options?.[key])
          }
          onChange={(v) => onChange(key, v)}
        />
      ));
  const slices = preparationSlices(selectedPreparation);
  const trainingSplit = normalizeSlice(values.training_split);
  const selectedSlice = slices.find((item) => item.name === trainingSplit) || slices[0];
  const sliceKnown = selectedSlice?.count != null;
  const canStart =
    Boolean(selectedPreparation) &&
    (!sliceKnown || (selectedSlice?.count ?? 0) > 0) &&
    (trainMode === "restart" || Boolean(selectedCheckpoint));
  const hint = preparations.length
    ? selectedPreparation
      ? sliceKnown && !(selectedSlice?.count ?? 0)
        ? "所选切片没有样本"
        : trainMode === "continue" && !selectedCheckpoint
        ? "请先选择检查点"
        : ""
      : "请先选择已准备完成的数据集"
    : "请先完成数据准备";
  const sliceSelect = (key: "training_split" | "evaluation_split" | "export_split", value: string) => (
    <Select
      aria-label={labels[key]}
      value={normalizeSlice(value)}
      options={slices.map((item) => ({
        value: item.name,
        label: sliceOptionLabel(item),
      }))}
      onChange={(next) => onChange(key, next)}
    />
  );
  return (
    <div className="training-layout">
      <Card title="训练参数设置" className="training-left">
        {officialCombos.length ? (
          <label className="train-combo">
            数据集-模型组合
            <Select
              aria-label="训练设置组合"
              placeholder="选择官方配置"
              value={selectedCombo}
              disabled={busy}
              options={officialCombos.map((item) => ({
                value: item.id,
                label: item.name,
              }))}
              onChange={(id) => onLoadCombo?.(id)}
            />
          </label>
        ) : null}
        <h3>参数优化</h3>
        <div className="configuration-grid">
          {fields([
            "optimizer",
            "learning_rate",
            "weight_decay",
            "precision",
            "accumulate",
            "gradient_clip",
            "scheduler",
            "scheduler_unit",
            "warmup_ratio",
            "min_lr",
            "min_lr_ratio",
          ])}
        </div>
        {values.scheduler_unit === "epoch" ? (
          <p>学习率调度：逐轮余弦（固定），最低学习率由最小学习率比例确定。</p>
        ) : null}
        <h3>训练控制</h3>
        <div className="configuration-grid">
          {fields([
            "max_epochs",
            "batch_size",
            "device",
            "num_workers",
            "save_on_interrupt",
            "parameter_group_policy",
          ])}
        </div>
        <h3>维护 EMA 权重</h3>
        <Checkbox
          checked={values.ema_decay !== null && values.ema_decay !== undefined}
          onChange={(e) => onChange("ema_decay", e.target.checked ? 0.9999 : null)}
        >
          启用 EMA
        </Checkbox>
        <div className="configuration-grid">{fields(["ema_decay", "ema_save_every"])}</div>
      </Card>
      <div className="training-right">
        <Card title="默认训练诊断">
          <div className="configuration-grid">
            {fields(["log_every", "log_every_updates", "loss_x_axis", "snapshot"])}
          </div>
          <div className="diagnostic-options">
            <Checkbox checked disabled>
              运行日志
            </Checkbox>
            <Checkbox
              checked={values.snapshot === true}
              disabled={!("snapshot" in values)}
              onChange={(e) => onChange("snapshot", e.target.checked)}
            >
              代码快照
            </Checkbox>
            <Checkbox disabled>梯度直方图（当前案例未声明）</Checkbox>
            <Checkbox disabled>性能剖析（当前案例未声明）</Checkbox>
          </div>
          <p>日志间隔按当前案例实际支持项保存；未声明诊断不可提交。</p>
        </Card>
        <Card title="测试评估">
          <div className="configuration-grid">
            {fields([
              "evaluation_enabled",
              "test_repeat",
              "evaluate_repeat",
              "test_repeat",
            ])}
          </div>
          {"evaluation_split" in values || selectedPreparation ? (
            <label className="train-combo">
              评估切片
              {sliceSelect("evaluation_split", values.evaluation_split || "test")}
            </label>
          ) : null}
          <label className="train-combo">
            评估物理量
            <Select
              mode="multiple"
              allowClear
              aria-label="评估物理量"
              placeholder="默认评估全部物理量"
              value={values.evaluation_fields ?? capabilities?.evaluation_fields?.default ?? []}
              options={capabilities?.evaluation_fields?.options ?? []}
              disabled={busy || !capabilities?.evaluation_fields}
              onChange={(value) => onChange("evaluation_fields", value)}
            />
          </label>
          <label className="train-combo">
            评估指标
            <Select
              mode="multiple"
              allowClear
              aria-label="评估指标"
              placeholder="不计算附加误差指标"
              value={values.evaluation_metrics ?? capabilities?.evaluation_metrics?.default ?? []}
              options={capabilities?.evaluation_metrics?.options ?? []}
              disabled={busy || !capabilities?.evaluation_metrics || capabilities?.training_constraints?.evaluation_enabled?.readOnly}
              onChange={(value) => onChange("evaluation_metrics", value)}
            />
          </label>
          <div className="configuration-grid">
            {fields(["validation_interval", "validation_unit"])}
          </div>
          <Checkbox
            checked={values.evaluation_aggregate !== false}
            onChange={(e) => onChange("evaluation_aggregate", e.target.checked)}
          >
            聚合测试评估结果
          </Checkbox>
          <p>
            测试重复评估次数是在同一测试分片上重复采样/前向，用于观察随机评估稳定性，不是评估间隔。所选物理量和指标只用于 evaluation；关闭测试评估时显示明确空态，不把 Loss 或在线分项当成测试指标。
          </p>
        </Card>
        <Card title="训练结束写出">
          <div className="diagnostic-options">
            <Checkbox
              aria-label="写出预测"
              checked={values.export_predictions === true}
              disabled={capabilities?.training_constraints?.export_predictions?.readOnly}
              onChange={(e) => {
                onChange("export_predictions", e.target.checked);
                if (!e.target.checked) onChange("export_vtk", false);
              }}
            >
              写出预测
            </Checkbox>
            <Checkbox
              aria-label="写出网格"
              checked={values.export_vtk === true}
              disabled={!values.export_predictions}
              onChange={(e) => onChange("export_vtk", e.target.checked)}
            >
              写出网格
            </Checkbox>
          </div>
          <label className="train-combo">
            写出切片
            {sliceSelect("export_split", values.export_split || "test")}
          </label>
          <p>
            默认关闭。打开后在本次训练成功结束时按所选分片写出，后处理结果文件可浏览。不会打开训练期测试评估，也不创建推理批次。
          </p>
        </Card>
        <Card title="开始训练" id="stage-handoff">
          <label className="train-combo">
            已准备完成的数据集
            <Select
              allowClear
              aria-label="已准备完成的数据集"
              placeholder={
                preparations.length
                  ? `有 ${preparations.length} 个已准备完成的数据集，请选择`
                  : "选择已准备完成的数据集"
              }
              value={selectedPreparation?.ref?.asset_id}
              disabled={busy}
              options={preparations.map((item) => ({
                value: item.ref.asset_id,
                label: preparedDatasetLabel(item),
              }))}
              onChange={(id) => {
                const item = preparations.find((row) => row.ref?.asset_id === id);
                onPreparation?.(item?.ref);
                const next = preparationSlices(item);
                const current = normalizeSlice(values.training_split);
                const chosen = next.find((slice) => slice.name === current && (slice.count ?? 1) > 0);
                onChange("training_split", chosen?.name || "train");
                if (!next.find((slice) => slice.name === normalizeSlice(values.evaluation_split)))
                  onChange("evaluation_split", values.evaluation_split || "test");
              }}
            />
          </label>
          <label className="train-combo">
            训练切片
            {sliceSelect("training_split", trainingSplit || "train")}
          </label>
          {selectedSlice?.method ? (
            <p>
              {selectedSlice.label}在数据准备时按
              {selectedSlice.method === "random" ? "随机抽取" : "原划分"}
              {selectedSlice.seed != null ? `，种子 ${selectedSlice.seed}` : ""}
              {selectedSlice.count != null ? `，${selectedSlice.count} 个样本` : ""}
              关联。
            </p>
          ) : null}
          <label className="train-combo">
            训练模式
            <Radio.Group
              aria-label="训练模式"
              value={trainMode}
              disabled={busy}
              onChange={(e) => onTrainMode?.(e.target.value)}
              options={[
                { value: "restart", label: "重新开始" },
                { value: "continue", label: "继续训练" },
              ]}
            />
          </label>
          {trainMode === "continue" ? (
            <label className="train-combo">
              检查点
              <Select
                allowClear
                aria-label="检查点"
                placeholder={
                  checkpoints.length
                    ? `有 ${checkpoints.length} 个检查点，请选择`
                    : "没有可继续的检查点"
                }
                value={selectedCheckpoint?.ref?.asset_id}
                disabled={busy || !checkpoints.length}
                options={checkpoints.map((item) => ({
                  value: item.ref.asset_id,
                  label: checkpointLabel(item),
                }))}
                onChange={(id) =>
                  onCheckpoint?.(
                    checkpoints.find((item) => item.ref?.asset_id === id)?.ref,
                  )
                }
              />
            </label>
          ) : null}
          <p>
            预检只核验本页训练参数是否合法，不要求已有准备记录。点保存即记下完成，未改参数也会盖住旧失败预检；刷新仍按已保存事实恢复。开始训练使用当前设置、所选已准备数据和其中的切片；评估与写出仍用该准备里的测试/评价切片。继续训练只把检查点当作这一轮起始权重。
          </p>
          <Button loading={busy} onClick={onCheck}>
            预检
          </Button>{" "}
          <Button type="default" loading={busy} onClick={onSave}>
            保存训练设置
          </Button>{" "}
          <Button type="primary" loading={busy} disabled={!canStart} onClick={onStart}>
            开始训练
          </Button>
          {hint ? <small className="handoff-hint">{hint}</small> : null}
        </Card>
      </div>
    </div>
  );
}
