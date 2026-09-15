/** 报告编排页面：组织布局、拖拽、历史操作、草稿和冻结。 */

import { useCallback, useEffect, useMemo, useReducer, useRef, useState } from 'react';
import {
  Alert, App as AntApp, Button, Divider, Dropdown, Empty, Input, InputNumber, Modal,
  Result, Select, Skeleton, Space, Switch, Tabs, Tag, Tooltip
} from 'antd';
import {
  ArrowDownOutlined, ArrowLeftOutlined, ArrowUpOutlined, BarsOutlined, CopyOutlined,
  DeleteOutlined, DownloadOutlined, EyeOutlined, FileAddOutlined, LeftOutlined,
  MenuOutlined, RedoOutlined, RightOutlined, SaveOutlined, UndoOutlined
} from '@ant-design/icons';
import {
  DndContext, KeyboardSensor, PointerSensor, closestCenter, useDraggable, useDroppable,
  useSensor, useSensors
} from '@dnd-kit/core';
import { SortableContext, sortableKeyboardCoordinates, useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Link, useParams } from 'react-router-dom';
import { apiFreezeReport, apiQuartoHealth, apiReportDraft, apiSaveReportDraft } from '../api.js';
import { apiCreateReportExport, apiReportExport, reportExportDownloadUrl } from '../../reportManage/index.js';
import { apiVisualizations } from '../../visIO/index.js';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';
import {
  addRow, addSection, createBlock, duplicateBlock, historyReducer, initialHistory,
  insertBlock, locateBlock, locateRow, moveBlock, moveBlockByStep, removeBlock,
  resizeBlock, updateBlock, updateSection, fixedVisualizationReference
} from '../domain/reportDocument.js';

const BLOCK_LABELS = {
  markdown: '文字', visualization: '可视化结果', metric: '指标', table: '表格', image: '图片',
  video: '视频', callout: '提示框', divider: '分隔线', toc: '目录', source: '来源', page_break: '分页'
};
const LIBRARY_TYPES = ['markdown', 'metric', 'table', 'image', 'video', 'callout', 'divider', 'toc', 'source', 'page_break'];

function visualizationBlock(item) {
  return createBlock('visualization', {
    title: item.name,
    body: item.takeaway || '',
    source_ref: item.revision ? fixedVisualizationReference(item) : {
      artifact_id: item.artifact_id, visualization_id: item.visualization_id,
      spec_id: item.spec_id, spec_version: item.spec_version, content_hash: item.content_hash
    },
    display: { caption: item.takeaway || '', alt_text: `${item.name} 可视化`, show_source: true }
  });
}

function LibraryItem({ id, label, subtitle, onAdd }) {
  const { attributes, listeners, setNodeRef, transform, isDragging } = useDraggable({ id, data: { library: true } });
  return <div ref={setNodeRef} className={`report-library-item ${isDragging ? 'is-dragging' : ''}`} style={{ transform: CSS.Translate.toString(transform) }}>
    <button className="library-drag-handle" type="button" {...listeners} {...attributes} aria-label={`拖动 ${label}`}><BarsOutlined /></button>
    <div><strong>{label}</strong>{subtitle ? <small title={subtitle}>{subtitle}</small> : null}</div>
    <Button type="text" size="small" onClick={onAdd}>添加</Button>
  </div>;
}

function SortableBlock({ block, selected, onSelect, onMove, onResize }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id: block.id, data: { block: true } });
  const source = block.source_ref;
  return <article ref={setNodeRef} className={`report-canvas-block ${selected ? 'is-selected' : ''} ${isDragging ? 'is-dragging' : ''}`} style={{ gridColumn: `span ${block.layout?.span ?? 12}`, transform: CSS.Transform.toString(transform), transition }} onClick={() => onSelect(block.id)} aria-label={`${BLOCK_LABELS[block.type] ?? block.type}块：${block.title || '未命名'}`}>
    <header><button type="button" className="block-drag-handle" {...attributes} {...listeners} aria-label="拖动或使用键盘移动块"><BarsOutlined /></button><Tag>{BLOCK_LABELS[block.type] ?? block.type}</Tag><strong>{block.title || '未命名块'}</strong></header>
    {block.type === 'visualization' ? <div className="block-viz-preview"><EyeOutlined /><span>{block.body || '已保存可视化结果'}</span><code>结果 ID：{source?.visualization_id}</code></div> : block.type === 'metric' ? <div className="block-metric-preview"><b>{block.value}</b><span>{block.unit}</span></div> : block.type === 'divider' ? <Divider /> : block.type === 'page_break' ? <div className="block-page-break">—— 导出时分页 ——</div> : <p>{block.body || (block.type === 'toc' ? '导出时自动生成目录' : '在右侧检查器中编辑内容')}</p>}
    <footer><span>{block.layout?.span ?? 12}/12 列</span><Space.Compact><Tooltip title="上移"><Button size="small" aria-label="上移块" icon={<ArrowUpOutlined />} onClick={(event) => { event.stopPropagation(); onMove(-1); }} /></Tooltip><Tooltip title="下移"><Button size="small" aria-label="下移块" icon={<ArrowDownOutlined />} onClick={(event) => { event.stopPropagation(); onMove(1); }} /></Tooltip><Select aria-label="块宽度" size="small" value={block.layout?.span ?? 12} onClick={(event) => event.stopPropagation()} onChange={onResize} options={[3, 4, 6, 8, 9, 12].map((value) => ({ value, label: `${value}/12` }))} /></Space.Compact></footer>
  </article>;
}

