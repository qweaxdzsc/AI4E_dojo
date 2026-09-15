import { request, query } from "../../infrastructure/http/client";
import type {
  Batch,
  BatchRequest,
  Catalog,
  Results,
  ResultFile,
  Field, Metric,
} from "./model";
const base = (p: string, t: string) =>
  `/projects/${encodeURIComponent(p)}/tasks/${encodeURIComponent(t)}/inference`;
function items(value: any): any[] {
  if (Array.isArray(value)) return value;
  if (Array.isArray(value?.items)) return value.items;
  throw new Error("推理服务返回的列表格式无效，请刷新重试");
}
function progress(value: any) {
  const p = value || {},
    ops = p.operations || {};
  const saved = ops.save?.status !== "skipped" ? ops.save : undefined;
  const record = saved || ops.predictions || ops.prediction;
  const active = Object.entries(ops).find(
    ([, v]: any) => v.status === "running",
  );
  const samples = (active?.[1] as any)?.samples || [];
  const unit = samples.find((s: any) => s.status === "running");
  return {
    ...p,
    completed: p.completed ?? record?.completed,
    total: p.total ?? record?.expected,
    operation: p.operation || active?.[0],
    sample: p.sample || unit?.samples?.join(", "),
  };
}
function batch(value: any): Batch {
  const v = value?.batch || value;
  if (!v?.id || !v?.status) throw new Error("推理批次缺少身份或状态");
  return {
    ...v,
    children: (v.children || []).map((c: any) => ({
      ...c,
      progress: progress(c.progress),
    })),
    files: v.files || [],
  };
}
/** 过渡期响应差异只在 adapter 转换，缺失兼容信息保持不可用。 */
export async function checkpoints(p: string, t: string): Promise<Catalog> {
  const v = await request(base(p, t) + "/checkpoints");
  return {
    items: items(v).map((c) => ({
      ...c,
      name: c.name || c.id,
      compatibility:
        typeof c.compatibility === "string"
          ? { status: c.compatibility }
          : c.compatibility || {
              status: "unknown",
              reason: "尚无兼容检查结果",
            },
    })),
    device_options: v.device_options || [],
    revision: v.revision,
  };
}
/** 样本只来自检查点对应的准备声明。 */
export async function samples(p: string, t: string, id: string) {
  const v = await request(
    base(p, t) + "/samples" + query({ checkpoint_id: id }),
  );
  if (v.compatibility?.status === "invalid")
    throw new Error(v.compatibility.reason || "准备记录与当前模型不兼容");
  if (!v.partitions || typeof v.partitions !== "object")
    throw new Error("准备记录缺少样本分片");
  return v as { selection_supported?: boolean; preparation: any; partitions: Record<string, string[]>; fields: Field[]; metrics: Metric[] };
}
export const check = (p: string, t: string, body: BatchRequest) =>
  request(base(p, t) + "/check", body);
export const submit = async (p: string, t: string, body: BatchRequest) =>
  batch(await request(base(p, t) + "/batches", body));
export const listBatches = async (p: string, t: string): Promise<Batch[]> =>
  items(await request(base(p, t) + "/batches")).map(batch);
export const getBatch = async (p: string, t: string, id: string) =>
  batch(await request(base(p, t) + "/batches/" + encodeURIComponent(id)));
export const cancel = (p: string, t: string, id: string) =>
  request(base(p, t) + "/batches/" + encodeURIComponent(id) + "/cancel", {});
/** 显式核对丢失的协调进程，服务负责幂等恢复。 */
export const recover = (p: string, t: string, id: string) =>
  request(base(p, t) + "/batches/" + encodeURIComponent(id) + "/recover", {});
export const retry = async (p: string, t: string, id: string, key: string) =>
  batch(
    await request(
      base(p, t) + "/batches/" + encodeURIComponent(id) + "/retry",
      { idempotency_key: key },
    ),
  );
/** 比较数值及可比原因原样交付，浏览器不重新累计指标。 */
export async function results(
  p: string,
  t: string,
  id: string,
): Promise<Results> {
  const v = await request(
    base(p, t) + "/batches/" + encodeURIComponent(id) + "/results",
  );
  return {
    items: items(v).map((r) => ({
      ...r,
      sample: String(r.sample ?? r.sample_id ?? ""),
      files: r.files || [],
    })),
    comparison: v.comparison,
    statistics: v.statistics || [],
    records: v.records || [],
  };
}
/** 固定文件交给现有资产服务；浏览器不解释服务器目录。 */
export async function source(p: string, t: string, file: ResultFile) {
  if (file.ref?.asset_id) return { ...file.ref, name: file.name };
  if (file.asset_id) return { ...file, name: file.name };
  if (!file.root || !file.path) throw new Error("结果缺少受控文件引用");
  return {
    ...(await request(`/projects/${p}/assets`, {
      root: file.root,
      path: file.path,
      task_id: file.task_id || t,
    })),
    name: file.name,
  };
}
export function download(p: string, t: string, file: ResultFile) {
  const ref = file.ref || file;
  if (ref.asset_id)
    return (
      `/api/v1/projects/${p}/assets/${encodeURIComponent(ref.asset_id)}/content` +
      query({ revision: ref.revision, download: "true" })
    );
  if (file.root && file.path)
    return (
      `/api/v1/projects/${p}/files/download` +
      query({ root: file.root, path: file.path, task_id: file.task_id || t })
    );
  return undefined;
}

/** 导出固定批次数值，返回现有受控下载引用。 */
export const exportResults = (p: string, t: string, id: string, format: string, selection: any) =>
  request(base(p, t) + "/batches/" + encodeURIComponent(id) + "/exports", { format, selection });
