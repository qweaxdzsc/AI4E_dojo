/** 可视化任务模块的推荐、案例、工作台和Spec API。 */

import { currentStorageContext } from '../visIO/index.js';
import { requestJson } from '../../infrastructure/http/client.js';

/** 获取并校验5家族、19语义类型、23方法目录。 */
export async function apiCatalog() {
  const body = await requestJson('/api/catalog');
  if (body?.counts?.families !== 5 || body?.counts?.kinds !== 19 || body?.counts?.functions !== 23) throw new Error('catalog revision mismatch: expected 5/19/23');
  return body;
}

/** 获取并校验23种可视化方法。 */
export async function apiSpecs() {
  const body = await requestJson('/api/specs');
  if (!Array.isArray(body?.functions) || body.functions.length !== 23) throw new Error('function registry revision mismatch: expected 23 functions');
  return body;
}

export const apiExample = (artifactId, recommendationId) => requestJson(`/api/examples/${encodeURIComponent(artifactId)}${recommendationId ? `?recommendation_id=${encodeURIComponent(recommendationId)}` : ''}`);
/** 获取一个数据资产的确定性可视化推荐候选。 */
export const apiArtifactRecommendations = (artifactId) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}/recommendations`);
export const apiRendererHealth = () => requestJson('/api/renderer-health');
export const apiVisualization = (visualizationId) => requestJson(`/api/visualizations/${encodeURIComponent(visualizationId)}${currentStorageContext() ? `?context_id=${encodeURIComponent(currentStorageContext())}` : ''}`);
export const apiVisualizationSpecVersions = (specId) => requestJson(`/api/visualization-specs/${encodeURIComponent(specId)}/versions${currentStorageContext() ? `?context_id=${encodeURIComponent(currentStorageContext())}` : ''}`);
export const apiVisualizationSpecVersion = (specId, version) => requestJson(`/api/visualization-specs/${encodeURIComponent(specId)}/versions/${version}${currentStorageContext() ? `?context_id=${encodeURIComponent(currentStorageContext())}` : ''}`);
export const apiCreateVisualizationSpec = (payload) => requestJson('/api/visualization-specs', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({...payload, context_id: currentStorageContext()}) });
export const apiAppendVisualizationSpec = (specId, payload) => requestJson(`/api/visualization-specs/${encodeURIComponent(specId)}/versions${currentStorageContext() ? `?context_id=${encodeURIComponent(currentStorageContext())}` : ''}`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({...payload, context_id: currentStorageContext()}) });
