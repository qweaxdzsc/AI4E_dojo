import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { expect, test } from '@playwright/test';

const here = path.dirname(fileURLToPath(import.meta.url));
const gsMetrics = path.resolve(here, '../../fixtures/gs/models/cnn_mlp/metrics.csv');
const browserLogs = new Map();

test.beforeEach(async ({ page }, testInfo) => {
  const lines = [];
  browserLogs.set(testInfo.testId, lines);
  page.on('console', (message) => {
    const location = message.location()?.url;
    lines.push(`[${message.type()}] ${message.text()}${location ? ` · ${location}` : ''}`);
  });
  page.on('response', (response) => {
    if (response.status() >= 400) {
      lines.push(`[http-${response.status()}] ${response.request().method()} ${response.url()}`);
    }
  });
  page.on('pageerror', (error) => {
    lines.push(`[pageerror] ${error.stack || error.message}`);
  });
});

test.afterEach(async ({}, testInfo) => {
  const lines = browserLogs.get(testInfo.testId) ?? [];
  await testInfo.attach('browser-console.log', {
    body: `${lines.join('\n')}${lines.length ? '\n' : ''}`,
    contentType: 'text/plain',
  });
  const errors = lines.filter((line) => line.startsWith('[error]') || line.startsWith('[pageerror]') || /^\[http-[45]\d\d\]/.test(line));
  expect(errors, 'browser console must not contain application errors').toEqual([]);
  browserLogs.delete(testInfo.testId);
});

