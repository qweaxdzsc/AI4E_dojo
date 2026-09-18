import { compatible, type Checkpoint } from "./model";

export const UNASSIGNED_RUN = "__unassigned__";

export type CheckpointRunGroup = {
  key: string;
  runId: string;
  label: string;
  status?: string;
  createdAt?: string;
  items: Checkpoint[];
};

/** 父级只显示服务给出的 run_id 短号，缺身份单独成组，不由文件名猜测所属运行。 */
export function runGroupLabel(runId: string): string {
  const id = runId.trim();
  if (!id) return "未归属运行";
  return "训练运行 · " + id.slice(0, 8);
}

export function runGroupKey(runId?: string): string {
  return (runId || "").trim() || UNASSIGNED_RUN;
}

/** 按服务 run_id 收成树；顺序跟随已排好的检查点，不重排运行。 */
export function groupCheckpointsByRun(items: Checkpoint[]): CheckpointRunGroup[] {
  const order: string[] = [];
  const buckets = new Map<string, Checkpoint[]>();
  for (const item of items) {
    const key = runGroupKey(item.run_id);
    if (!buckets.has(key)) {
      buckets.set(key, []);
      order.push(key);
    }
    buckets.get(key)!.push(item);
  }
  return order.map((key) => {
    const rows = buckets.get(key)!;
    const runId = key === UNASSIGNED_RUN ? "" : key;
    return {
      key,
      runId,
      label: runGroupLabel(runId),
      status: rows.find((row) => row.status)?.status,
      createdAt: rows.find((row) => row.created_at)?.created_at,
      items: rows,
    };
  });
}

/** 全选与选父级都只操作兼容检查点叶子，不把运行节点写进提交名单。 */
export function compatibleIds(items: Checkpoint[]): string[] {
  return items.filter(compatible).map((item) => item.id);
}
