import { configurationEdits } from "../../infrastructure/configuration/edits";
import {
  bindingOptionKey,
  preparedDatasetLabel,
  uniqueManifestChoices,
  unavailableBindingItems,
} from "./inputChoices";
/** 工作台公开页面：组合领域面板，保留配置与执行交接。 */
import { useModelSelection } from "./useModelSelection";
import { ActionButton as Button } from "../../infrastructure/components/ActionButton";
import { Alert, Select, Space, Spin } from "antd";
import { useEffect, useRef, useState } from "react";
import { ExecutionLog, listRuns } from "../executions";
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
  invalidateStageInputs,
  invalidateModelOptions,
  modelAssetUrl,
  pollOperation,
  exportModelPreset,
} from "./api";

function selectedBindings(items: any[]) {
  const selected: Record<string, any> = {};
  for (const item of items)
    if (item.selected && item.ref) selected[item.binding] = item.ref;
  return selected;
}

function runsForStage(stage: string, rows: any[]) {
  const candidates =
    stage === "model"
      ? []
      : rows.filter((x: any) =>
          (x.stages || Object.keys(x.summary?.reports || {})).includes(stage),
        );
  const latest = [...candidates].sort((a, b) =>
    String(b.created_at || b.created || "").localeCompare(
      String(a.created_at || a.created || ""),
    ),
  )[0]?.id;
  const resultRun =
    stage === "trainprep"
      ? candidates
          .filter((x: any) => (x.operation_mode || "execute") === "execute")
          .sort((a: any, b: any) =>
            String(b.created_at || b.created || "").localeCompare(
              String(a.created_at || a.created || ""),
            ),
          )[0]?.id
      : undefined;
  return { candidates, latest, resultRun };
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
  onStarted,
}: {
  project: string;
  task: string;
  stage: string;
  onStarted?: (runId: string) => void;
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
  const gate = useRef(false);
  const editBaseline = useRef<any>({});
  const [targetSwitch, setTargetSwitch] = useState<{
    model?: string;
    variant?: string;
    preset?: string;
  }>();
  const [exportBusy, setExportBusy] = useState(false);
  const [pageCombo, setPageCombo] = useState<string>();
  const [trainMode, setTrainMode] = useState<"restart" | "continue">("restart");
  const [resumeRef, setResumeRef] = useState<any>();
  const {
    models,
    modelError,
    modelsLoading,
    selectedCase,
    selectedVariant,
    selectedPreset,
    loadModels,
    chooseModel,
    chooseVariant,
    choosePreset,
  } = useModelSelection(project, task, stage, gate, applyOption, () =>
    setTargetSwitch(undefined),
  );
  function applyOption(
    option: any,
    extra: { model?: string; variant?: string; preset?: string } = {},
  ) {
    setValues(structuredClone(option.model));
    setCfg((old: any) => ({ ...old, capabilities: option.capabilities }));
    setDirty(true);
    setPageCombo(undefined);
    setTrace(undefined);
    setTraceStale(false);
    setError("");
    setMessage("模型已切换；保存后请重新准备数据，训练设置将恢复为目标默认值");
    setTargetSwitch({
      model: extra.preset
        ? undefined
        : extra.model || option.model_id || option.id,
      variant: extra.variant,
      preset: extra.preset,
    });
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
          configurationEdits(editBaseline.current, values),
        );
        revision = result.revision;
        setCfg({ ...cfg, revision });
        setValues(result.config?.[cfg.stage] ?? values);
        editBaseline.current = structuredClone(result.config?.[cfg.stage] ?? values);
        setDirty(false);
        setBindingEdits({});
        setTargetSwitch(undefined);
      }
      await exportModelPreset(project, task, revision, name);
      invalidateModelOptions(project, task);
      await loadModels();
      setMessage("模型配置已导出");
    } catch (e: any) {
      setError(e.message);
    } finally {
      gate.current = false;
      setExportBusy(false);
    }
  }
  const generation = useRef(0);
  const storageKey = `dojo.stage-submit:${project}:${task}:${stage}`;
  useEffect(() => {
    const token = ++generation.current;
    setCfg(undefined);
    setError("");
    setMessage("");
    setBindings({});
    setBindingEdits({});
    setDirty(false);
    setPageCombo(undefined);
    setTrainMode("restart");
    setResumeRef(undefined);
    setTrace(undefined);
    setTraceStale(false);
    gate.current = false;
    setBusy(false);
    /** 配置先渲染；产物与运行名单并行补齐，慢列表不能挡住切步。 */
    readStage(project, task, stage)
      .then((c) => {
        if (token !== generation.current) return;
        setCfg(c);
        setValues(c.values);
        editBaseline.current = structuredClone(c.values);
      })
      .catch((e) => {
        if (token !== generation.current) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    stageInputs(project, task)
      .then((items) => {
        if (token !== generation.current) return;
        setInputs(items);
        setBindings(selectedBindings(items));
      })
      .catch((e) => {
        if (token !== generation.current) return;
        setError(e instanceof Error ? e.message : String(e));
      });
    if (stage === "model") {
      setRuns([]);
      setRun(undefined);
      setResultRun(undefined);
    } else
      listRuns(project, task)
        .then((rows) => {
          if (token !== generation.current) return;
          const listed = runsForStage(stage, rows);
          setRuns(listed.candidates);
          setRun(listed.latest);
          setResultRun(listed.resultRun);
        })
        .catch((e) => {
          if (token !== generation.current) return;
          setError(e instanceof Error ? e.message : String(e));
        });
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
      const persistSettings = dirty || mode === "save";
      if (persistSettings) {
        const result = await saveStage(
          project,
          task,
          cfg.stage,
          revision,
          values,
          bindingEdits,
          targetSwitch,
          configurationEdits(editBaseline.current, values),
        );
        revision = result.revision;
        effectiveValues = result.config?.[cfg.stage] ?? values;
        saved = true;
        if (current()) {
          setCfg({ ...cfg, revision });
          setValues(effectiveValues);
          editBaseline.current = structuredClone(effectiveValues);
          setDirty(false);
          setBindingEdits({});
          setTargetSwitch(undefined);
          setMessage("配置已保存，未创建新版本");
        }
        invalidateStageInputs(project, task);
        if (cfg.stage === "model") invalidateModelOptions(project, task);
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
          editBaseline.current = structuredClone(effectiveValues);
          setInputs(freshInputs);
          setBindings(effectiveBindings);
        }
      }
      const allowed =
        cfg.stage === "post"
          ? ["inputs.post.results"]
          : cfg.stage === "trainprep"
            ? ["inputs.trainprep.dataset", "inputs.trainprep.statistics"]
            : cfg.stage === "train"
              ? mode === "execute"
                ? trainMode === "continue"
                  ? ["inputs.train.preparation", "inputs.train.resume"]
                  : ["inputs.train.preparation"]
                : []
              : ["inputs.trainprep.dataset", "inputs.train.preparation"];
      if (cfg.stage === "train" && mode === "execute") {
        const preparation =
          effectiveBindings["inputs.train.preparation"] || bindings["inputs.train.preparation"];
        effectiveBindings = {};
        if (preparation) effectiveBindings["inputs.train.preparation"] = preparation;
        if (trainMode === "continue" && resumeRef)
          effectiveBindings["inputs.train.resume"] = resumeRef;
      } else
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
          { bindings: effectiveBindings },
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
        if (cfg.stage === "train" && mode === "execute") onStarted?.(result.id);
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
  async function loadCombo(caseId: string) {
    if (gate.current || !cfg) return;
    gate.current = true;
    setBusy(true);
    setError("");
    const token = generation.current;
    const current = () => token === generation.current;
    try {
      const result = await saveStage(
        project,
        task,
        cfg.stage,
        cfg.revision,
        values,
        bindingEdits,
        { case: caseId },
        configurationEdits(editBaseline.current, values),
      );
      invalidateStageInputs(project, task);
      if (cfg.stage === "model") invalidateModelOptions(project, task);
      const [fresh, freshInputs] = await Promise.all([
        readStage(project, task, cfg.stage),
        stageInputs(project, task),
      ]);
      if (fresh.revision !== result.revision) throw new Error("configuration_revision_conflict");
      if (!current()) return;
      setCfg(fresh);
      setValues(fresh.values);
      editBaseline.current = structuredClone(fresh.values);
      setInputs(freshInputs);
      setBindings(
        Object.fromEntries(
          freshInputs
            .filter((item: any) => item.selected && item.ref)
            .map((item: any) => [item.binding, item.ref]),
        ),
      );
      setBindingEdits({});
      setDirty(false);
      setPageCombo(caseId);
      if (cfg.stage === "trainprep") setTargetSwitch(undefined);
      setMessage(
        cfg.stage === "trainprep"
          ? "已加载官方数据准备组合"
          : "已加载官方配置，仅覆盖本页参数",
      );
      window.dispatchEvent(new CustomEvent("dojo:task-updated", { detail: { project, task } }));
    } catch (e: any) {
      if (current()) setError(e.message);
    } finally {
      if (current()) {
        gate.current = false;
        setBusy(false);
      }
    }
  }
  if (!cfg) return error ? <Alert type="error" message={error} /> : <Spin />;
  const bindingNames: Record<string, string> = {
    "inputs.trainprep.dataset": stage === "trainprep" ? "平台数据集" : "物理数据清单",
    "inputs.train.preparation": "已准备完成的数据集",
    "inputs.infer.checkpoint": "模型检查点",
    "inputs.post.results": "固定推理结果",
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
      ? ["inputs.trainprep.dataset"]
      : stage === "post"
        ? ["inputs.post.results"]
        : stage === "model" || stage === "train"
          ? []
          : ["inputs.trainprep.dataset", "inputs.train.preparation"];
  const choices = (binding: string) => {
    const items = inputs.filter((item) => item.ref && item.binding === binding);
    return binding === "inputs.trainprep.dataset" ? uniqueManifestChoices(items) : items;
  };
  const selectedChoice = (binding: string) => {
    const ref = bindings[binding];
    if (!ref) return undefined;
    const items = choices(binding);
    return (
      items.find(
        (item) => item.selected && item.ref.asset_id === ref.asset_id,
      ) ||
      items.find(
        (item) =>
          item.origin === "platform" && item.ref.asset_id === ref.asset_id,
      ) ||
      items.find((item) => item.ref.asset_id === ref.asset_id)
    );
  };
  const selectedDataset = selectedChoice("inputs.trainprep.dataset");
  const bindingPanel = (
    <div className="input-bindings" id="stage-handoff">
      {unavailableBindingItems(inputs, bindingKeys).map((i) => (
          <Alert
            key={i.binding}
            type="error"
            message={
              (bindingNames[i.binding] || i.binding) + "：已绑定来源不可用"
            }
            description={
              bindingReasons[i.compatibility.reason] || i.compatibility.reason
            }
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
                ? binding === "inputs.trainprep.dataset"
                  ? `有 ${choices(binding).length} 个平台数据集，请选择`
                  : `有 ${choices(binding).length} 个正式产物，请选择`
                : binding === "inputs.trainprep.dataset"
                  ? "选择平台数据集"
                  : "选择正式运行产物"
            }
            value={
              selectedChoice(binding)
                ? bindingOptionKey(selectedChoice(binding))
                : undefined
            }
            options={choices(binding).map((i) => ({
              value: bindingOptionKey(i),
              label:
                binding === "inputs.train.preparation"
                  ? preparedDatasetLabel(i)
                  : i.origin === "platform"
                  ? i.source_project_name ? `${i.processed_name || i.name} · ${i.source_project_name}` : i.processed_name || i.name
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
                choices(binding).find(
                  (item) => bindingOptionKey(item) === value,
                )?.ref,
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
          inputAsset={bindings["inputs.trainprep.dataset"]}
          datasetName={selectedDataset?.processed_name || selectedDataset?.name}
          emptyHint={
            choices("inputs.trainprep.dataset").length && !bindings["inputs.trainprep.dataset"]
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
          onLoadCombo={loadCombo}
          busy={busy}
          dirty={dirty}
          capabilities={cfg.capabilities}
        />
      ) : stage === "model" ? (
        <ModelPanel
          modelOptions={models?.options || []}
          presets={models?.presets || []}
          selectedCase={
            selectedCase || cfg.capabilities?.official_combos?.current_model_id
          }
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
          officialCombos={(cfg.capabilities?.official_combos?.options || []).filter(
            (item: any) =>
              item.model_id ===
              (selectedCase || cfg.capabilities?.official_combos?.current_model_id),
          )}
          selectedCombo={pageCombo}
          comboLocked={Boolean(targetSwitch)}
          onLoadCombo={loadCombo}
          trace={trace}
          graphUrl={
            trace
              ? (member?: string) => modelAssetUrl(project, trace, member)
              : undefined
          }
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
          officialCombos={(cfg.capabilities?.official_combos?.options || []).filter(
            (item: any) =>
              item.model_id === cfg.capabilities?.official_combos?.current_model_id,
          )}
          selectedCombo={pageCombo}
          onLoadCombo={loadCombo}
          onCheck={() => action("check")}
          onSave={() => action("save")}
          onStart={() => action("execute")}
          busy={busy}
          preparations={inputs.filter(
            (item: any) =>
              item.ref &&
              item.binding === "inputs.train.preparation" &&
              item.compatibility?.status !== "invalid",
          )}
          selectedPreparation={inputs.find(
            (item: any) =>
              item.ref &&
              item.binding === "inputs.train.preparation" &&
              item.ref.asset_id === bindings["inputs.train.preparation"]?.asset_id,
          )}
          onPreparation={(ref) => bind("inputs.train.preparation", ref)}
          checkpoints={inputs.filter(
            (item: any) =>
              item.ref &&
              item.binding === "inputs.infer.checkpoint" &&
              item.compatibility?.status !== "invalid",
          )}
          selectedCheckpoint={inputs.find(
            (item: any) =>
              item.ref && item.ref.asset_id === resumeRef?.asset_id,
          )}
          onCheckpoint={setResumeRef}
          trainMode={trainMode}
          onTrainMode={(mode) => {
            setTrainMode(mode);
            if (mode === "restart") setResumeRef(undefined);
          }}
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
              disabled={busy}
              loading={busy}
            >
              保存配置
            </Button>
          </Space>
        )}
      </div>
      {stage !== "model" && stage !== "train" && (
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
