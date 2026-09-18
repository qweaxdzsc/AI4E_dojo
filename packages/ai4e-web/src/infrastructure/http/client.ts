/** 服务通信集中处理错误，失败不会成为成功状态。 */
export async function request<T = any>(
  path: string,
  body?: unknown,
  method?: string,
): Promise<T> {
  let r: Response;
  try {
    r = await fetch("/api/v1" + path, {
      method: method || (body === undefined ? "GET" : "POST"),
      headers: { "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error("无法连接 Dojo 后端服务，请确认服务已启动后重试。");
  }
  if (r.ok && r.status === 204) return undefined as T;
  // 开发代理断连可能返回空正文或 HTML；先读文本，避免解析异常盖过服务状态。
  let value: any;
  try {
    const text = await r.text();
    value = text.trim() ? JSON.parse(text) : undefined;
  } catch {
    value = undefined;
  }
  if (!r.ok) {
    const mapped = typeof value?.error?.message === "string" ? value.error.message.trim() : "";
    const detail = value?.detail;
    const fallback = r.status >= 500
      ? `Dojo 后端服务暂不可用（HTTP ${r.status}），请确认服务已启动后重试。`
      : `请求失败（HTTP ${r.status}），请重试。`;
    const error = new Error(mapped
      ? mapped
      : typeof detail === "string" && detail
      ? detail
      : detail != null ? JSON.stringify(detail) : fallback);
    Object.assign(error, { code: value?.error?.code, status: r.status });
    throw error;
  }
  if (value === undefined)
    throw new Error("Dojo 后端返回了空响应或无效数据，请刷新重试。");
  return value;
}
export const query = (values: Record<string, string | number | undefined>) =>
  "?" +
  new URLSearchParams(
    Object.entries(values)
      .filter(([, v]) => v !== undefined)
      .map(([k, v]) => [k, String(v)]),
  );
