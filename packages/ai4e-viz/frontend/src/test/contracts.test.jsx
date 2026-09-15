import { afterEach, describe, expect, it, vi } from 'vitest';
import { act, cleanup, render, screen, waitFor, within } from '@testing-library/react';
import App from '../App.jsx';
import { API_BASE } from '../infrastructure/http/client.js';
import { FRONTEND_MODULES } from '../app/moduleRegistry.js';
import { fallbackCatalog, fallbackFunctions, fallbackSpecs } from '../modules/visTaskManage/fallback.js';
import { UI_TERMS } from '../modules/visTaskManage/terminology.js';
import {
  createBlock, createRow, createSection, historyReducer, initialHistory, insertBlock,
  locateBlock, moveBlock, resizeBlock
} from '../modules/reportDesigner/domain/reportDocument.js';

afterEach(() => {
  cleanup();
  sessionStorage.clear();
  vi.restoreAllMocks();
});

describe('visualization registry contract', () => {
  it('registers dataAssets and visDatasets as separate bounded contexts', () => {
    const names = FRONTEND_MODULES.map((module) => module.name);
    expect(names).toContain('dataAssets');
    expect(names).toContain('visDatasets');
    expect(FRONTEND_MODULES.find((module) => module.name === 'dataAssets').routes).toEqual(['/', '/assets/:artifactId']);
    expect(FRONTEND_MODULES.find((module) => module.name === 'visDatasets').routes).toEqual([]);
  });

  it('uses one unambiguous set of interface terms', () => {
    expect(UI_TERMS).toEqual({
      artifact: '数据资产',
      family: '数据家族',
      kind: '数据语义类型',
      method: '可视化方法',
      spec: '可视化配置',
      visualization: '可视化结果',
      renderer: '渲染器',
      format: '文件格式',
      dtype: '字段类型'
    });
    expect(Object.values(UI_TERMS)).not.toContain('数据类别');
  });

  it('contains the exact approved counts', () => {
    expect(fallbackCatalog.counts).toEqual({ families: 5, kinds: 19, functions: 23 });
    expect(fallbackCatalog.kinds.every((kind) => kind.example_ids.length > 0)).toBe(true);
    expect(fallbackFunctions).toHaveLength(23);
    const methodIds = fallbackCatalog.kinds.flatMap((item) => item.method_ids).sort();
    expect(fallbackFunctions.map((item) => item.id).sort()).toEqual(methodIds);
    expect(fallbackFunctions.every((item) => !item.id.includes('vizro') && item.renderer !== 'vizro')).toBe(true);
    expect(fallbackFunctions.every((item) => item.accepted_formats.length && item.example_id && Object.keys(item.default_parameters).length)).toBe(true);
    const methodCases = fallbackFunctions.map((item) => item.example_id);
    expect(methodCases).toHaveLength(23);
    expect(new Set(methodCases).size).toBe(23);
    expect(fallbackCatalog.kinds.every((kind) => kind.example_ids.length === kind.method_ids.length)).toBe(true);
    expect(fallbackCatalog.kinds.every((kind) => kind.examples.every((example) => example.name && example.case_type_label))).toBe(true);
    const scalarField = fallbackFunctions.find((item) => item.id === 'scientific.field-scalar@2.1.0');
    const vectorField = fallbackFunctions.find((item) => item.id === 'scientific.field-vector@2.1.0');
    expect(scalarField.accepted_formats).toContain('NPZ');
    expect(vectorField.accepted_formats).toContain('NPZ');
  });

  it('binds GEO mesh only to Online3DViewer', () => {
    const mesh = fallbackCatalog.kinds.find((kind) => kind.id === 'mesh');
    const fn = fallbackFunctions.find((item) => item.id === mesh.default_function);
    expect(fn.renderer).toBe('o3dv');
    expect(fallbackSpecs.renderer_bindings[mesh.default_function].owner).toBe('o3dv');
  });
});

describe('backend transport contract', () => {
  it('uses the same-origin API proxy when no deployment override is set', () => {
    expect(API_BASE).toBe('');
  });
});

