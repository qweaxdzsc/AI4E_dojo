/** 与训练 run 一样用本地墙钟精确到秒，便于区分同名多次推理。 */
const GENERIC_BATCH_NAME = /^(批量推理|推理)$/;
const INFER_STAMP = /^infer-\d{8}-\d{6}$/;

export type InferenceBatchIdentity = {
  id: string;
  name?: string;
  created_at?: string;
};

/** 新批次默认身份：`infer-YYYYMMDD-HHMMSS`。 */
export function defaultInferenceBatchName(now = new Date()): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `infer-${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}-${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
}

export function isInferBatchStamp(name: string): boolean {
  return INFER_STAMP.test(name.trim());
}

/** 旧「批量推理」有创建时间则格式化成 infer 身份；自定义名称原样保留。 */
export function inferenceBatchLabel(batch: InferenceBatchIdentity): string {
  const name = (batch.name || "").trim();
  if (name && !GENERIC_BATCH_NAME.test(name)) return name;
  if (batch.created_at) {
    const at = new Date(batch.created_at);
    if (!Number.isNaN(at.getTime())) return defaultInferenceBatchName(at);
  }
  return name || batch.id.slice(0, 12);
}
