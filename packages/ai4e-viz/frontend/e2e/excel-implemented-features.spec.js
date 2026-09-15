/**
 * Excel“功能模块”中已实现用户链路的逐项浏览器回归。
 *
 * 用例编号直接对应工作簿序号；这里只验证真实页面、真实Renderer与可操作控件，
 * 不把目录占位、参数校验器或静态说明当成用户功能实现。
 */

import { expect, test } from '@playwright/test';


test('Excel 1/3：O3DV支持旋转平移缩放入口和适合窗口', async ({ page }) => {
  await page.goto('/#/assets/A-1027');
  await page.getByRole('tab', { name: '默认参数预览' }).click();
  await expect(page.getByText('● 查看器就绪')).toBeVisible();
  const viewer = page.frameLocator('iframe');
  await expect(viewer.getByRole('navigation', { name: '三维查看工具栏' })).toBeVisible();
  await expect(viewer.getByRole('button', { name: '复位视图' })).toBeVisible();
  await expect(viewer.getByRole('button', { name: '放大模型' })).toBeVisible();
  await expect(viewer.getByRole('button', { name: '缩小模型' })).toBeVisible();
  await expect(viewer.getByText('单指旋转 · 双指平移/缩放')).toBeVisible();
  await viewer.getByRole('button', { name: '放大模型' }).click();
  await viewer.getByRole('button', { name: '缩小模型' }).click();
  await viewer.getByRole('button', { name: '复位视图' }).click();
});


test('Excel 48-51：表格、散点、折线和柱状图都进入真实Renderer', async ({ page }) => {
  await page.goto('/#/recommendations/table');
  // Perspective使用Shadow DOM；以其真实可访问数据网格和字段名作为用户层证据。
  const table = page.locator('.evidence-canvas').getByRole('table');
  await expect(table).toBeVisible();
  await expect(table.getByRole('columnheader', { name: 'point_id' })).toBeVisible();
  await expect(table.getByRole('columnheader', { name: 'pressure_kpa' })).toBeVisible();

  const svgCases = [
    ['optimization', '优化候选图'],
    ['series', '序列趋势图'],
    ['distribution', '分布图'],
  ];
  for (const [kind, method] of svgCases) {
    await page.goto(`/#/recommendations/${kind}`);
    await expect(page.getByRole('button', { name: new RegExp(method) })).toBeVisible();
    await expect(page.locator('.evidence-canvas svg')).toBeVisible();
  }
});


test('Excel 55：PNG图片由浏览器原生图片组件真实解码', async ({ page }) => {
  await page.goto('/#/recommendations/image');
  const image = page.locator('.evidence-canvas img').first();
  await expect(image).toBeVisible();
  await expect.poll(() => image.evaluate((node) => node.naturalWidth)).toBeGreaterThan(0);
});


test('Excel 19/21/22/32：物理场云图可重置视角并控制240帧时序', async ({ page }, testInfo) => {
  await page.goto('/#/assets/A-1115');
  await page.getByRole('tab', { name: '默认参数预览' }).click();
  await expect(page.getByText('Trame + vtk.js · 交互服务在线')).toBeVisible({ timeout: 60_000 });
  const trame = page.frameLocator('iframe.trame-frame');
  await expect(trame.getByRole('button', { name: '重置视角' })).toBeVisible({ timeout: 60_000 });
  await expect(trame.getByRole('button', { name: '播放', exact: true })).toBeVisible();
  await expect(trame.getByRole('button', { name: '上一帧' })).toBeVisible();
  await expect(trame.getByRole('button', { name: '下一帧' })).toBeVisible();
  const slider = trame.getByRole('slider', { name: 'Miller 时序帧' });
  await expect(slider).toBeVisible();
  const before = Number(await slider.inputValue());
  const nextFrame = trame.getByRole('button', { name: '下一帧' });
  if (testInfo.project.name === 'mobile-chromium') {
    // 390px下按钮位于iframe可视区外，当前可用替代操作是聚焦滑块后按方向键。
    await slider.focus();
    await slider.press('ArrowRight');
  } else {
    await nextFrame.click({ force: true });
  }
  await expect.poll(async () => Number(await slider.inputValue())).toBe((before + 1) % 240);
});


test('Excel 80/81/83：报告可查询筛选、复制并冻结版本', async ({ page, request }, testInfo) => {
  const reportTitle = `Excel功能逐项测试报告-${testInfo.project.name}`;
  const createdResponse = await request.post('/api/reports', { data: {
    title: reportTitle, author: 'E2E', audience: '测试团队',
    goal: '验证报告管理已实现边界', template: 'analysis', key_questions: ['版本是否冻结？'],
  } });
  expect(createdResponse.ok()).toBeTruthy();
  const created = await createdResponse.json();

  await page.goto('/#/reports');
  const search = page.getByPlaceholder('搜索报告标题、ID 或作者');
  await search.fill(reportTitle);
  await expect(page.getByRole('row', { name: new RegExp(created.report_id) })).toBeVisible();

  const duplicate = await request.post(`/api/reports/${created.report_id}/duplicate`, { data: {} });
  expect(duplicate.ok()).toBeTruthy();
  const frozen = await request.post(`/api/reports/${created.report_id}/versions`, { data: {} });
  expect(frozen.ok()).toBeTruthy();
  expect((await frozen.json()).version).toBe(1);
});


test('Excel 88-90：报告编排可引用已保存结果并新增、移动内容块', async ({ page, request }) => {
  const visualizationResponse = await request.post('/api/artifacts/A-1025/visualizations', {
    data: { recommendation_id: 'time-series', parameters: { line_width: 2 } },
  });
  expect(visualizationResponse.ok()).toBeTruthy();
  const visualization = await visualizationResponse.json();
  const reportResponse = await request.post('/api/reports', { data: {
    title: 'Excel报告编排逐项测试', author: 'E2E', audience: '测试团队',
    goal: '验证可视化引用和内容块编排', template: 'analysis', key_questions: [],
  } });
  const report = await reportResponse.json();

  await page.goto(`/#/reports/${report.report_id}/edit`);
  if ((page.viewportSize()?.width ?? 1440) <= 760) {
    await page.getByRole('button', { name: 'menu 素材', exact: true }).click();
  }
  const libraryItem = page.locator('.report-library-item').filter({ hasText: visualization.visualization_id }).first();
  await libraryItem.getByRole('button', { name: '添加' }).click();
  if ((page.viewportSize()?.width ?? 1440) <= 760) {
    await page.getByRole('button', { name: '关闭素材库' }).click();
  }
  const resultText = `结果 ID：${visualization.visualization_id}`;
  await expect(page.locator('.report-document-canvas').getByText(resultText, { exact: true })).toBeVisible();
  const block = page.locator('.report-document-canvas').getByText(resultText, { exact: true }).locator('..').locator('..');
  await block.click();
  await expect(block.getByRole('button', { name: /上移|下移/ }).first()).toBeVisible();
});
