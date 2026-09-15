/** 数据资产模块Endpoint、请求和DTO转换。 */

import { API_BASE, requestJson } from '../../infrastructure/http/client.js';
import { toDataAsset } from './model.js';

/** 获取数据资产列表并兼容旧artifacts字段。 */
export async function apiArtifacts() {
  const body = await requestJson('/api/artifacts');
  const items = Array.isArray(body?.items) ? body.items : Array.isArray(body?.artifacts) ? body.artifacts : [];
  return { ...body, items: items.map(toDataAsset) };
}

export const apiArtifact = (artifactId) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}`);
export const apiClassifyArtifact = (artifactId, payload) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}/classification`, { method: 'PATCH', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });

/** 上传一个文件并返回首个数据资产入库结果。 */
export async function apiUpload(file, declaredKind) {
  const form = new FormData();
  form.append('files', file);
  if (declaredKind) form.append('declared_kind', declaredKind);
  const response = await fetch(`${API_BASE}/api/artifacts`, { method: 'POST', body: form });
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.detail || `upload -> ${response.status}`);
  return body.items?.[0] ?? body;
}
