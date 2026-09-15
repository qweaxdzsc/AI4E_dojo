/** 物理场工作区协议适配；请求只携带上下文身份，不传机器路径。 */
import { requestJson, resourceUrl } from '../../infrastructure/http/client.js';

/** 调用与当前来源和任务绑定的可视化 API。 */
export const physApi = {
  append: (context, session, assetId, member='') => requestJson(`/api/phys/sessions/${session}/sources`, {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({context_id:context,asset_id:assetId,member}),timeoutMs:150000}),
  context: (id) => requestJson(`/api/contexts/${encodeURIComponent(id)}`),
  create: (context, spec, renderer) => requestJson('/api/phys/sessions', { method: 'POST', body: JSON.stringify({ context_id: context, ...(renderer ? {renderer} : {}), ...(spec ? { spec } : {}) }), headers: { 'Content-Type': 'application/json' }, timeoutMs: 90000 }),
  command: (context, session, command) => requestJson(`/api/phys/sessions/${session}/commands`, { method: 'POST', body: JSON.stringify({ context_id: context, command }), headers: { 'Content-Type': 'application/json' }, timeoutMs: 150000 }),
  close: (context, session) => requestJson(`/api/phys/sessions/${session}?context_id=${encodeURIComponent(context)}`, { method: 'DELETE' }),
  release: (context, session) => fetch(resourceUrl(`/api/phys/sessions/${session}?context_id=${encodeURIComponent(context)}`), {method:'DELETE', keepalive:true}),
  heartbeat: (context, session) => requestJson(`/api/phys/sessions/${session}/heartbeat`, { method: 'POST', body: JSON.stringify({ context_id: context }), headers: { 'Content-Type': 'application/json' } }),
  list: (context) => requestJson(`/api/visualizations?context_id=${encodeURIComponent(context)}`),
  read: (context, id) => requestJson(`/api/visualizations/${id}?context_id=${encodeURIComponent(context)}`),
  save: (context, body) => requestJson('/api/visualizations', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ ...body, context_id: context }) }),
  export: (context, id, revision, options) => requestJson(`/api/visualizations/${id}/exports`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ context_id: context, revision, options }) }),
  status: (context, id, output) => requestJson(`/api/visualizations/${id}/exports/${output}?context_id=${encodeURIComponent(context)}`),
  cancel: (context, id, output) => requestJson(`/api/visualizations/${id}/exports/${output}/cancel`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ context_id: context }) }),
  download: (context, id, output, name) => resourceUrl(`/api/visualizations/${id}/exports/${output}/files/${encodeURIComponent(name)}?context_id=${encodeURIComponent(context)}`),
  record: async (context, id, revision, blob) => {
    const result = await fetch(resourceUrl(`/api/visualizations/${id}/recordings?context_id=${encodeURIComponent(context)}&revision=${revision}`), { method: 'POST', headers: { 'Content-Type': 'video/webm' }, body: blob });
    const body = await result.json();
    if (!result.ok) throw new Error(body.detail);
    return body;
  },
};

/** 工作区资源与 WebSocket 共用受控代理前缀。 */
export function viewUrl(context, session, secret) {
  const path = resourceUrl(`/api/phys/view/${encodeURIComponent(context)}/${session}/`);
  const socket = new URL(path + 'ws', window.location.href);
  socket.protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return path + '?' + new URLSearchParams({ sessionURL: socket.href, secret });
}