test('upload → deterministic recommendations → frozen Spec → real drawing', async ({ page }) => {
  await page.goto('/#/');
  await page.getByRole('button', { name: '上传数据' }).click();
  await page.locator('.ant-upload input[type="file"]').setInputFiles(gsMetrics);
  await page.getByRole('button', { name: '上传、分析并推荐方法' }).click();
  await expect(page.getByText(/已生成 \d+ 个可视化方法选项|检测到相同内容/)).toBeVisible();
  await page.getByRole('button', { name: '打开数据资产' }).click();

  await expect(page.getByRole('heading', { name: /metrics/i })).toBeVisible();
  await expect(page.getByText('基于数据画像推荐的可视化方法')).toBeVisible();
  await page.getByRole('button', { name: /训练\/迭代趋势/ }).click();
  await page.getByRole('button', { name: '配置并预览' }).click();
  await expect(page.getByRole('heading', { name: /配置方法 · metrics/i })).toBeVisible();
  await expect(page.getByText('参数已校验')).toBeVisible();
  const lineWidth = page.getByText('线宽', { exact: true }).locator('..').locator('input');
  if (await lineWidth.count()) await lineWidth.fill('3.5');
  await expect(page.getByText('参数已校验')).toBeVisible();
  await page.getByRole('button', { name: '保存配置并生成结果' }).click();
  await expect(page).toHaveURL(/#\/visualizations\/viz-/);
  await expect(page.locator('.evidence-canvas svg')).toBeVisible();
  await expect(page.getByText(/来自原始文件|个数值序列/)).toBeVisible();
});

test('previously broken assets expose truthful render or diagnostic paths', async ({ page }) => {
  const checks = [
    ['A-1027', 'Online3DViewer'],
    ['A-1028', '真实中截面静态证据'],
    ['A-1029', '真实轨迹 XY 投影'],
    ['A-1032', '日志明细与筛选'],
  ];
  for (const [id, evidence] of checks) {
    await page.goto(`/#/assets/${id}`);
    await expect(page.getByText(id, { exact: false }).first()).toBeVisible();
    if (id === 'A-1032') {
      await expect(page.getByRole('button', { name: /日志明细与筛选/ })).toBeVisible();
    } else {
      await page.getByRole('tab', { name: '默认参数预览' }).click();
      if (id === 'A-1028' || id === 'A-1029') {
        await expect(page.getByText(/交互服务在线|交互服务离线/)).toBeVisible();
      }
      const staticFallback = page.getByRole('button', { name: '查看静态降级' });
      if (await staticFallback.count()) await staticFallback.click();
      await expect(page.locator('.evidence-canvas').getByText(evidence, { exact: false }).first()).toBeVisible();
    }
  }
  await page.goto('/#/assets/A-1030');
  await expect(page.getByText('声明类型是 FLD / 物理场（field），识别类型是 GEO / 几何网格（mesh）')).toBeVisible();
  await expect(page.getByRole('button', { name: /修正为几何网格/ })).toBeVisible();
});

test('report composer persists a frozen visualization block and restores after reload', async ({ page, request }) => {
  const vizResponse = await request.post('/api/artifacts/A-1025/visualizations', { data: { recommendation_id: 'time-series', parameters: { line_width: 2.5 } } });
  expect(vizResponse.ok()).toBeTruthy();
  const visualization = await vizResponse.json();
  const reportResponse = await request.post('/api/reports', { data: {
    title: 'Playwright 报告编排验证', author: 'E2E', audience: '工程团队', goal: '验证拖拽替代操作与草稿恢复', template: 'analysis', key_questions: ['可否重载恢复？']
  } });
  expect(reportResponse.ok()).toBeTruthy();
  const report = await reportResponse.json();
  await page.goto(`/#/reports/${report.report_id}/edit`);
  await expect(page.getByRole('heading', { name: 'Playwright 报告编排验证' })).toBeVisible();
  if ((page.viewportSize()?.width ?? 1440) <= 760) {
    await page.getByRole('button', { name: 'menu 素材', exact: true }).click();
  }
  const libraryItem = page.locator('.report-library-item').filter({ hasText: visualization.visualization_id }).first();
  await libraryItem.getByRole('button', { name: '添加' }).click();
  if ((page.viewportSize()?.width ?? 1440) <= 760) {
    await page.getByRole('button', { name: '关闭素材库' }).click();
  }
  const savedBlock = page.locator('.report-document-canvas').getByText(`结果 ID：${visualization.visualization_id}`, { exact: true }).first();
  await expect(savedBlock).toBeVisible();
  await expect(page.getByText(/已保存 r(?:[2-9]|\d{2,})/)).toBeVisible({ timeout: 10_000 });
  await page.reload();
  const restoredBlock = page.locator('.report-document-canvas').getByText(`结果 ID：${visualization.visualization_id}`, { exact: true }).first();
  await expect(restoredBlock).toBeVisible();
  await restoredBlock.locator('..').locator('..').click();
  if ((page.viewportSize()?.width ?? 1440) <= 760) {
    await page.getByRole('button', { name: 'right 属性', exact: true }).click();
  }
  await expect(page.locator('.frozen-source').getByText(/sha256:/)).toBeVisible();
});

test('G-S audit report keeps source conflict and real-data evidence visible', async ({ page }) => {
  await page.goto('/#/reports/rep-gs-pino-2026-0823');
  await expect(page.getByRole('heading', { name: 'PINO Grad–Shafranov 多几何泛化审计报告' })).toBeVisible();
  await expect(page.getByText('GS-AUDIT-001')).toHaveCount(0);
  await expect(page.getByText('源文档口径说明')).toBeVisible();
  await expect(page.getByText(/约 \+3 MA、传统解约 −3 MA/)).toBeVisible();
  await expect(page.getByText('八模型验证损失（对数轴）')).toBeVisible();
  await expect(page.getByText('PINO / 传统解 / 差值 / 残差对照')).toBeVisible();
  await expect(page.getByRole('link', { name: '下载原始 HTML' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'download 下载当前报告' })).toBeVisible();
});

test('Miller NPZ is classified as a physical field and its derived report is readable', async ({ page, request }) => {
  const parsedResponse = await request.get('/api/artifact/A-1115/parse');
  expect(parsedResponse.ok()).toBeTruthy();
  const parsed = await parsedResponse.json();
  expect(parsed.inferred_kind).toBe('field');
  expect(parsed.frames).toBe(240);
  expect(parsed.topology_shape).toEqual([148, 176]);

  await page.goto('/#/assets/A-1115');
  await expect(page.getByRole('heading', { name: 'Miller 托卡马克静电势时序场' })).toBeVisible();
  await expect(page.getByText(/240 帧 · 148 × 176 曲面网格/).first()).toBeVisible();
  await expect(page.getByRole('button', { name: /Miller 曲面时序标量场/ })).toBeVisible();

  await page.goto('/#/reports/rep-miller-tokamak-timeseries');
  await expect(page.getByRole('heading', { name: 'Miller 托卡马克静电势时序场分析报告' })).toBeVisible();
  await expect(page.getByText('范围声明')).toBeVisible();
  await expect(page.getByText(/确定性合成展示场/).first()).toBeVisible();
  await expect(page.getByText('归一化 k_y 谱强度')).toBeVisible();
  await expect(page.locator('.miller-frame-grid .report-chart')).toHaveCount(3);
  await expect(page.locator('.report-chart svg').first()).toBeVisible();
  await expect(page.getByRole('link', { name: '下载来源程序' })).toHaveCount(0);
  await expect(page.getByRole('link', { name: '下载 240 帧 NPZ' })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'download 下载当前报告' })).toBeVisible();
});

