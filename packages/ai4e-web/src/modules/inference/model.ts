/** 推理页面使用的轻量契约；数值计算与兼容判断来自服务。 */
export interface Checkpoint {
  id: string;
  run_id: string;
  name: string;
  revision: string;
  epoch?: number;
  updates?: number;
  created_at?: string;
  evaluation?: { value: number; metric: string; direction: string; split: string; protocol: string };
  size?: number;
  aliases?: string[];
  status: string;
  compatibility: { status: string; reason?: string };
  preparation?: any;
}
export interface Device {
  id: string;
  label: string;
  busy: boolean;
}
export interface Catalog {
  items: Checkpoint[];
  device_options: Device[];
  revision: string;
}
export interface Batch {
  id: string;
  name?: string;
  created_at?: string;
  status: string;
  total?: number;
  completed?: number;
  children: any[];
  inherited_children?: any[];
  files: any[];
  error?: string;
}
export interface ResultFile {
  name: string;
  path?: string;
  root?: string;
  task_id?: string;
  ref?: any;
  asset_id?: string;
  revision?: string;
}
export interface Result {
  run_id: string;
  checkpoint: any;
  sample: string;
  sample_id?: string;
  split?: string;
  files: ResultFile[];
  metrics: any;
  vtk?: { exported: boolean; reason?: string | null; kind?: string; sample_id?: string };
}
export type { InferenceFieldDescription as Field, InferenceMetricDescription as Metric, InferenceStatistic as Statistic } from "../../infrastructure/contracts/platform.generated";
import type { InferenceStatistic as Statistic } from "../../infrastructure/contracts/platform.generated";
export interface Results {
  statistics?: Statistic[];
  records?: any[];
  items: Result[];
  comparison: any;
}
export interface BatchRequest {
  name: string;
  expected_revision: string;
  checkpoints: { id: string; revision: string }[];
  sample_selection: { split: string; sample: string }[];
  fields?: string[];
  metrics?: string[];
  device: string;
  options: {
    evaluate: boolean;
    save_predictions: boolean;
    export_vtk: boolean;
    export_pointcloud: boolean;
    export_mesh: boolean;
    query_chunk_size: number;
  };
  idempotency_key: string;
}
const labels: Record<string, string> = {
  pending: "等待执行",
  queued: "等待执行",
  capturing: "固定输入",
  running: "运行中",
  succeeded: "成功",
  completed: "成功",
  partial: "部分失败",
  partially_failed: "部分失败",
  failed: "失败",
  canceled: "已取消",
  cancelled: "已取消",
  stopped: "已停止",
  stopping: "正在停止",
  interrupted: "已中断",
};
/** 未知状态保留原文，不能当作成功。 */
export const statusLabel = (status: string) =>
  labels[status] || status || "状态待核对";
/** 终态决定轮询与取消显示，不参与科研成功判断。 */
export const terminal = (status: string) =>
  [
    "succeeded",
    "completed",
    "partial",
    "partially_failed",
    "failed",
    "canceled",
    "cancelled",
    "stopped",
    "interrupted",
  ].includes(status);
/** 只放行服务明确判定兼容的候选。 */
export const compatible = (c: Checkpoint) =>
  ["compatible", "valid", "ok", "available"].includes(c.compatibility.status);