describe('hash routes', () => {
  it('does not hard-code report business counts in the application shell', () => {
    window.location.hash = '#/reports';
    render(<App />);
    // Ant Design 图标会参与无障碍名称计算，因此这里同时覆盖桌面端和移动端导航文本。
    const reportLinks = screen.getAllByRole('link', { name: /报告中心|报告$/ });
    expect(reportLinks.length).toBeGreaterThan(0);
    expect(reportLinks.every((link) => !link.textContent.includes('6'))).toBe(true);
  });

  it('renders three readable catalog counters without exposing an internal revision', async () => {
    window.location.hash = '#/recommendations/field';
    render(<App />);
    expect(await screen.findByRole('heading', { name: '物理场' })).toBeInTheDocument();
    const counters = screen.getByLabelText('注册表统计');
    expect(within(counters).getAllByText(/5|19|23/)).toHaveLength(3);
    expect(within(counters).queryByText(/Revision|visual-report-engine/i)).not.toBeInTheDocument();
  });

  it('opens a recommendation kind through a deep link', async () => {
    window.location.hash = '#/recommendations/mesh';
    render(<App />);
    expect(await screen.findByRole('heading', { name: '几何网格' })).toBeInTheDocument();
    expect(screen.getByText('GEO 契约')).toBeInTheDocument();
  });

  it('does not silently replace an unknown report with the first report', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue({ ok: false, status: 404, json: async () => ({ detail: '未知报告' }) });
    window.location.hash = '#/reports/not-found';
    render(<App />);
    await waitFor(() => expect(screen.getByText('报告不存在')).toBeInTheDocument());
    expect(screen.queryByText('机翼跨声速风洞试验 × CFD 对比验证报告')).not.toBeInTheDocument();
  });

  it('clears the previous report when a client-side route changes to an unknown id', async () => {
    const validReport = {
      id: 'rep-ok', title: '可用报告', status: 'succeeded', summary: '有效内容', author: '测试',
      generated_at: '2026-08-23 00:00', spec: 'rspec-test v1', takeaways: ['有效结论'], sections: []
    };
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => String(input).endsWith('/api/reports/rep-ok')
      ? { ok: true, status: 200, json: async () => validReport }
      : { ok: false, status: 404, json: async () => ({ detail: '未知报告' }) });
    window.location.hash = '#/reports/rep-ok';
    render(<App />);
    expect(await screen.findByText('可用报告')).toBeInTheDocument();
    await act(async () => {
      window.location.hash = '#/reports/not-found-after-valid';
      window.dispatchEvent(new HashChangeEvent('hashchange'));
    });
    await waitFor(() => expect(screen.getByText('报告不存在')).toBeInTheDocument());
    expect(screen.queryByText('可用报告')).not.toBeInTheDocument();
  });
});

describe('report document model', () => {
  it('moves blocks across rows and preserves a valid 12-column grid', () => {
    const section = createSection('结果');
    const first = createBlock('markdown', { title: '结论', span: 6 });
    const second = createBlock('metric', { title: '误差', span: 6 });
    section.rows[0] = createRow([first, second]);
    section.rows.push(createRow());
    const document = { metadata: {}, theme: {}, sections: [section] };
    const moved = moveBlock(document, second.id, section.rows[1].id);
    expect(locateBlock(moved, second.id).row.id).toBe(section.rows[1].id);
    const resized = resizeBlock(moved, first.id, 12);
    expect(locateBlock(resized, first.id).block.layout.span).toBe(12);
    expect(resized.sections[0].rows.every((row) => row.blocks.reduce((sum, block) => sum + block.layout.span, 0) <= 12)).toBe(true);
  });

  it('creates a new row when a drop target is already full', () => {
    const section = createSection('证据');
    section.rows[0] = createRow([createBlock('markdown', { span: 12 })]);
    const document = { metadata: {}, theme: {}, sections: [section] };
    const block = createBlock('visualization', { span: 12, source_ref: { artifact_id: 'A', visualization_id: 'V', spec_id: 'S', spec_version: 1, content_hash: 'x' } });
    const inserted = insertBlock(document, section.rows[0].id, block);
    expect(inserted.sections[0].rows).toHaveLength(2);
    expect(locateBlock(inserted, block.id).row.id).toBe(inserted.sections[0].rows[1].id);
  });

  it('supports bounded undo and redo', () => {
    const document = { metadata: { title: 'v1' }, theme: {}, sections: [createSection()] };
    const changed = { ...document, metadata: { title: 'v2' } };
    const state = historyReducer(initialHistory(document), { type: 'change', document: changed });
    const undone = historyReducer(state, { type: 'undo' });
    expect(undone.present.metadata.title).toBe('v1');
    expect(historyReducer(undone, { type: 'redo' }).present.metadata.title).toBe('v2');
  });
});
