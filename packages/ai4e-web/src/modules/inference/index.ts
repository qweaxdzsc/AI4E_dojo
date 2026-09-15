/** 推理微领域公开门面：工作区、固定结果与服务适配。 */
export { InferenceWorkspace } from "./InferenceWorkspace";
export { InferenceResults } from "./InferenceResults";
export {
  listBatches as listInferenceBatches,
  results as inferenceResults,
  source as inferenceSource,
} from "./api";
export { statusLabel as inferenceStatusLabel } from "./model";
export type { Batch, Results, ResultFile } from "./model";
