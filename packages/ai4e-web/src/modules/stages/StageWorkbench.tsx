import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Select, Space, Spin } from "antd";
import { useEffect, useRef, useState } from "react";
import { ExecutionLog, TrainingMonitor, listRuns } from "../executions";
import { PreparationPanel } from "../trainprep";
import { ModelPanel } from "../models";
import { TrainingPanel } from "../training";
import { PostWorkspace } from "../post";
import {
  readStage,
  saveStage,
  runStage,
  traceModel,
  stageInputs,
  modelAssetUrl,
  pollOperation,
  modelOptions,
  exportModelPreset,
} from "./api";

/** 同一清单只作为一条选项；平台名称优先并按登记时间倒序，避免与任务历史共用 asset_id 导致点一项选中多项。 */
function bindingOptionKey(item: any) {
  return [
    item.origin || "run",
    item.ref?.asset_id,
    item.processed_name || item.run_id || "",
    item.name,
  ].join(":");
}

function choiceTime(item: any) {
  return String(item.created_at || "");
}

function byNewest(left: any, right: any) {
  return choiceTime(right).localeCompare(choiceTime(left)) || String(left.name || "").localeCompare(String(right.name || ""));
}

function uniqueManifestChoices(items: any[]) {
  const valid = items.filter((item) => item.ref && item.compatibility?.status !== "invalid");
  const platform = valid.filter((item) => item.origin === "platform").slice().sort(byNewest);
  const used = new Set(platform.map((item) => item.ref.asset_id));
  return [
    ...platform,
    ...valid
      .filter((item) => item.origin !== "platform" && !used.has(item.ref.asset_id))
      .slice()
      .sort(byNewest),
  ];
}

/** 相同草稿不受对象键插入顺序影响，刷新后仍能恢复同一次提交。 */
function fingerprintOf(value: any) {
  return JSON.stringify(value, (_key, item) =>
    item && typeof item === "object" && !Array.isArray(item)
      ? Object.fromEntries(
          Object.entries(item).sort(([a], [b]) => a.localeCompare(b)),
        )
      : item,
  );
}

