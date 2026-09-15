import {test, expect} from '@playwright/test';

/** 网格预览弹窗夹具：核对默认加高与放大到视口全屏，不冒充真实 VTK 渲染。 */
test('三维预览弹窗可加高并放大到全屏幕', async ({page}) => {
  await page.setViewportSize({width: 1440, height: 900});
  await page.route('**/api/v1/**', async route => {
    const path = new URL(route.request().url()).pathname;
    let value: unknown = [];
    if (path.endsWith('/preview')) value = {kind: 'mesh', fields: []};
    else if (path.endsWith('/assets') && route.request().method() === 'POST') value = {asset_id: 'mesh', revision: 'v1', project_id: 'fixture', task_id: 'task'};
    else if (path.endsWith('/tasks')) value = [{id: 'task', name: '测试任务'}];
    else if (path.endsWith('/visualizations')) value = {items: []};
    else if (path.endsWith('/sessions')) value = {session_id: 's1', embed_url: 'about:blank'};
    else if (path.includes('/sessions/')) value = {status: 'closed'};
    await route.fulfill({json: value});
  });
  await page.goto('/');
  await page.evaluate(async () => {
    const React = (await import('/node_modules/.vite/deps/react.js' as any)).default;
    const {createRoot} = (await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;
    const {FilePreviewDialog} = await import('/src/modules/previews/FilePreviewDialog.tsx' as any);
    document.body.innerHTML = '<div id="fixture"></div>';
    createRoot(document.getElementById('fixture')!).render(React.createElement(FilePreviewDialog, {
      project: 'fixture',
      task: 'task',
      file: {root: 'task', path: 'surface.vtk', name: 'surface.vtk'},
      onClose: () => {},
    }));
  });
  await expect(page.getByRole('button', {name: '放大到全屏幕'})).toBeVisible();
  const host = page.locator('.file-preview-dialog.mesh .file-preview-mesh');
  await expect(host).toBeVisible();
  await expect.poll(async () => host.evaluate(el => (el as HTMLElement).offsetHeight)).toBeGreaterThanOrEqual(760);
  await expect.poll(async () => page.locator('.file-preview-dialog.mesh iframe[title="独立可视化应用"]').evaluate(el => (el as HTMLElement).offsetHeight)).toBeGreaterThanOrEqual(600);
  await expect.poll(async () => page.locator('.file-preview-dialog.mesh').evaluate(el => getComputedStyle(el).overflowY)).toMatch(/auto|scroll/);
  await page.getByRole('button', {name: '放大到全屏幕'}).click();
  await expect(page.locator('.file-preview-dialog.fullscreen')).toBeVisible();
  await expect.poll(async () => (await page.locator('.file-preview-dialog.fullscreen .ant-modal').boundingBox())?.width ?? 0).toBeGreaterThanOrEqual(1400);
  await expect.poll(async () => (await page.locator('.file-preview-dialog.fullscreen .ant-modal').boundingBox())?.height ?? 0).toBeGreaterThanOrEqual(850);
  await expect.poll(async () => page.locator('.file-preview-dialog.fullscreen .file-preview-mesh').evaluate(el => (el as HTMLElement).offsetHeight)).toBeGreaterThan(600);
  await expect.poll(async () => page.locator('.file-preview-dialog.fullscreen .phys-host').evaluate(el => (el as HTMLElement).offsetHeight)).toBeGreaterThan(500);
  await expect.poll(async () => page.locator('.file-preview-dialog.fullscreen iframe[title="独立可视化应用"]').evaluate(el => (el as HTMLElement).offsetHeight)).toBeGreaterThan(500);
  await page.getByRole('button', {name: '退出全屏幕'}).click();
  await expect(page.locator('.file-preview-dialog.fullscreen')).toHaveCount(0);
  await expect(page.getByRole('button', {name: '放大到全屏幕'})).toBeVisible();
});
