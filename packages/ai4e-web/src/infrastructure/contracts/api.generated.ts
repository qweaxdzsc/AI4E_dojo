/** 自动生成：uv run packages/ai4e-web/scripts/generate-contracts.py。 */
export interface AssetRegistration {
  root: string;
  path: string;
  task_id?: string | null;
}
export interface Compare {
  mode: string;
  left: string;
  right?: string | null;
  parameter?: string | null;
}
export interface ConfigEdit {
  revision: string;
  rawprep: Record<string, unknown>;
}
export interface ConfigurationEdit {
  expected_revision: string;
  values: Record<string, unknown>;
  stage: string;
}
export interface DatasetEdit {
  expected_revision: string;
  sources: Record<string, unknown>;
}
export interface DifferenceRequest {
  task_id: string;
  expected_revision: string;
  inputs: (Record<string, unknown>)[];
  idempotency_key?: string | null;
}
export interface HTTPValidationError {
  detail?: (ValidationError)[];
}
export interface PreviewOperation {
  source: Record<string, unknown>;
  operation?: string;
  options?: Record<string, unknown>;
  idempotency_key?: string | null;
}
export interface ProjectEdit {
  name?: string | null;
  description?: string | null;
  archived?: boolean | null;
}
export interface Report {
  title: string;
  text?: string;
  run_ids?: (string)[];
}
export interface Selection {
  revision: string;
  root: string;
  files: (string)[];
  all_selected?: boolean;
  count?: number | null;
  samples?: (string)[] | null;
  idempotency_key?: string | null;
}
export interface StageOperation {
  expected_revision: string;
  mode: string;
  inputs?: (Record<string, unknown>)[];
  selection?: Record<string, unknown>;
  idempotency_key?: string | null;
}
export interface TaskCreate {
  name?: string | null;
  description?: string | null;
  archived?: boolean | null;
  case_id?: string | null;
  data_root?: string | null;
  data_path?: string;
  data_sources?: Record<string, unknown>;
}
export interface TaskEdit {
  name?: string | null;
  description?: string | null;
  archived?: boolean | null;
}
export interface ValidationError {
  loc: (string | number)[];
  msg: string;
  type: string;
  input?: unknown;
  ctx?: Record<string, unknown>;
}
