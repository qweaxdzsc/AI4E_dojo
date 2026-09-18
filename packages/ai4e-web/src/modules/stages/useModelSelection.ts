/** 模型候选及选择草稿；请求失效控制与执行状态分开。 */
import { useEffect, useRef, useState, type MutableRefObject } from "react";
import {
  describeModelOption,
  modelOptions,
  peekModelOptions,
} from "./api";

export type ModelOption = {
  id: string;
  name: string;
  model_id?: string;
  variant?: string | null;
  model: Record<string, unknown>;
  train: Record<string, unknown>;
  trainprep: Record<string, unknown>;
  component: string;
  capabilities: Record<string, unknown>;
  variants?: { id: string; name: string }[];
  variant_defaults?: Record<string, ModelOption>;
};
export type ModelChoices = {
  revision: string;
  current_model_id?: string;
  current_variant?: string | null;
  current_preset_id?: string | null;
  options: ModelOption[];
  presets: ModelOption[];
  trace_available: boolean;
};

type Selection = { model?: string; variant?: string; preset?: string };

function optionReady(option?: ModelOption) {
  const capabilities = option?.capabilities || {};
  return Boolean(
    option?.model && (capabilities.sampling || capabilities.losses),
  );
}

/** 只管理模型选择；调用者负责把选择应用到工作台配置草稿。 */
export function useModelSelection(
  project: string,
  task: string,
  stage: string,
  gate: MutableRefObject<boolean>,
  applyOption: (option: ModelOption, selection: Selection) => void,
  resetTarget: () => void,
) {
  const [models, setModels] = useState<ModelChoices>(),
    [modelError, setModelError] = useState(""),
    [modelsLoading, setModelsLoading] = useState(false),
    [selectedCase, setSelectedCase] = useState<string>(),
    [selectedVariant, setSelectedVariant] = useState<string>(),
    [selectedPreset, setSelectedPreset] = useState<string>();
  const modelRequest = useRef(0);
  function remember(result: ModelChoices) {
    setModels(result);
    setSelectedCase(result.current_model_id || undefined);
    setSelectedVariant(result.current_variant || undefined);
    setSelectedPreset(result.current_preset_id || undefined);
  }
  async function loadModels() {
    const request = ++modelRequest.current;
    setModelsLoading(true);
    setModelError("");
    try {
      const result = await modelOptions(project, task);
      if (request !== modelRequest.current) return;
      remember(result);
    } catch (e: unknown) {
      if (request === modelRequest.current)
        setModelError(e instanceof Error ? e.message : String(e));
    } finally {
      if (request === modelRequest.current) setModelsLoading(false);
    }
  }
  useEffect(() => {
    resetTarget();
    setModelError("");
    if (stage !== "model") {
      setModels(undefined);
      setSelectedCase(undefined);
      setSelectedVariant(undefined);
      setSelectedPreset(undefined);
      return () => {
        modelRequest.current++;
      };
    }
    const cached = peekModelOptions(project, task);
    if (cached) {
      remember(cached);
      setModelsLoading(false);
      return () => {
        modelRequest.current++;
      };
    }
    setModels(undefined);
    setSelectedCase(undefined);
    setSelectedVariant(undefined);
    setSelectedPreset(undefined);
    void loadModels();
    return () => {
      modelRequest.current++;
    };
  }, [project, task, stage]);
  async function ensureDescribed(option: ModelOption, selection: Selection) {
    if (optionReady(option)) return option;
    return describeModelOption(project, task, selection);
  }
  function mergeDescribed(option: ModelOption, modelId?: string) {
    const id = modelId || option.model_id || option.id;
    setModels((old) => {
      if (!old) return old;
      return {
        ...old,
        options: old.options.map((item) => {
          if (item.id !== id) return item;
          return {
            ...item,
            ...option,
            id: item.id,
            name: item.name,
            variants: item.variants || option.variants,
            variant_defaults: {
              ...(item.variant_defaults || {}),
              ...(option.variant_defaults || {}),
            },
          };
        }),
        presets: old.presets.map((item) =>
          item.id === option.id ? { ...item, ...option } : item,
        ),
      };
    });
  }
  async function chooseModel(id: string) {
    if (gate.current || (id === selectedCase && !selectedPreset)) return;
    const listed = models?.options?.find((item: ModelOption) => item.id === id);
    if (!listed) return;
    const variant = listed.variants?.[0]?.id;
    const ready =
      (variant ? listed.variant_defaults?.[variant] : undefined) || listed;
    if (optionReady(ready)) {
      setSelectedCase(id);
      setSelectedVariant(variant);
      setSelectedPreset(undefined);
      applyOption(ready, { model: id, variant });
      return;
    }
    const request = ++modelRequest.current;
    setModelsLoading(true);
    setModelError("");
    try {
      const option = await ensureDescribed(listed, { model: id, variant });
      if (request !== modelRequest.current) return;
      const applied =
        (variant ? option.variant_defaults?.[variant] : undefined) || option;
      mergeDescribed(option, id);
      setSelectedCase(id);
      setSelectedVariant(variant);
      setSelectedPreset(undefined);
      applyOption(applied, { model: id, variant });
    } catch (e: unknown) {
      if (request === modelRequest.current)
        setModelError(e instanceof Error ? e.message : String(e));
    } finally {
      if (request === modelRequest.current) setModelsLoading(false);
    }
  }
  async function chooseVariant(id: string) {
    if (gate.current || id === selectedVariant) return;
    const listed = models?.options?.find(
      (item: ModelOption) => item.id === selectedCase,
    );
    const defaults = listed?.variant_defaults?.[id] || listed;
    if (!defaults || !selectedCase) return;
    if (optionReady(defaults)) {
      setSelectedVariant(id);
      setSelectedPreset(undefined);
      applyOption(defaults, { model: selectedCase, variant: id });
      return;
    }
    const request = ++modelRequest.current;
    setModelsLoading(true);
    setModelError("");
    try {
      const option = await ensureDescribed(defaults, {
        model: selectedCase,
        variant: id,
      });
      if (request !== modelRequest.current) return;
      mergeDescribed(
        {
          ...(listed as ModelOption),
          variant_defaults: {
            ...(listed?.variant_defaults || {}),
            [id]: option,
          },
        },
        selectedCase,
      );
      setSelectedVariant(id);
      setSelectedPreset(undefined);
      applyOption(option, { model: selectedCase, variant: id });
    } catch (e: unknown) {
      if (request === modelRequest.current)
        setModelError(e instanceof Error ? e.message : String(e));
    } finally {
      if (request === modelRequest.current) setModelsLoading(false);
    }
  }
  async function choosePreset(id?: string) {
    if (gate.current) return;
    if (!id) {
      setSelectedPreset(undefined);
      return;
    }
    const listed = models?.presets?.find((item: ModelOption) => item.id === id);
    if (!listed) return;
    if (optionReady(listed)) {
      setSelectedCase(listed.model_id);
      setSelectedVariant(listed.variant || undefined);
      setSelectedPreset(id);
      applyOption(listed, {
        preset: id,
        variant: listed.variant || undefined,
      });
      return;
    }
    const request = ++modelRequest.current;
    setModelsLoading(true);
    setModelError("");
    try {
      const option = await ensureDescribed(listed, { preset: id });
      if (request !== modelRequest.current) return;
      mergeDescribed(option);
      setSelectedCase(option.model_id);
      setSelectedVariant(option.variant || undefined);
      setSelectedPreset(id);
      applyOption(option, { preset: id, variant: option.variant || undefined });
    } catch (e: unknown) {
      if (request === modelRequest.current)
        setModelError(e instanceof Error ? e.message : String(e));
    } finally {
      if (request === modelRequest.current) setModelsLoading(false);
    }
  }
  return {
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
  };
}
