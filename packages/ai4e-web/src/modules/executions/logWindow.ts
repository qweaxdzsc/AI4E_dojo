/** 日志栏默认只渲染最近若干行，其余留在内存，避免整段正文撑死页面。 */
export const LOG_WINDOW = 500;

/** 只识别日志中显式的级别标记，历史原文不按内容猜测级别。 */
export function lineLevel(line: string) {
  return (
    line.match(/(?:^|\s)\[(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\](?:\s|$)/)?.[1] ||
    line.match(
      /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[,.]\d+)?\s+(DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)\s/,
    )?.[1] ||
    "未标注"
  );
}

/** 按已有级别和搜索过滤行，不改原文。 */
export function filterLogLines(lines: string[], level: string, search: string) {
  const needle = search.toLowerCase();
  return lines.filter(
    (line) =>
      (level === "全部" || lineLevel(line) === level) &&
      line.toLowerCase().includes(needle),
  );
}

/** 跟随模式下窗口起点：只露出末尾 window 行。 */
export function tailStart(total: number, window = LOG_WINDOW) {
  return Math.max(0, total - window);
}

/** 取消跟随时钉住起点，不超出可显示范围。 */
export function clampStart(start: number, total: number, window = LOG_WINDOW) {
  if (total <= 0) return 0;
  return Math.min(Math.max(0, start), tailStart(total, window));
}

/** 向上展开一页更早的行。 */
export function olderStart(start: number, window = LOG_WINDOW) {
  return Math.max(0, start - window);
}