test('Miller vtk.js view plays the temporal field and exposes keyboard-operable controls', async ({ page }) => {
  await page.goto('/#/reports/rep-miller-tokamak-timeseries');
  await page.locator('iframe.trame-frame').scrollIntoViewIfNeeded();
  const trame = page.frameLocator('iframe.trame-frame');
  const playButton = trame.getByRole('button', { name: '播放', exact: true });
  const frameSlider = trame.getByRole('slider', { name: 'Miller 时序帧' });
  await expect(playButton).toBeVisible({ timeout: 60_000 });
  await expect(frameSlider).toBeVisible();
  await frameSlider.focus();
  const sliderBefore = Number(await frameSlider.inputValue());
  await frameSlider.press('ArrowRight');
  await expect.poll(async () => Number(await frameSlider.inputValue())).toBe(sliderBefore + 1);
  const frameLabel = trame.getByText(/帧 \d+\/240/).last();
  const before = await frameLabel.textContent();
  // vtk.js keeps repainting the iframe while Playwright waits for positional
  // stability. Force only bypasses that synthetic stability heuristic; the
  // button is still resolved by its accessible role and name.
  await playButton.click({ force: true });
  await expect.poll(async () => frameLabel.textContent(), { timeout: 12_000 }).not.toBe(before);
  const pauseButton = trame.getByRole('button', { name: '暂停', exact: true });
  await pauseButton.click({ force: true });
  const nextButton = trame.getByRole('button', { name: '下一帧' });
  await nextButton.click({ force: true });
  await expect(trame.getByText(/帧 \d+\/240/).last()).toBeVisible();
});

test('built-in report downloads the current reader as self-contained HTML and PDF', async ({ page, request }, testInfo) => {
  test.setTimeout(180_000);
  await page.goto('/#/reports/rep-miller-tokamak-timeseries');
  await expect(page.getByRole('heading', { name: 'Miller 托卡马克静电势时序场分析报告' })).toBeVisible();

  const exportCurrent = async (menuLabel) => {
    await page.getByRole('button', { name: 'download 下载当前报告' }).click();
    await page.getByText(menuLabel, { exact: true }).click();
    const modal = page.getByRole('dialog', { name: '生成当前报告' });
    await expect(modal).toBeVisible();
    await expect(modal.getByText('succeeded', { exact: true })).toBeVisible({ timeout: 120_000 });
    const download = modal.getByRole('link').last();
    const href = await download.getAttribute('href');
    expect(href).toMatch(/\/api\/report-exports\/export-[^/]+\/download/);
    const response = await request.get(href);
    expect(response.ok()).toBeTruthy();
    await page.getByRole('button', { name: 'Close' }).click();
    return response;
  };

  const html = await exportCurrent('下载当前报告 HTML');
  expect(html.headers()['content-type']).toContain('text/html');
  const htmlText = await html.text();
  expect(htmlText).toContain('Miller 托卡马克静电势时序场分析报告');
  expect(htmlText).not.toMatch(/127\.0\.0\.1|localhost/);

  if (testInfo.project.name === 'desktop-chromium') {
    const pdf = await exportCurrent('下载当前报告 PDF');
    expect(pdf.headers()['content-type']).toContain('application/pdf');
    expect((await pdf.body()).subarray(0, 4).toString()).toBe('%PDF');
  }
});

