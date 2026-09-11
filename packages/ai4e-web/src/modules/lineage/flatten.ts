export type FlatRow = { key: string; value: unknown };

/** 把创建快照里的嵌套配置摊平为可勾选参数行。 */
export function flattenEntries(value: unknown, prefix = ""): FlatRow[] {
  if (value == null || typeof value !== "object" || Array.isArray(value)) {
    return prefix ? [{ key: prefix, value }] : [];
  }
  return Object.entries(value as Record<string, unknown>).flatMap(([key, child]) =>
    flattenEntries(child, prefix ? prefix + "." + key : key),
  );
}

export function valueType(value: unknown): string {
  if (typeof value === "number" && Number.isFinite(value)) return "数值";
  if (typeof value === "boolean") return "文本";
  const text = typeof value === "string" ? value : "";
  if (text.includes("/") || /\.(json|ya?ml|pt|zarr|vtkhdf|vtp|npy)$/i.test(text)) return "文件";
  return "文本";
}

export function displayValue(value: unknown): string {
  if (value == null) return "—";
  if (typeof value === "string" || typeof value === "number" || typeof value === "boolean") return String(value);
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}
