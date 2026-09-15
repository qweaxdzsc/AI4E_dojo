/** 自动生成自 ai4e-spec/artifacts/platform.py；请勿手改。 */
export interface AssetRef {
  project_id: string;
  asset_id: string;
  revision: string;
  task_id?: string | null;
  run_id?: string | null;
  member?: string | null;
  block?: string | null;
}

export interface FieldDescriptor {
  field_id: string;
  name: string;
  member: string | null;
  association: "geometry" | "point" | "cell" | "global" | "array" | "column";
  shape: Array<number>;
  dtype: string;
  components: number;
  unit: string | null;
  entity_set: string | null;
  semantic_key: string | null;
}

export interface DatasetDescriptor {
  dataset_id: string;
  revision: string;
  samples: Array<Record<string, unknown>>;
  sources: Array<Record<string, unknown>>;
  fields: Array<FieldDescriptor>;
  dependencies: Array<Record<string, unknown>>;
  capabilities: Record<string, unknown>;
  profile?: Record<string, unknown>;
  inspection?: Record<string, unknown>;
  errors?: Array<Record<string, unknown>>;
  selection?: Array<string> | Record<string, Array<string>>;
}

export interface RawprepDescriptor {
  schema_version: number;
  dataset_id: string;
  defaults: Record<string, unknown>;
  binding: Record<string, unknown>;
  domains: Record<string, string>;
  outputs: Array<Record<string, unknown>>;
  geometry: Array<Record<string, unknown>>;
  filters: Array<Record<string, unknown>>;
  formats: Array<string>;
  vtkhdf: boolean;
  statistics_modes: Array<string>;
}

export interface ExtractionMember {
  source_field: string;
  output_member: string;
  components?: number;
}

export interface ExtractionOutput {
  id: string;
  name: string;
  members: Array<ExtractionMember>;
}

export interface ExtractionEntry {
  id: string;
  name: string;
  source_selector: Record<string, unknown>;
  outputs: Array<ExtractionOutput>;
}

export interface StageConfig {
  task_id: string;
  revision: string;
  stage: string;
  values: Record<string, unknown>;
  capabilities: Record<string, unknown>;
  readiness: Record<string, unknown>;
}

export interface StageOperationRequest {
  expected_revision: string;
  mode: "check" | "trial" | "execute";
  inputs: Array<AssetRef>;
  selection: Record<string, unknown>;
  idempotency_key: string;
}

export interface OperationError {
  code: string;
  message: string;
  location?: string;
}

export interface Operation {
  operation_id: string;
  kind: string;
  status: "queued" | "running" | "succeeded" | "failed" | "canceled" | "interrupted" | "stale";
  phase: string | null;
  progress: number | null;
  result_refs: Array<AssetRef>;
  error: OperationError | null;
  event_cursor: number;
  subscription_id?: string;
}

export interface VizRequest {
  protocol_version: 1;
  request_id: string;
  operation: "inspect" | "read_slice" | "summarize" | "transform";
  source: Record<string, unknown>;
  options: Record<string, unknown>;
  output_dir: string;
}

export interface BinaryBuffer {
  name: string;
  path: string;
  dtype: string;
  shape: Array<number>;
  byte_order: "little" | "big" | "not-applicable";
  byte_length: number;
  sha256: string;
}

export interface CoordinateSpace {
  id: string;
  unit: string;
  evidence: "source-declaration";
  source_refs: Array<AssetRef>;
}

export interface DisplayAssetManifest {
  schema_version: 1;
  source_refs: Array<Record<string, unknown>>;
  pipeline: Array<Record<string, unknown>>;
  dataset_type: string;
  bounds: Array<number>;
  geometry_buffers: Array<BinaryBuffer>;
  topology_buffers: Array<BinaryBuffer>;
  fields: Array<Record<string, unknown>>;
  entity_mapping: Record<string, unknown>;
  statistics: Record<string, unknown>;
  provenance: Record<string, unknown>;
  coordinate_space?: CoordinateSpace;
}

export interface SceneDocument {
  schema_version: 1;
  sources: Array<AssetRef>;
  pipeline_nodes: Array<Record<string, unknown>>;
  representations: Array<Record<string, unknown>>;
  viewports: Array<Record<string, unknown>>;
  link_groups: Array<Record<string, unknown>>;
  active_view: string | null;
  selected_node: string | null;
}

export interface VisualizationRef {
  visualization_id: string;
  project_id: string;
  task_id: string;
  revision: number;
  content_hash: string;
  kind: string;
}

export interface VisualizationSession {
  session_id: string;
  status: string;
  embed_url: string;
  scope_id: string | null;
  error?: string | null;
}

export interface VisualizationSourceRef {
  asset_id: string;
  revision: string;
  project_id?: string;
  task_id?: string | null;
  member?: string;
  block?: number;
}

export interface VisualizationExportRef {
  export_id: string;
  visualization_id: string;
  revision: number;
  content_hash: string;
  status: string;
  format: string;
}

export interface InferenceSampleSelection {
  split: string;
  sample: string;
}

export interface InferenceFieldDescription {
  id: string;
  domain: string;
  field: string;
  component: string;
  label: string;
  category: string;
  unit: string | null;
  available: boolean;
  evaluable: boolean;
  default: boolean;
  reason?: string;
}

export interface InferenceMetricDescription {
  id: string;
  label: string;
  category: string;
  formula: string;
  unit_rule: string;
  scope: string;
  default: boolean;
}

export interface InferenceStatistic {
  checkpoint_id: string;
  checkpoint: string;
  split: string;
  field_id: string;
  field: string;
  metric: string;
  unit: string | null;
  mean: number | null;
  median: number | null;
  p90: number | null;
  max: number | null;
  valid: number;
  expected: number;
  undefined: number;
  complete: boolean;
  prediction_seconds: number | null;
  throughput: number | null;
  algorithm?: string;
  checkpoint_revision?: string | null;
  source_runs?: Array<string>;
  source_protocols?: Array<string>;
  undefined_reasons?: Array<string>;
}
