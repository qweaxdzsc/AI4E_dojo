/** 报告编排前端领域模型：内容块、十二列布局以及撤销重做的纯状态变换。 */

const clone = (value) => JSON.parse(JSON.stringify(value));
const uid = (prefix) => `${prefix}-${globalThis.crypto?.randomUUID?.().slice(0, 10) ?? Math.random().toString(36).slice(2, 12)}`;

export const defaultLayout = (span = 12) => ({
  span, align: 'stretch', min_height: 120, page_break_before: false,
  keep_together: true, hidden: false
});

export function createBlock(type, seed = {}) {
  return {
    id: uid('block'), type, title: seed.title ?? '', body: seed.body ?? '',
    source_ref: seed.source_ref ?? null,
    layout: { ...defaultLayout(seed.span ?? 12), ...(seed.layout ?? {}) },
    display: { caption: '', alt_text: '', show_source: true, ...(seed.display ?? {}) },
    ...(type === 'metric' ? { value: seed.value ?? '—', unit: seed.unit ?? '' } : {}),
    ...(type === 'table' ? { columns: seed.columns ?? ['字段', '值'], rows: seed.rows ?? [['待补充', '—']] } : {})
  };
}

export function createRow(blocks = []) {
  return { id: uid('row'), gap: 16, align: 'start', blocks };
}

export function createSection(title = '未命名章节') {
  return { id: uid('section'), title, description: '', page_break_before: false, rows: [createRow()] };
}

export function locateBlock(document, blockId) {
  for (let sectionIndex = 0; sectionIndex < document.sections.length; sectionIndex += 1) {
    const section = document.sections[sectionIndex];
    for (let rowIndex = 0; rowIndex < section.rows.length; rowIndex += 1) {
      const blockIndex = section.rows[rowIndex].blocks.findIndex((block) => block.id === blockId);
      if (blockIndex >= 0) return { sectionIndex, rowIndex, blockIndex, section, row: section.rows[rowIndex], block: section.rows[rowIndex].blocks[blockIndex] };
    }
  }
  return null;
}

export function locateRow(document, rowId) {
  for (let sectionIndex = 0; sectionIndex < document.sections.length; sectionIndex += 1) {
    const rowIndex = document.sections[sectionIndex].rows.findIndex((row) => row.id === rowId);
    if (rowIndex >= 0) return { sectionIndex, rowIndex, section: document.sections[sectionIndex], row: document.sections[sectionIndex].rows[rowIndex] };
  }
  return null;
}

export function insertBlock(document, rowId, block, beforeBlockId = null) {
  const next = clone(document);
  let target = locateRow(next, rowId);
  if (!target) return document;
  const occupied = target.row.blocks.reduce((sum, item) => sum + Number(item.layout?.span ?? 12), 0);
  if (occupied >= 12) {
    const row = createRow();
    next.sections[target.sectionIndex].rows.splice(target.rowIndex + 1, 0, row);
    target = locateRow(next, row.id);
  }
  const available = 12 - target.row.blocks.reduce((sum, item) => sum + Number(item.layout?.span ?? 12), 0);
  block.layout = { ...defaultLayout(), ...(block.layout ?? {}), span: Math.min(Number(block.layout?.span ?? 12), available) };
  const index = beforeBlockId ? target.row.blocks.findIndex((item) => item.id === beforeBlockId) : -1;
  target.row.blocks.splice(index >= 0 ? index : target.row.blocks.length, 0, clone(block));
  return next;
}

