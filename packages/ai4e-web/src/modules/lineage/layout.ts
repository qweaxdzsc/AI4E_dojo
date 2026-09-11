export const NODE_W = 230;
export const NODE_H = 80;
const GAP_X = 50;
const GAP_Y = 90;
const PAD = 40;

export type TreeNode = { id: string; parent?: string | null };
export type NodeBox = { id: string; x: number; y: number };

/** 按真实父版本分层排布，不使用原型固定坐标。 */
export function layoutTree(rows: TreeNode[]): { boxes: NodeBox[]; width: number; height: number } {
  const ids = new Set(rows.map((r) => r.id));
  const children = new Map<string, string[]>();
  for (const row of rows) {
    const parent = row.parent && ids.has(row.parent) ? row.parent : "";
    if (!children.has(parent)) children.set(parent, []);
    children.get(parent)!.push(row.id);
  }
  const boxes = new Map<string, NodeBox>();
  const nextX: number[] = [];
  function place(id: string, depth: number): NodeBox {
    const kids = children.get(id) || [];
    const y = PAD + depth * (NODE_H + GAP_Y);
    let x: number;
    if (!kids.length) {
      x = PAD + (nextX[depth] || 0);
    } else {
      const placed = kids.map((k) => place(k, depth + 1));
      x = (placed[0].x + placed[placed.length - 1].x) / 2;
      x = Math.max(x, PAD + (nextX[depth] || 0));
    }
    nextX[depth] = x - PAD + NODE_W + GAP_X;
    const box = { id, x, y };
    boxes.set(id, box);
    return box;
  }
  for (const root of children.get("") || []) place(root, 0);
  for (const orphan of rows) if (!boxes.has(orphan.id)) place(orphan.id, 0);
  const list = [...boxes.values()];
  const width = Math.max(920, ...list.map((b) => b.x + NODE_W + PAD), PAD);
  const height = Math.max(535, ...list.map((b) => b.y + NODE_H + PAD), PAD);
  return { boxes: list, width, height };
}

/** 父节点底边到子节点顶边的正交曲线，仅连接真实来源。 */
export function connectorPath(parent: NodeBox, child: NodeBox): string {
  const x1 = parent.x + NODE_W / 2;
  const y1 = parent.y + NODE_H;
  const x2 = child.x + NODE_W / 2;
  const y2 = child.y;
  const mid = (y1 + y2) / 2;
  return `M${x1} ${y1} V${mid - 8} Q${x1} ${mid} ${x1 + Math.sign(x2 - x1) * 20} ${mid} H${x2 - Math.sign(x2 - x1) * 20} Q${x2} ${mid} ${x2} ${mid + 8} V${y2}`;
}
