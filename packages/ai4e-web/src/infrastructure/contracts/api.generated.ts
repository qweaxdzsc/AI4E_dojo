/** 自动生成：uv run packages/ai4e-web/scripts/generate-contracts.py。 */
export interface AssetRegistration {
  root: string;
  path: string;
  task_id?: string | null;
}
export interface CheckpointSelectionRequest {
  id: string;
  revision: string;
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
  edited_paths?: ((string)[])[] | null;
  removed_paths?: ((string)[])[] | null;
  processed_name?: string | null;
  profile?: Record<string, unknown> | null;
}
export interface ConfigurationEdit {
  expected_revision: string;
  values: Record<string, unknown>;
  edited_paths?: ((string)[])[] | null;
  removed_paths?: ((string)[])[] | null;
  stage: string;
  bindings?: Record<string, Record<string, unknown> | null>;
  target_case_id?: string | null;
  target_model?: string | null;
  target_variant?: string | null;
  target_preset?: string | null;
}
export interface DatasetEdit {
  expected_revision: string;
  sources?: Record<string, Record<string, unknown>> | null;
  dataset_id?: string | null;
  instance_id?: string | null;
}
export interface DifferenceRequest {
  task_id: string;
  expected_revision: string;
  inputs: (Record<string, unknown>)[];
  idempotency_key?: string | null;
}
export interface ExportRequest {
  format?: string;
  row_ids?: (string)[] | null;
}
export interface HTTPValidationError {
  detail?: (ValidationError)[];
}
export interface InferenceBatchRequest {
  expected_revision: string;
  checkpoints: (CheckpointSelectionRequest)[];
  name?: string;
  samples?: (string)[] | null;
  split?: string | null;
  sample_selection?: (SampleSelectionRequest)[] | null;
  fields?: (string)[] | null;
  metrics?: (string)[] | null;
  device?: string;
  options?: InferenceOptionsRequest | null;
  idempotency_key?: string | null;
}
export interface InferenceExportRequest {
  format: string;
  selection?: Record<string, unknown> | null;
}
export interface InferenceOptionsRequest {
  evaluate?: boolean;
  save_predictions?: boolean;
  export_vtk?: boolean;
  export_pointcloud?: boolean;
  export_mesh?: boolean;
  query_chunk_size?: number;
}
export interface MetricRequest {
  results: (ResultRef)[];
  fields: (string)[];
  metrics: (string)[];
  idempotency_key: string;
}
export interface ModelPresetCreate {
  expected_revision: string;
  name: string;
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
export interface ResultRef {
  id: string;
  revision: string;
}
export interface RetryRequest {
  idempotency_key?: string | null;
}
export interface SampleSelectionRequest {
  split: string;
  sample: string;
}
export interface Selection {
  revision: string;
  root?: string;
  files?: (string)[];
  all_selected?: boolean;
  count?: number | null;
  samples?: (string)[] | null;
  idempotency_key?: string | null;
  sample_scope?: Record<string, unknown> | null;
  catalog_revision?: string | null;
  overwrite_processed_name?: boolean;
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
  data_sources?: Record<string, Record<string, unknown>>;
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