function CanvasRow({ row, selectedId, onSelect, onMove, onResize }) {
  const { setNodeRef, isOver } = useDroppable({ id: row.id, data: { row: true } });
  return <div ref={setNodeRef} className={`report-canvas-row ${isOver ? 'is-over' : ''}`} data-row-id={row.id}>
    <SortableContext items={row.blocks.map((block) => block.id)}>{row.blocks.map((block) => <SortableBlock key={block.id} block={block} selected={selectedId === block.id} onSelect={onSelect} onMove={(direction) => onMove(block.id, direction)} onResize={(span) => onResize(block.id, span)} />)}</SortableContext>
    {!row.blocks.length ? <div className="report-row-empty">拖入素材，或从左侧点击“添加”</div> : null}
  </div>;
}

function InspectorSwitch({ label, checked, onChange }) {
  return <div className="inspector-switch" onClick={(event) => {
    if (!event.target.closest('.ant-switch')) onChange(!checked);
  }}><span>{label}</span><Switch checked={checked} onChange={onChange} /></div>;
}

function Inspector({ document, selectedId, apply, onDelete, onDuplicate, onClose }) {
  const found = selectedId ? locateBlock(document, selectedId) : null;
  if (!found) return <div className="report-inspector-empty"><RightOutlined /><p>选择一个报告块后，在这里编辑内容、尺寸、分页与来源设置。</p></div>;
  const block = found.block;
  const change = (patch) => apply(updateBlock(document, block.id, patch));
  const changeLayout = (patch) => change({ layout: { ...block.layout, ...patch } });
  const changeDisplay = (patch) => change({ display: { ...block.display, ...patch } });
  return <div className="report-inspector-form">
    <div className="panel-mobile-heading"><strong>块检查器</strong><Button type="text" aria-label="关闭检查器" icon={<RightOutlined />} onClick={onClose} /></div>
    <label>标题<Input value={block.title} onChange={(event) => change({ title: event.target.value })} /></label>
    {!['divider', 'toc', 'page_break', 'visualization'].includes(block.type) ? <label>内容<Input.TextArea value={block.body} autoSize={{ minRows: 5, maxRows: 14 }} onChange={(event) => change({ body: event.target.value })} /></label> : null}
    {block.type === 'metric' ? <Space.Compact block><label>指标值<Input value={block.value} onChange={(event) => change({ value: event.target.value })} /></label><label>单位<Input value={block.unit} onChange={(event) => change({ unit: event.target.value })} /></label></Space.Compact> : null}
    <Divider orientation="left">布局</Divider>
    <label>宽度<Select value={block.layout.span} onChange={(span) => apply(resizeBlock(document, block.id, span))} options={Array.from({ length: 12 }, (_, index) => ({ value: index + 1, label: `${index + 1}/12 列` }))} /></label>
    <label>最小高度<Space.Compact block><InputNumber style={{ width: '100%' }} min={80} max={1200} step={20} value={block.layout.min_height} onChange={(min_height) => changeLayout({ min_height })} /><Button disabled>px</Button></Space.Compact></label>
    <label>对齐<Select value={block.layout.align} onChange={(align) => changeLayout({ align })} options={['stretch', 'start', 'center', 'end'].map((value) => ({ value, label: value }))} /></label>
    <InspectorSwitch label="块前分页" checked={block.layout.page_break_before} onChange={(page_break_before) => changeLayout({ page_break_before })} />
    <InspectorSwitch label="尽量保持同页" checked={block.layout.keep_together} onChange={(keep_together) => changeLayout({ keep_together })} />
    <InspectorSwitch label="在导出中隐藏" checked={block.layout.hidden} onChange={(hidden) => changeLayout({ hidden })} />
    <Divider orientation="left">说明与来源</Divider>
    <label>说明<Input.TextArea value={block.display?.caption ?? ''} onChange={(event) => changeDisplay({ caption: event.target.value })} /></label>
    <label>替代文本<Input.TextArea value={block.display?.alt_text ?? ''} onChange={(event) => changeDisplay({ alt_text: event.target.value })} /></label>
    <InspectorSwitch label="显示来源" checked={block.display?.show_source !== false} onChange={(show_source) => changeDisplay({ show_source })} />
    {block.source_ref ? <div className="frozen-source"><b>冻结引用</b><span>数据资产 ID <code>{block.source_ref.artifact_id}</code></span><span>可视化结果 ID <code>{block.source_ref.visualization_id}</code></span><span>可视化配置 ID / 版本 <code>{block.source_ref.spec_id} / v{block.source_ref.spec_version}</code></span><small>内容哈希 sha256:{block.source_ref.content_hash?.slice(0, 16)}…</small></div> : null}
    <Space wrap><Button icon={<CopyOutlined />} onClick={onDuplicate}>复制块</Button><Button danger icon={<DeleteOutlined />} onClick={onDelete}>删除块</Button></Space>
  </div>;
}

