/** 与 viz `fit_graph_viewport` 同一替换：正式网络图按宽度适配，不把整图缩成细线。 */
const FIT_ENTIRE_GRAPH =
  "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;";
const FIT_WIDTH =
  "const scale = Math.min(1, (width * 0.92) / Math.max(graphWidth, 1));";
const CENTER_VERTICAL = "height / 2 - (minY + graphHeight / 2) * scale";
const TOP_ALIGN = "24 - minY * scale";

export function fitModelGraphViewport(html: string): string {
  if (!html.includes(FIT_ENTIRE_GRAPH)) return html;
  return html.replace(FIT_ENTIRE_GRAPH, FIT_WIDTH).replace(CENTER_VERTICAL, TOP_ALIGN);
}
