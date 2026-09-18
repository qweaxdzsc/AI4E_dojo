import type { Field, Metric } from "./model";

/** 检查点关联的样本、物理量与指标目录。 */
export type SampleCatalog = {
  partitions: Record<string, string[]>;
  fields?: Field[];
  metrics?: Metric[];
  selection_supported?: boolean;
  vtk_exports?: {
    pointcloud?: { available?: boolean; include_truth?: boolean; reason?: string | null };
    mesh?: {
      available?: boolean;
      include_truth?: boolean;
      structured?: boolean;
      reason?: string | null;
    };
  };
};

/** 比较各检查点目录是否同一套样本、物理量和指标。 */
export function catalogFingerprint(value: SampleCatalog): string {
  const partitions = Object.fromEntries(
    Object.keys(value.partitions || {})
      .sort()
      .map((key) => [key, [...(value.partitions[key] || [])].sort()]),
  );
  return JSON.stringify({
    partitions,
    fields: (value.fields || []).map((item) => [item.id, !!item.available]).sort(),
    metrics: (value.metrics || []).map((item) => item.id).sort(),
    selection_supported: value.selection_supported !== false,
  });
}

/** 全部检查点目录一致时才能进页共用，否则回退到先选检查点。 */
export function sameSampleCatalog(items: SampleCatalog[]): boolean {
  if (!items.length) return true;
  const first = catalogFingerprint(items[0]);
  return items.every((item) => catalogFingerprint(item) === first);
}

export type SharedCatalogResult = {
  catalog?: SampleCatalog;
  mismatch: boolean;
};

/** 其余检查点全部成功且与第一份相同才算共用目录。 */
export async function remainingCatalogsMatch(
  load: (id: string) => Promise<SampleCatalog>,
  ids: string[],
  first: SampleCatalog,
): Promise<boolean> {
  if (ids.length <= 1) return true;
  const rest = await Promise.allSettled(ids.slice(1).map((id) => load(id)));
  const rows = rest.flatMap((item) => (item.status === "fulfilled" ? [item.value] : []));
  return rest.every((item) => item.status === "fulfilled") && sameSampleCatalog([first, ...rows]);
}

/** 先取第一份兼容目录填屏，再核对其余；失败或不一致只回退，不让整页空白。 */
export async function loadSharedCatalog(
  load: (id: string) => Promise<SampleCatalog>,
  ids: string[],
): Promise<SharedCatalogResult> {
  if (!ids.length) return { mismatch: false };
  const first = await load(ids[0]);
  if (await remainingCatalogsMatch(load, ids, first)) return { catalog: first, mismatch: false };
  return { catalog: first, mismatch: true };
}