test('G-S current report HTML freezes all comparison figures without old source downloads', async ({ request }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop-chromium', 'one full current-reader capture is sufficient');
  test.setTimeout(180_000);
  const created = await request.post('/api/reports/rep-gs-pino-2026-0823/exports', {
    data: { format: 'html', mode: 'portable' },
  });
  expect(created.ok()).toBeTruthy();
  let task = await created.json();
  await expect.poll(async () => {
    const response = await request.get(`/api/report-exports/${task.export_id}`);
    task = await response.json();
    return task.status;
  }, { timeout: 120_000 }).toBe('succeeded');
  expect(task.error).toBeNull();
  const downloaded = await request.get(`/api/report-exports/${task.export_id}/download`);
  expect(downloaded.ok()).toBeTruthy();
  const html = await downloaded.text();
  expect(html).toContain('PINO Grad–Shafranov 多几何泛化审计报告');
  expect(html.match(/data:image\/png;base64/g)?.length ?? 0).toBeGreaterThanOrEqual(8);
  expect(html).not.toMatch(/127\.0\.0\.1|localhost|<script[^>]+src=/i);
  expect(html).not.toContain('下载原始 HTML');
});

test('series exposes its method, formats and default configuration', async ({ page }) => {
  await page.goto('/#/recommendations/series');
  const methodCard = page.locator('.method-grid > button');
  await expect(methodCard).toHaveCount(1);
  await expect(methodCard).toContainText('序列趋势图');
  await expect(methodCard).toContainText('chart.echarts-series@2.1.0');
  await expect(methodCard).toContainText('CSV');
  await expect(page.getByText('每个方法都有格式要求、默认配置和独立案例。', { exact: false })).toBeVisible();
  await expect(page.locator('.method-contract pre')).toContainText('line_width');
  await expect(page.locator('.example-preview .example-id')).toContainText('案例 ID CASE-SERIES');
  await expect(page.locator('.evidence-canvas svg')).toBeVisible();

  await page.goto('/#/recommendations/scalar');
  await expect(page.locator('.method-grid > button')).toHaveCount(2);
  await page.getByRole('button', { name: /标量柱状图/ }).click();
  await expect(page.locator('.method-contract pre')).toContainText('bar_width');

  await page.goto('/#/recommendations/raster');
  await expect(page.locator('.method-grid > button')).toHaveCount(2);
  await expect(page.getByRole('button', { name: /二维矢量栅格/ })).toBeVisible();

  await page.goto('/#/reports/rep-2026-0811-d');
  await expect(page.getByRole('heading', { name: '加热板几何校验与热分析准备报告' })).toBeVisible();
  await expect(page.getByText('REF-SPEC-404')).toHaveCount(0);
  await expect(page.getByText('加热板 STL 几何')).toBeVisible();
  await expect(page.locator('.evidence-canvas')).toBeVisible();
  await expect(page.getByText('物理场数组')).toBeVisible();
});

test('live Trame case without a snapshot opens the interactive vtk.js view', async ({ page }) => {
  await page.goto('/#/recommendations/raster');
  await expect(page.getByText(/交互服务在线/)).toBeVisible();
  await expect(page.locator('iframe.trame-frame')).toBeVisible();
  await expect(page.getByText('Trame/vtk.js 表示当前不可用')).toHaveCount(0);
  await expect(page.getByRole('button', { name: '刷新服务状态' })).toBeVisible();
});
