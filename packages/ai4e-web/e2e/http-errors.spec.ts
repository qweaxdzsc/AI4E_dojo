import { test, expect } from '@playwright/test';

/** 项目入口通过真实请求门面显示代理失败，不能泄露 JSON 解析异常。 */
for (const [name, status, body, expected] of [
  ['空的代理错误', 500, '', 'Dojo 后端服务暂不可用（HTTP 500）'],
  ['HTML 网关错误', 502, '<html>Bad Gateway</html>', 'Dojo 后端服务暂不可用（HTTP 502）'],
  ['服务业务错误', 409, '{"detail":"配置已变更，请重新读取"}', '配置已变更，请重新读取'],
  ['映射后的业务错误', 409, '{"detail":"processed_dataset_name_conflict","error":{"code":"processed_dataset_name_conflict","message":"该平台数据集名称已被不同处理声明占用，请换一个名称。"}}', '该平台数据集名称已被不同处理声明占用'],
  ['截断的成功响应', 200, '{"items":', 'Dojo 后端返回了空响应或无效数据'],
  ['空的成功响应', 200, '', 'Dojo 后端返回了空响应或无效数据'],
] as const) {
  test(name, async ({ page }) => {
    await page.route('**/api/v1/projects', route => route.fulfill({status, body}));
    await page.goto('/projects');
    await expect(page.getByRole('alert')).toContainText(expected);
    await expect(page.locator('body')).not.toContainText('Unexpected end of JSON');
  });
}

test('连接断开后刷新可以恢复项目列表', async ({ page }) => {
  await page.route('**/api/v1/projects', route => route.abort('connectionrefused'));
  await page.goto('/projects');
  await expect(page.getByRole('alert')).toContainText('无法连接 Dojo 后端服务');
  await page.unroute('**/api/v1/projects');
  await page.route('**/api/v1/projects', route => route.fulfill({json: []}));
  await page.reload();
  await expect(page.getByRole('heading', {name: '项目管理', exact: true})).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('无正文成功与合法JSON响应遵守各自契约', async ({ page }) => {
  await page.route('**/api/v1/projects', route => route.fulfill({json: []}));
  await page.goto('/projects');
  await page.route('**/api/v1/http-test', route => route.fulfill({status: 204}));
  const empty = await page.evaluate(async () => {
    // 在 Vite 中消费同一请求门面，不复制实现作为测试。
    const {request} = await import('/src/infrastructure/http/client.ts');
    return (await request('/http-test', undefined, 'DELETE')) === undefined;
  });
  expect(empty).toBe(true);
  await page.unroute('**/api/v1/http-test');
  await page.route('**/api/v1/http-test', route => route.fulfill({json: {revision: 3}}));
  expect(await page.evaluate(async () => {
    const {request} = await import('/src/infrastructure/http/client.ts');
    return request('/http-test');
  })).toEqual({revision: 3});
});