export function moveBlock(document, blockId, targetRowId, beforeBlockId = null) {
  const next = clone(document);
  const source = locateBlock(next, blockId);
  let target = locateRow(next, targetRowId);
  if (!source || !target) return document;
  const [block] = source.row.blocks.splice(source.blockIndex, 1);
  const occupied = target.row.blocks.reduce((sum, item) => sum + Number(item.layout?.span ?? 12), 0);
  if (occupied >= 12) {
    const row = createRow();
    next.sections[target.sectionIndex].rows.splice(target.rowIndex + 1, 0, row);
    target = locateRow(next, row.id);
  }
  const available = 12 - target.row.blocks.reduce((sum, item) => sum + Number(item.layout?.span ?? 12), 0);
  block.layout.span = Math.min(Number(block.layout?.span ?? 12), available);
  const index = beforeBlockId ? target.row.blocks.findIndex((item) => item.id === beforeBlockId) : -1;
  target.row.blocks.splice(index >= 0 ? index : target.row.blocks.length, 0, block);
  return next;
}

export function updateBlock(document, blockId, patch) {
  const next = clone(document);
  const found = locateBlock(next, blockId);
  if (!found) return document;
  const value = typeof patch === 'function' ? patch(found.block) : patch;
  found.row.blocks[found.blockIndex] = { ...found.block, ...value };
  return next;
}

export function resizeBlock(document, blockId, requestedSpan) {
  const found = locateBlock(document, blockId);
  if (!found) return document;
  const occupiedByOthers = found.row.blocks.reduce((sum, item) => item.id === blockId ? sum : sum + Number(item.layout?.span ?? 12), 0);
  const span = Math.max(1, Math.min(Number(requestedSpan), 12 - occupiedByOthers));
  return updateBlock(document, blockId, { layout: { ...found.block.layout, span } });
}

export function removeBlock(document, blockId) {
  const next = clone(document);
  const found = locateBlock(next, blockId);
  if (!found) return document;
  found.row.blocks.splice(found.blockIndex, 1);
  return next;
}

export function duplicateBlock(document, blockId) {
  const next = clone(document);
  const found = locateBlock(next, blockId);
  if (!found) return document;
  const copy = clone(found.block);
  copy.id = uid('block');
  copy.title = copy.title ? `${copy.title} 副本` : '';
  found.row.blocks.splice(found.blockIndex + 1, 0, copy);
  return next;
}

export function addRow(document, sectionId) {
  const next = clone(document);
  const section = next.sections.find((item) => item.id === sectionId);
  if (section) section.rows.push(createRow());
  return next;
}

export function addSection(document, title = '新章节') {
  const next = clone(document);
  next.sections.push(createSection(title));
  return next;
}

export function updateSection(document, sectionId, patch) {
  const next = clone(document);
  const section = next.sections.find((item) => item.id === sectionId);
  if (section) Object.assign(section, patch);
  return next;
}

export function moveBlockByStep(document, blockId, direction) {
  const found = locateBlock(document, blockId);
  if (!found) return document;
  const rows = found.section.rows;
  const flat = rows.flatMap((row) => row.blocks.map((block) => ({ row, block })));
  const index = flat.findIndex((item) => item.block.id === blockId);
  const target = flat[index + direction];
  if (!target) return document;
  return moveBlock(document, blockId, target.row.id, direction < 0 ? target.block.id : null);
}

export const initialHistory = (document = null) => ({ past: [], present: document, future: [] });

export function historyReducer(state, action) {
  if (action.type === 'reset') return initialHistory(action.document);
  if (action.type === 'undo' && state.past.length) return { past: state.past.slice(0, -1), present: state.past.at(-1), future: [state.present, ...state.future] };
  if (action.type === 'redo' && state.future.length) return { past: [...state.past, state.present], present: state.future[0], future: state.future.slice(1) };
  if (action.type === 'change' && action.document !== state.present) return { past: [...state.past.slice(-49), state.present], present: action.document, future: [] };
  return state;
}

/** 固定报告素材的配置修订；后续保存或导出不能使旧报告引用漂移。 */
export function fixedVisualizationReference(asset, view = 0) {
  if (!asset.visualization_id || !Number.isInteger(asset.revision) || !asset.content_hash) throw new Error('报告素材必须具有固定配置修订');
  return { visualization_id: asset.visualization_id, revision: asset.revision, content_hash: asset.content_hash, project_id: asset.project_id, task_id: asset.task_id, view };
}
