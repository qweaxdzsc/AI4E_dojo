import type { ModelChoices, ModelOption } from "./useModelSelection";
import { request } from "../../infrastructure/http/client";
const base = (p: string, t: string) => `/projects/${p}/tasks/${t}`;
/** 阶段配置只保存用户选择，绑定通过服务解析受控引用后同修订保存。 */
export const readStage = (p: string, t: string, s: string) =>
  request(base(p, t) + `/configuration?stage=${s}`);
export const saveStage = (
  p: string,
  t: string,
  s: string,
  revision: string,
  values: unknown,
  bindings: Record<string, any> = {},
  target?: { model?: string; variant?: string; preset?: string; case?: string },
  edits?: { edited_paths: string[][]; removed_paths: string[][] },
) =>
  request(
    base(p, t) + "/configuration",
    {
      stage: s,
      expected_revision: revision,
      values,
      bindings,
      ...(["rawprep", "trainprep", "model", "train"].includes(s) ? edits : {}),
      ...(target?.case
        ? { target_case_id: target.case }
        : target?.preset
          ? { target_preset: target.preset }
          : target?.model
            ? {
                target_model: target.model,
                ...(target.variant ? { target_variant: target.variant } : {}),
              }
            : {}),
    },
    "PUT",
  );
/** 接收调用者稳定幂等键；响应丢失时重用原键，不新建研究运行。 */
export const runStage = async (
  p: string,
  t: string,
  s: string,
  revision: string,
  mode: string,
  selection: any = {},
  key: string = crypto.randomUUID(),
  accepted?: (value: any) => void,
) => {
  const result = await request(base(p, t) + `/stages/${s}/operations`, {
    expected_revision: revision,
    mode,
    selection,
    inputs: Object.values(selection.bindings || {}),
    idempotency_key: key,
  });
  accepted?.(result);
  return mode === "check" ? await waitOperation(p, result) : result;
};
export const traceModel = async (
  p: string,
  t: string,
  revision: string,
  bindings: Record<string, any> = {},
  key: string = crypto.randomUUID(),
  accepted?: (value: any) => void,
) => {
  const value = await request(base(p, t) + "/model-inspections", {
    expected_revision: revision,
    mode: "check",
    selection: {},
    inputs: [],
    idempotency_key: key,
  });
  accepted?.(value);
  return pollOperation(p, value);
};
export const modelAssetUrl = (p: string, value: any, member?: string) =>
  `/api/v1/projects/${p}/assets/${value.result_refs[0].asset_id}/content?member=${encodeURIComponent(member || value.result.member)}&revision=${value.result_refs[0].revision}`;
export const resumeRun = (p: string, r: string) =>
  request(`/projects/${p}/runs/${r}/resume`, {});
const stageInputLoads = new Map<
  string,
  { value?: any[]; pending?: Promise<any[]>; at?: number }
>();
const STAGE_INPUT_TTL_MS = 10_000;
/** 同任务在途请求合并，短时复用；避免切步重复扫检查点占住正式入口。 */
export const stageInputs = (p: string, t: string) => {
  const key = `${p}:${t}`;
  const current = stageInputLoads.get(key);
  if (
    current?.value &&
    current.at &&
    Date.now() - current.at < STAGE_INPUT_TTL_MS
  )
    return Promise.resolve(current.value);
  if (current?.pending) return current.pending;
  const pending = request(base(p, t) + "/stage-inputs")
    .then((value: any[]) => {
      stageInputLoads.set(key, { value, at: Date.now() });
      return value;
    })
    .catch((error) => {
      stageInputLoads.delete(key);
      throw error;
    });
  stageInputLoads.set(key, { pending });
  return pending;
};
/** 保存或执行后丢掉短时缓存，下一读走服务当前产物。 */
export const invalidateStageInputs = (p: string, t: string) => {
  stageInputLoads.delete(`${p}:${t}`);
};
/** 已提交检查重连后继续查询原操作；迟到响应不得产生新提交。 */
export async function pollOperation(p: string, value: any) {
  while (["queued", "running"].includes(value.status)) {
    await new Promise((r) => setTimeout(r, 300));
    value = await request(`/projects/${p}/operations/${value.operation_id}`);
  }
  if (value.status !== "succeeded")
    throw new Error(value.error?.message || value.status);
  return value;
}
export async function waitOperation(p: string, value: any) {
  return (await pollOperation(p, value)).result;
}

const modelOptionLoads = new Map<
  string,
  { value?: ModelChoices; pending?: Promise<ModelChoices>; at?: number }
>();
const MODEL_OPTION_TTL_MS = 10_000;
/** 同任务在途请求合并，短时复用；进页不重复描述全部候选。 */
export const peekModelOptions = (p: string, t: string) => {
  const current = modelOptionLoads.get(`${p}:${t}`);
  if (
    current?.value &&
    current.at &&
    Date.now() - current.at < MODEL_OPTION_TTL_MS
  )
    return current.value;
  return undefined;
};
/** 模型目录由官方模型或用户预设提供；完整能力在点选后再取。 */
export const modelOptions = (p: string, t: string) => {
  const key = `${p}:${t}`;
  const current = modelOptionLoads.get(key);
  if (
    current?.value &&
    current.at &&
    Date.now() - current.at < MODEL_OPTION_TTL_MS
  )
    return Promise.resolve(current.value);
  if (current?.pending) return current.pending;
  const pending = request<ModelChoices>(base(p, t) + "/model-options")
    .then((value) => {
      modelOptionLoads.set(key, { value, at: Date.now() });
      return value;
    })
    .catch((error) => {
      modelOptionLoads.delete(key);
      throw error;
    });
  modelOptionLoads.set(key, { pending });
  return pending;
};
/** 保存换模或导出后丢掉短时缓存，下一读走服务当前目录。 */
export const invalidateModelOptions = (p: string, t: string) => {
  modelOptionLoads.delete(`${p}:${t}`);
};
/** 点选后描述一份官方模型或预设，供参数草稿与能力同时替换。 */
export const describeModelOption = (
  p: string,
  t: string,
  selection: { model?: string; variant?: string; preset?: string },
) => {
  const query = new URLSearchParams();
  if (selection.model) query.set("model", selection.model);
  if (selection.variant) query.set("variant", selection.variant);
  if (selection.preset) query.set("preset", selection.preset);
  return request<ModelOption>(base(p, t) + "/model-option?" + query.toString());
};
export const exportModelPreset = (
  p: string,
  t: string,
  revision: string,
  name: string,
) =>
  request(base(p, t) + "/model-presets", { expected_revision: revision, name });
