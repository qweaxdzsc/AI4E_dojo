export type GraphView = {
  id: string;
  label: string;
  member: string;
  graph_nodes?: number;
};

/** 只有检查结果真正登记了两档成员才提供切换，历史单图不假装有第二档。 */
export function selectableGraphViews(result: any): GraphView[] {
  const views = result?.views;
  if (!views || typeof views !== "object" || Array.isArray(views)) return [];
  return Object.entries(views)
    .filter(([, value]) => value && typeof value === "object" && Boolean((value as any).member))
    .map(([id, value]) => ({
      id,
      label: String((value as any).label || id),
      member: String((value as any).member),
      graph_nodes:
        typeof (value as any).graph_nodes === "number"
          ? (value as any).graph_nodes
          : undefined,
    }));
}

export function selectedGraphMember(result: any, viewId?: string) {
  const views = selectableGraphViews(result);
  const current = views.find((item) => item.id === viewId) || views[0];
  return current?.member || result?.member;
}
