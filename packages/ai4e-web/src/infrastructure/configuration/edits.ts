/** 对比已读取草稿与当前草稿，保留空值、空映射和删除的不同含义。路径不按点拆分。 */
export function configurationEdits(before: any, after: any) {
  const edited_paths: string[][] = [];
  const removed_paths: string[][] = [];
  const mapping = (value: any) => value !== null && typeof value === "object" && !Array.isArray(value);
  function visit(old: any, next: any, path: string[]) {
    if (JSON.stringify(old) === JSON.stringify(next)) return;
    if (mapping(old) && mapping(next) && Object.keys(next).length > 0) {
      for (const key of new Set([...Object.keys(old), ...Object.keys(next)])) {
        if (!(key in next)) removed_paths.push([...path, key]);
        else if (!(key in old)) edited_paths.push([...path, key]);
        else visit(old[key], next[key], [...path, key]);
      }
    } else edited_paths.push(path);
  }
  for (const key of new Set([...Object.keys(before || {}), ...Object.keys(after || {})])) {
    if (!(key in (after || {}))) removed_paths.push([key]);
    else if (!(key in (before || {}))) edited_paths.push([key]);
    else visit(before[key], after[key], [key]);
  }
  return { edited_paths, removed_paths };
}
