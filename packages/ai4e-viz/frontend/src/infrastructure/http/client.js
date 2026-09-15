/** 前端共享HTTP基座：只负责基础地址、超时、取消和统一错误，不包含业务Endpoint。 */

export const API_BASE = import.meta.env.VITE_API_BASE || (window.location.pathname.startsWith('/vis/') ? '/vis' : '');

/** 发送JSON请求并统一转换后端错误。 */
export async function requestJson(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), options.timeoutMs ?? 8000);
  const externalSignal = options.signal;
  const abortFromExternal = () => controller.abort();
  externalSignal?.addEventListener('abort', abortFromExternal, { once: true });
  try {
    const { timeoutMs: _timeoutMs, ...requestOptions } = options;
    const response = await fetch(`${API_BASE}${path}`, { ...requestOptions, signal: controller.signal });
    const body = await response.json().catch(() => null);
    if (!response.ok) {
      const error = new Error(body?.detail?.message || body?.detail || `${path} -> ${response.status}`);
      error.status = response.status;
      error.detail = body?.detail;
      throw error;
    }
    return body;
  } finally {
    clearTimeout(timer);
    externalSignal?.removeEventListener('abort', abortFromExternal);
  }
}

/** 生成供浏览器下载或嵌入使用的同源资源URL。 */
export function resourceUrl(path) {
  return `${API_BASE}${path}`;
}