/** 保存与提交分别反馈，操作凭据仅用于重连，不复制服务运行事实。 */
export function StageWorkbench({
  project,
  task,
  stage,
}: {
  project: string;
  task: string;
  stage: string;
}) {
  const [cfg, setCfg] = useState<any>(),
    [values, setValues] = useState<any>(),
    [inputs, setInputs] = useState<any[]>([]),
    [bindings, setBindings] = useState<Record<string, any>>({}),
    [bindingEdits, setBindingEdits] = useState<Record<string, any>>({}),
    [runs, setRuns] = useState<any[]>([]),
    [run, setRun] = useState<string>(),
    [trace, setTrace] = useState<any>(),
    [traceStale, setTraceStale] = useState(false),
    [error, setError] = useState(""),
    [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [dirty, setDirty] = useState(false),
    [progress, setProgress] = useState<any>(),
    [resultRun, setResultRun] = useState<string>();
  const [models, setModels] = useState<any>(),
    [modelError, setModelError] = useState(""),
    [modelsLoading, setModelsLoading] = useState(false),
    [selectedCase, setSelectedCase] = useState<string>(),
    [selectedVariant, setSelectedVariant] = useState<string>(),
    [selectedPreset, setSelectedPreset] = useState<string>(),
    [targetSwitch, setTargetSwitch] = useState<{
      model?: string;
      variant?: string;
      preset?: string;
    }>(),
    [exportBusy, setExportBusy] = useState(false);
  const modelRequest = useRef(0);
  async function loadModels() {
    const request = ++modelRequest.current;
    setModelsLoading(true);
    setModelError("");
    try {
      const result = await modelOptions(project, task);
      if (request !== modelRequest.current) return;
      setModels(result);
      setSelectedCase(result.current_model_id || undefined);
      setSelectedVariant(result.current_variant || undefined);
      setSelectedPreset(result.current_preset_id || undefined);
    } catch (e: any) {
      if (request === modelRequest.current) setModelError(e.message);
    } finally {
      if (request === modelRequest.current) setModelsLoading(false);
    }
  }
  useEffect(() => {
    setModels(undefined);
    setSelectedCase(undefined);
    setSelectedVariant(undefined);
    setSelectedPreset(undefined);
    setTargetSwitch(undefined);
    setModelError("");
    if (stage === "model") void loadModels();
    return () => {
      modelRequest.current++;
    };
  }, [project, task, stage]);
  function applyOption(option: any, extra: { model?: string; variant?: string; preset?: string } = {}) {
    setValues(structuredClone(option.model));
    setCfg((old: any) => ({ ...old, capabilities: option.capabilities }));
    setDirty(true);
    setTrace(undefined);
    setTraceStale(false);
    setError("");
    setMessage(
      "模型已切换；保存后请重新准备数据，训练设置将恢复为目标默认值",
    );
    setTargetSwitch({
      model: extra.preset ? undefined : extra.model || option.model_id || option.id,
      variant: extra.variant,
      preset: extra.preset,
    });
  }
  function chooseModel(id: string) {
    if (gate.current || (id === selectedCase && !selectedPreset)) return;
    const option = models?.options?.find((item: any) => item.id === id);
    if (!option) return;
    const variant = option.variants?.[0]?.id;
    setSelectedCase(id);
    setSelectedVariant(variant);
    setSelectedPreset(undefined);
    applyOption(option.variant_defaults?.[variant] || option, { model: id, variant });
  }
  function chooseVariant(id: string) {
    if (gate.current || id === selectedVariant) return;
    const option = models?.options?.find((item: any) => item.id === selectedCase);
    const defaults = option?.variant_defaults?.[id] || option;
    if (!defaults) return;
    setSelectedVariant(id);
    setSelectedPreset(undefined);
    applyOption(defaults, { model: selectedCase, variant: id });
  }
  function choosePreset(id?: string) {
    if (gate.current) return;
    if (!id) {
      setSelectedPreset(undefined);
      return;
    }
    const option = models?.presets?.find((item: any) => item.id === id);
    if (!option) return;
    setSelectedCase(option.model_id);
    setSelectedVariant(option.variant || undefined);
    setSelectedPreset(id);
    applyOption(option, { preset: id, variant: option.variant || undefined });
  }
  async function exportPreset(name: string) {
    if (gate.current || !cfg) return;
    gate.current = true;
    setExportBusy(true);
    setError("");
    try {
      let revision = cfg.revision;
      if (dirty) {
        const result = await saveStage(
          project,
          task,
          cfg.stage,
          revision,
          values,
          bindingEdits,
          targetSwitch,
        );
        revision = result.revision;
        setCfg({ ...cfg, revision });
        setValues(result.config?.[cfg.stage] ?? values);
        setDirty(false);
        setBindingEdits({});
        setTargetSwitch(undefined);
      }
      await exportModelPreset(project, task, revision, name);
      await loadModels();
      setMessage("模型配置已导出");
    } catch (e: any) {
      setError(e.message);
    } finally {
      gate.current = false;
      setExportBusy(false);
    }
  }
  const gate = useRef(false),
    generation = useRef(0);
  const storageKey = `dojo.stage-submit:${project}:${task}:${stage}`;
  useEffect(() => {
    const token = ++generation.current;
    setCfg(undefined);
    setError("");
    setMessage("");
    setBindings({});
    setBindingEdits({});
    setDirty(false);
    setTrace(undefined);
    setTraceStale(false);
    gate.current = false;
    setBusy(false);
    Promise.all([
      readStage(project, task, stage === "execution" ? "train" : stage),
      stageInputs(project, task),
      listRuns(project, task),
    ])
      .then(([c, i, r]) => {
        if (token !== generation.current) return;
        setCfg(c);
        setValues(c.values);
        setInputs(i);
        const selected: Record<string, any> = {};
        for (const item of i)
          if (item.selected && item.ref) selected[item.binding] = item.ref;
        setBindings(selected);
        const expected = stage === "execution" ? "train" : stage;
        const candidates =
          stage === "model"
            ? []
            : r.filter((x: any) =>
                (x.stages || Object.keys(x.summary?.reports || {})).includes(
                  expected,
                ),
              );
        setRuns(candidates);
        const latest = [...candidates].sort((a, b) =>
          String(b.created_at || b.created || "").localeCompare(
            String(a.created_at || a.created || ""),
          ),
        )[0]?.id;
        setRun(latest);
        setResultRun(
          stage === "trainprep"
            ? candidates
                .filter((x: any) => (x.operation_mode || "execute") === "execute")
                .sort((a: any, b: any) =>
                  String(b.created_at || b.created || "").localeCompare(
                    String(a.created_at || a.created || ""),
                  ),
                )[0]?.id
            : undefined,
        );
      })
      .catch((e) => token === generation.current && setError(e.message));
    return () => {
      generation.current++;
    };
  }, [project, task, stage]);
  function change(key: string, value: any) {
    if (gate.current) return;
    setValues((old: any) => ({ ...old, [key]: value }));
    setDirty(true);
    setTraceStale(Boolean(trace));
    setMessage("");
  }
  function bind(key: string, ref: any) {
    if (gate.current) return;
    setBindings((old) => {
      const next = { ...old };
      if (ref) next[key] = ref;
      else delete next[key];
      return next;
    });
    setBindingEdits((old) => ({ ...old, [key]: ref || null }));
    setDirty(true);
    setTraceStale(Boolean(trace));
    setMessage("");
  }
  async function action(mode: string) {
    if (gate.current || !cfg) return;
    if (mode !== "save" && cfg.capabilities?.unavailable_reason) {
      setError("能力检查暂不可用，请核对配置后重试");
      return;
    }
    gate.current = true;
    setBusy(true);
    setError("");
    if (mode === "execute" && stage === "trainprep") {
      setProgress(undefined);
      setResultRun(undefined);
    }
    const token = generation.current;
    const current = () => token === generation.current;
    let saved = false;
    try {
      let revision = cfg.revision,
        effectiveValues = values;
      let effectiveBindings = bindings;
      if (dirty) {
        const result = await saveStage(
          project,
          task,
          cfg.stage,
          revision,
          values,
          bindingEdits,
          targetSwitch,
        );
        revision = result.revision;
        effectiveValues = result.config?.[cfg.stage] ?? values;
        saved = true;
        if (current()) {
          setCfg({ ...cfg, revision });
          setValues(effectiveValues);
          setDirty(false);
          setBindingEdits({});
          setTargetSwitch(undefined);
          setMessage("配置已保存，未创建新版本");
        }
        const [fresh, freshInputs] = await Promise.all([
          readStage(project, task, cfg.stage),
          stageInputs(project, task),
        ]);
        if (fresh.revision !== revision)
          throw new Error("configuration_revision_conflict");
        effectiveValues = fresh.values;
        effectiveBindings = {};
        for (const item of freshInputs)
          if (item.selected && item.ref)
            effectiveBindings[item.binding] = item.ref;
        if (current()) {
          setCfg(fresh);
          setValues(effectiveValues);
          setInputs(freshInputs);
          setBindings(effectiveBindings);
        }
      }
      const allowed =
        cfg.stage === "post"
          ? ["train.preparation", "post.checkpoint"]
          : cfg.stage === "trainprep"
            ? ["train.manifest", "trainprep.normalization.statistics"]
            : ["train.manifest", "train.preparation"];
      effectiveBindings = Object.fromEntries(
        Object.entries(effectiveBindings).filter(([key]) =>
          allowed.includes(key),
        ),
      );
      if (mode === "save") {
        if (current()) setMessage("配置已保存，未创建新版本");
        window.dispatchEvent(
          new CustomEvent("dojo:task-updated", { detail: { project, task } }),
        );
        return;
      }
      const fingerprint = fingerprintOf({
        revision,
        mode,
        stage: cfg.stage,
        bindings: effectiveBindings,
        values: effectiveValues,
      });
      let pending: any;
      try {
        pending = JSON.parse(sessionStorage.getItem(storageKey) || "null");
      } catch {
        pending = null;
      }
      if (pending?.fingerprint !== fingerprint)
        pending = { fingerprint, key: crypto.randomUUID() };
      sessionStorage.setItem(storageKey, JSON.stringify(pending));
      const accepted = (operation: any) => {
        pending.operation = operation;
        sessionStorage.setItem(storageKey, JSON.stringify(pending));
      };
      let result: any;
      if (pending.operation?.operation_id) {
        const operation = await pollOperation(project, pending.operation);
        result = mode === "trace" ? operation : operation.result;
      } else if (pending.operation?.id) result = pending.operation;
      else if (mode === "trace")
        result = await traceModel(
          project,
          task,
          revision,
          effectiveBindings,
          pending.key,
          accepted,
        );
      else
        result = await runStage(
          project,
          task,
          cfg.stage,
          revision,
          mode,
          { prepare_first: stage === "execution", bindings: effectiveBindings },
          pending.key,
          accepted,
        );
      sessionStorage.removeItem(storageKey);
      if (!current()) return;
      if (mode === "trace") {
        setTrace(result);
        setTraceStale(false);
        setMessage("真实模型结构已生成 · 配置修订 " + revision.slice(0, 8));
      } else if (result.id) {
        setRun(result.id);
        if (mode === "execute") setResultRun(result.id);
        setRuns((old) => [...old.filter((r) => r.id !== result.id), result]);
        setMessage("运行已提交");
      } else if (result.valid === false) {
        setError(
          "配置与交接检查未通过：" + JSON.stringify(result.errors || result),
        );
        setMessage("");
      } else
        setMessage(
          result.valid ? "配置与交接检查通过" : JSON.stringify(result),
        );
      window.dispatchEvent(
        new CustomEvent("dojo:task-updated", { detail: { project, task } }),
      );
    } catch (e: any) {
      if (current()) {
        setError((saved ? "配置已保存；后续操作失败：" : "") + e.message);
        if (saved) setMessage("配置已保存，未创建新版本");
      }
    } finally {
      if (current()) {
        gate.current = false;
        setBusy(false);
      }
    }
  }
  if (!cfg) return error ? <Alert type="error" message={error} /> : <Spin />;
  const bindingNames: Record<string, string> = {
    "train.manifest": stage === "trainprep" ? "平台数据集" : "物理数据清单",
    "train.preparation": "准备记录",
    "post.checkpoint": "模型检查点",
  };
  const bindingReasons: Record<string, string> = {
    path_outside_root: "所选文件不在可访问范围内。",
    binding_file_missing: "已绑定来源文件不存在。",
    binding_source_unavailable: "已绑定来源不可用。",
    invalid_binding_path: "绑定路径无效。",
    binding_resolution_failed: "绑定路径无法解析。",
  };
  const bindingKeys =
    stage === "trainprep"
      ? ["train.manifest"]
      : stage === "post"
        ? ["train.preparation", "post.checkpoint"]
        : stage === "model"
          ? []
          : ["train.manifest", "train.preparation"];
  const choices = (binding: string) => {
    const items = inputs.filter((item) => item.ref && item.binding === binding);
    return binding === "train.manifest" ? uniqueManifestChoices(items) : items;
  };
  const selectedChoice = (binding: string) => {
    const ref = bindings[binding];
    if (!ref) return undefined;
    const items = choices(binding);
    return (
      items.find((item) => item.selected && item.ref.asset_id === ref.asset_id) ||
      items.find((item) => item.origin === "platform" && item.ref.asset_id === ref.asset_id) ||
      items.find((item) => item.ref.asset_id === ref.asset_id)
    );
  };
  const selectedDataset = selectedChoice("train.manifest");
  const bindingPanel = (
    <div className="input-bindings" id="stage-handoff">
      {inputs
        .filter(
          (i) =>
            bindingKeys.includes(i.binding) &&
            !i.ref &&
            i.compatibility?.status === "invalid",
        )
        .map((i) => (
          <Alert
            key={i.binding}
            type="error"
            message={(bindingNames[i.binding] || i.binding) + "：已绑定来源不可用"}
            description={bindingReasons[i.compatibility.reason] || i.compatibility.reason}
          />
        ))}
      {traceStale && (
        <Alert
          type="warning"
          message="模型结构已过期，请按当前配置与输入重新生成"
        />
      )}
      {bindingKeys.map((binding) => (
        <div key={binding}>
          <label>{bindingNames[binding]}</label>
          <Select
            allowClear
            disabled={busy}
            aria-label={binding}
            style={{ width: "100%", marginBottom: 8 }}
            placeholder={
              choices(binding).length
                ? binding === "train.manifest"
                  ? `有 ${choices(binding).length} 个平台数据集，请选择`
                  : `有 ${choices(binding).length} 个正式产物，请选择`
                : binding === "train.manifest"
                  ? "选择平台数据集"
                  : "选择正式运行产物"
            }
            value={selectedChoice(binding) ? bindingOptionKey(selectedChoice(binding)) : undefined}
            options={choices(binding).map((i) => ({
              value: bindingOptionKey(i),
              label:
                i.origin === "platform"
                  ? i.processed_name || i.name
                  : (i.run_id?.slice(0, 8) || "本任务历史") +
                    " / " +
                    i.name +
                    " · " +
                    (i.compatibility?.status === "compatible"
                      ? "兼容"
                      : "待检查"),
            }))}
            onChange={(value) =>
              bind(
                binding,
                choices(binding).find((item) => bindingOptionKey(item) === value)?.ref,
              )
            }
          />
        </div>
      ))}
    </div>
  );
  return (
    <div className="stage-content" style={{ display: "flow-root" }}>
      {cfg.capabilities?.unavailable_reason && (
        <Alert
          type="warning"
          message="能力检查暂不可用，仍可修改已保存配置"
          description={cfg.capabilities.unavailable_reason}
        />
      )}{" "}
      {error && <Alert type="error" message={error} />}{" "}
      {message && <Alert type="success" message={message} />}
      {stage === "trainprep" ? (
        <PreparationPanel
          project={project}
          task={task}
          run={run}
          resultRun={resultRun}
          inputAsset={bindings["train.manifest"]}
          datasetName={selectedDataset?.processed_name || selectedDataset?.name}
          emptyHint={
            choices("train.manifest").length && !bindings["train.manifest"]
              ? "请从上方选择平台数据集"
              : undefined
          }
          progress={progress}
          values={values}
          onChange={change}
          bindings={bindingPanel}
          onExecute={() => action("execute")}
          onCheck={() => action("check")}
          onSave={() => action("save")}
          busy={busy}
          dirty={dirty}
          capabilities={cfg.capabilities}
        />
      ) : stage === "model" ? (
        <ModelPanel
          modelOptions={models?.options || []}
          presets={models?.presets || []}
          selectedCase={selectedCase}
          selectedVariant={selectedVariant}
          selectedPreset={selectedPreset}
          onModelChange={chooseModel}
          onVariantChange={chooseVariant}
          onPresetChange={choosePreset}
          onExport={exportPreset}
          exportBusy={exportBusy}
          modelError={modelError}
          modelsLoading={modelsLoading}
          onRetryModels={loadModels}
          capabilities={cfg.capabilities}
          values={values}
          onChange={change}
          trace={trace}
          traceUrl={trace ? modelAssetUrl(project, trace) : undefined}
          onTrace={() => action("trace")}
          busy={busy}
          canTrace={
            !cfg.capabilities?.unavailable_reason &&
            models?.trace_available !== false
          }
        />
      ) : stage === "train" ? (
        <TrainingPanel
          capabilities={cfg.capabilities}
          values={values}
          onChange={change}
          onCheck={() => action("check")}
          onSave={() => action("save")}
          busy={busy}
        />
      ) : stage === "execution" ? (
        <TrainingMonitor
          project={project}
          run={run}
          runs={runs}
          onRun={setRun}
          inputs={inputs}
          onInput={(ref) => bind("train.manifest", ref)}
          onStart={() => action("execute")}
          busy={busy}
        />
      ) : (
        <PostWorkspace
          project={project}
          task={task}
          run={run}
          runs={runs}
          onRun={setRun}
          values={values}
          onChange={change}
          bindings={bindingPanel}
          onExecute={() => action("execute")}
          busy={busy}
        />
      )}
      <div
        className="stage-controls"
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          margin: "8px 0",
          fontSize: 11,
          color: "#728bbb",
        }}
      >
        {dirty && <span>操作前将先保存当前设置</span>}
        {!["train", "trainprep"].includes(stage) && (
          <Space>
            <Button
              onClick={() => action("check")}
              loading={busy}
              disabled={Boolean(cfg.capabilities?.unavailable_reason)}
            >
              检查配置与交接
            </Button>
            <Button
              type="primary"
              onClick={() => action("save")}
              disabled={!dirty}
              loading={busy}
            >
              保存配置
            </Button>
          </Space>
        )}
      </div>
      {stage !== "execution" && stage !== "model" && (
        <ExecutionLog
          project={project}
          run={run}
          accumulate={stage === "trainprep"}
          onSnapshot={
            stage === "trainprep"
              ? (value) => {
                  if (run === resultRun) setProgress(value);
                }
              : undefined
          }
        />
      )}
    </div>
  );
}