export default function ReportComposerPage() {
  const { reportId } = useParams();
  const { message } = AntApp.useApp();
  const [loading, setLoading] = useState(true);
  const [record, setRecord] = useState(null);
  const [visualizations, setVisualizations] = useState([]);
  const [quarto, setQuarto] = useState(null);
  const [history, dispatch] = useReducer(historyReducer, initialHistory());
  const [selectedId, setSelectedId] = useState(null);
  const [dirty, setDirty] = useState(false);
  const [saveState, setSaveState] = useState('saved');
  const [mobilePanel, setMobilePanel] = useState(null);
  const [exportTask, setExportTask] = useState(null);
  const revisionRef = useRef(null);
  const savingRef = useRef(false);
  const editSequenceRef = useRef(0);
  const sensors = useSensors(useSensor(PointerSensor, { activationConstraint: { distance: 6 } }), useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }));

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [draft, library, health] = await Promise.all([apiReportDraft(reportId), apiVisualizations(), apiQuartoHealth().catch(() => ({ state: 'offline' }))]);
      setRecord(draft); revisionRef.current = draft.draft_revision; dispatch({ type: 'reset', document: draft.document });
      setVisualizations(library.items ?? []); setQuarto(health); setDirty(false); setSaveState('saved');
    } catch (error) { setRecord(null); if (error.status !== 404) message.error(error.message); }
    finally { setLoading(false); }
  }, [message, reportId]);
  useEffect(() => { load(); }, [load]);

  const markDirty = useCallback(() => {
    editSequenceRef.current += 1;
    setDirty(true);
    setSaveState('dirty');
  }, []);
  const apply = useCallback((document) => { dispatch({ type: 'change', document }); markDirty(); }, [markDirty]);
  const save = useCallback(async (manual = false) => {
    if (!history.present || savingRef.current || (!dirty && !manual)) return !dirty;
    const savedSequence = editSequenceRef.current;
    const documentToSave = history.present;
    savingRef.current = true; setSaveState('saving');
    try {
      const next = await apiSaveReportDraft(reportId, { base_revision: revisionRef.current, document: documentToSave });
      revisionRef.current = next.draft_revision; setRecord(next);
      if (editSequenceRef.current === savedSequence) {
        setDirty(false); setSaveState('saved');
      } else {
        setDirty(true); setSaveState('dirty');
      }
      if (manual) message.success(`草稿已保存 · r${next.draft_revision}`);
      return true;
    } catch (error) {
      setSaveState(error.status === 409 ? 'conflict' : 'error');
      if (error.status === 409) message.error('草稿存在较新版本，已停止自动覆盖；请重新载入后合并。');
      else message.error(error.message);
      return false;
    } finally { savingRef.current = false; }
  }, [dirty, history.present, message, reportId]);
  useEffect(() => { if (!dirty || saveState === 'conflict') return undefined; const timer = setTimeout(() => save(false), 800); return () => clearTimeout(timer); }, [dirty, history.present, save, saveState]);

  const firstRowId = history.present?.sections?.[0]?.rows?.[0]?.id;
  const addToFirstRow = (block) => { if (!firstRowId) return; const next = insertBlock(history.present, firstRowId, block); apply(next); setSelectedId(block.id); };
  const libraryBlock = (id) => {
    if (id.startsWith('viz:')) return visualizationBlock(visualizations.find((item) => item.visualization_id === id.slice(4)));
    const type = id.slice(5);
    return createBlock(type, { title: BLOCK_LABELS[type], body: type === 'markdown' ? '在右侧检查器中输入正文。' : '' });
  };
  const dragEnd = ({ active, over }) => {
    if (!over || !history.present) return;
    const targetBlock = locateBlock(history.present, String(over.id));
    const targetRow = targetBlock ? targetBlock.row : locateRow(history.present, String(over.id))?.row;
    if (!targetRow) return;
    const next = String(active.id).startsWith('viz:') || String(active.id).startsWith('type:')
      ? insertBlock(history.present, targetRow.id, libraryBlock(String(active.id)), targetBlock?.block.id)
      : moveBlock(history.present, String(active.id), targetRow.id, targetBlock?.block.id);
    apply(next);
  };

  const freeze = async () => {
    if (!await save(true)) return;
    try { const version = await apiFreezeReport(reportId); message.success(`已冻结报告 v${version.version}`); }
    catch (error) { message.error(error.message); }
  };
  const exportReport = async (format, mode) => {
    try {
      const task = await apiCreateReportExport(reportId, { format, mode });
      setExportTask(task);
    } catch (error) { message.error(error.detail?.message || error.message); }
  };
  useEffect(() => {
    if (!exportTask || !['queued', 'running'].includes(exportTask.status)) return undefined;
    const timer = setInterval(async () => { try { const next = await apiReportExport(exportTask.export_id); setExportTask(next); } catch { /* keep last task state */ } }, 1200);
    return () => clearInterval(timer);
  }, [exportTask]);

  const exportItems = [
    { key: 'pdf', label: '静态 PDF（Typst）', onClick: () => exportReport('pdf', 'static') },
    { key: 'portable', label: '离线 HTML ZIP', onClick: () => exportReport('html', 'portable') },
    { key: 'connected', label: '连接版 HTML', onClick: () => exportReport('html', 'connected') }
  ];
  const selected = selectedId && history.present ? locateBlock(history.present, selectedId) : null;

  if (loading) return <div className="workspace-page"><Skeleton active paragraph={{ rows: 16 }} /></div>;
  if (!record || !history.present) return <Result status="404" title="可编辑报告不存在" subTitle="内置只读报告需要先复制为草稿。" extra={<Link to="/reports"><Button type="primary">返回报告中心</Button></Link>} />;

  return <div className="workspace-page report-composer">
    <PageTitle title={history.present.metadata?.title || record.title} description="章节 + 行 + 12 列网格 · 仅使用已保存的可视化结果" actions={<>
      <Link to="/reports"><Button icon={<ArrowLeftOutlined />}>报告中心</Button></Link>
      <Button icon={<UndoOutlined />} disabled={!history.past.length} onClick={() => { dispatch({ type: 'undo' }); markDirty(); }}>撤销</Button>
      <Button icon={<RedoOutlined />} disabled={!history.future.length} onClick={() => { dispatch({ type: 'redo' }); markDirty(); }}>重做</Button>
      <Button icon={<SaveOutlined />} onClick={() => save(true)}>保存</Button>
      <Link to={`/reports/${reportId}`}><Button icon={<EyeOutlined />}>预览</Button></Link>
      <Button onClick={freeze}>冻结版本</Button>
      <Dropdown menu={{ items: exportItems }} disabled={quarto?.state !== 'live'}><Tooltip title={quarto?.state === 'live' ? '使用 Quarto 1.10.18 导出' : quarto?.message || 'Quarto 未安装'}><Button type="primary" icon={<DownloadOutlined />}>导出</Button></Tooltip></Dropdown>
    </>} />
    <div className="composer-statusbar"><span className={`save-state state-${saveState}`}>{saveState === 'saving' ? '正在保存…' : saveState === 'dirty' ? '有未保存更改' : saveState === 'conflict' ? '版本冲突' : saveState === 'error' ? '保存失败' : `已保存 r${revisionRef.current}`}</span><span>Quarto {quarto?.version || quarto?.required_version || '1.10.18'} · {quarto?.state === 'live' ? '导出可用' : '导出暂不可用'}</span><span>{visualizations.length} 个已保存可视化结果</span></div>
    {saveState === 'conflict' ? <Alert type="error" showIcon message="检测到并发修改" description="服务器上的 draft_revision 已更新。为避免覆盖，自动保存已经停止。" action={<Button onClick={load}>重新载入服务器版本</Button>} /> : null}
    <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={dragEnd}>
      <div className="report-composer-layout">
        <aside className={`report-library ${mobilePanel === 'library' ? 'is-mobile-open' : ''}`}>
          <div className="panel-mobile-heading"><strong>素材库</strong><Button type="text" aria-label="关闭素材库" icon={<LeftOutlined />} onClick={() => setMobilePanel(null)} /></div>
          <Tabs items={[{
            key: 'viz', label: `已保存结果 ${visualizations.length}`, children: visualizations.length ? <div className="report-library-list">{visualizations.map((item) => <LibraryItem key={item.visualization_id} id={`viz:${item.visualization_id}`} label={item.name} subtitle={item.revision ? `任务 ${item.task_id} · 配置 r${item.revision}` : `配置 ${item.spec_id} v${item.spec_version}`} onAdd={() => addToFirstRow(visualizationBlock(item))} />)}</div> : <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="请先在数据资产中保存可视化结果" />
          }, {
            key: 'content', label: '内容块', children: <div className="report-library-list">{LIBRARY_TYPES.map((type) => <LibraryItem key={type} id={`type:${type}`} label={BLOCK_LABELS[type]} subtitle={type === 'page_break' ? '导出时开始新页' : '可在右侧编辑'} onAdd={() => addToFirstRow(libraryBlock(`type:${type}`))} />)}</div>
          }]} />
        </aside>
        <main className="report-document-canvas">
          <div className="composer-mobile-toolbar"><Button icon={<MenuOutlined />} onClick={() => setMobilePanel('library')}>素材</Button><Button icon={<RightOutlined />} disabled={!selected} onClick={() => setMobilePanel('inspector')}>属性</Button></div>
          <div className="report-paper" data-page-size={history.present.theme?.page_size || 'A4'}>
            <header className="report-paper-title"><Input.TextArea variant="borderless" autoSize={{ minRows: 1, maxRows: 3 }} value={history.present.metadata?.title} aria-label="报告标题" onChange={(event) => apply({ ...history.present, metadata: { ...history.present.metadata, title: event.target.value } })} /><span>{history.present.metadata?.author} · 面向 {history.present.metadata?.audience}</span></header>
            {history.present.sections.map((section, sectionIndex) => <section className="composer-section" key={section.id}>
              <header><span>{String(sectionIndex + 1).padStart(2, '0')}</span><Input variant="borderless" value={section.title} aria-label={`第 ${sectionIndex + 1} 章标题`} onChange={(event) => apply(updateSection(history.present, section.id, { title: event.target.value }))} /><Button type="text" onClick={() => apply(addRow(history.present, section.id))}>添加行</Button></header>
              {section.rows.map((row) => <CanvasRow key={row.id} row={row} selectedId={selectedId} onSelect={(id) => { setSelectedId(id); setMobilePanel(null); }} onMove={(id, direction) => apply(moveBlockByStep(history.present, id, direction))} onResize={(id, span) => apply(resizeBlock(history.present, id, span))} />)}
            </section>)}
            <Button className="add-section-button" icon={<FileAddOutlined />} onClick={() => apply(addSection(history.present))}>添加章节</Button>
          </div>
        </main>
        <aside className={`report-inspector ${mobilePanel === 'inspector' ? 'is-mobile-open' : ''}`}><Inspector document={history.present} selectedId={selectedId} apply={apply} onClose={() => setMobilePanel(null)} onDelete={() => { apply(removeBlock(history.present, selectedId)); setSelectedId(null); }} onDuplicate={() => apply(duplicateBlock(history.present, selectedId))} /></aside>
      </div>
    </DndContext>
    {mobilePanel ? <button className="composer-mobile-scrim" aria-label="关闭面板" onClick={() => setMobilePanel(null)} /> : null}
    <Modal open={Boolean(exportTask)} title="Quarto 导出任务" footer={null} onCancel={() => setExportTask(null)}>
      {exportTask ? <div className="export-task-status"><Tag color={exportTask.status === 'succeeded' ? 'success' : exportTask.status === 'failed' ? 'error' : 'processing'}>{exportTask.status}</Tag><p>阶段：<code>{exportTask.stage}</code></p>{exportTask.error ? <Alert type="error" message={exportTask.error.code} description={exportTask.error.message} /> : null}{exportTask.status === 'failed' ? <Button onClick={() => exportReport(exportTask.format, exportTask.mode)}>重试导出</Button> : null}{exportTask.status === 'succeeded' ? <a href={reportExportDownloadUrl(exportTask.export_id)}><Button type="primary" icon={<DownloadOutlined />}>下载导出文件</Button></a> : null}</div> : null}
    </Modal>
  </div>;
}
