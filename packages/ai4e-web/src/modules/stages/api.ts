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
  target?: { model?: string; variant?: string; preset?: string },
) =>
  request(
    base(p, t) + "/configuration",
    {
      stage: s,
      expected_revision: revision,
      values,
      bindings,
      ...(target?.preset
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
export const modelAssetUrl = (p: string, value: any) =>
  `/api/v1/projects/${p}/assets/${value.result_refs[0].asset_id}/content?member=${encodeURIComponent(value.result.member)}&revision=${value.result_refs[0].revision}`;
export const resumeRun = (p: string, r: string) =>
  request(`/projects/${p}/runs/${r}/resume`, {});
export const stageInputs = (p: string, t: string) =>
  request(base(p, t) + "/stage-inputs");
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

/** 模型默认值与能力由官方模型或用户预设提供。 */
export const modelOptions = (p: string, t: string) =>
  request(base(p, t) + "/model-options");
export const exportModelPreset = (p: string, t: string, revision: string, name: string) =>
  request(base(p, t) + "/model-presets", { expected_revision: revision, name });
