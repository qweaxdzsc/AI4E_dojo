/** 可视化资产保存、预览、查询和导出API。 */

import { requestJson } from '../../infrastructure/http/client.js';

export const apiCreateArtifactVisualization = (artifactId, payload) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}/visualizations`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({...payload, context_id: currentStorageContext()}) });
export const apiPreviewArtifactVisualization = (artifactId, payload, signal) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}/visualizations/preview`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), signal });
export const apiVisualization = (visualizationId) => requestJson(`/api/visualizations/${encodeURIComponent(visualizationId)}${currentStorageContext() ? `?context_id=${encodeURIComponent(currentStorageContext())}` : ''}`);

/** 按数据集、类型和渲染器过滤可视化资产。 */
export function apiVisualizations(filters = {}) {
  const parameters = new URLSearchParams();
  if (currentStorageContext()) parameters.set("context_id", currentStorageContext());
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') parameters.set(key, String(value));
  });
  return requestJson(`/api/visualizations${parameters.size ? `?${parameters}` : ''}`);
}


/** 同一标签页保留明确选择的任务上下文，独立标签页互不切换。 */
export function currentStorageContext() {
  const selected = new URLSearchParams(window.location.hash.split('?')[1] || '').get('context');
  if(selected) sessionStorage.setItem('ai4e-vis-context', selected);
  return selected || sessionStorage.getItem('ai4e-vis-context') || '';
}
