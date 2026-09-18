import { test, expect } from '@playwright/test';
/** 管理流程从项目导航点击进入，不能以深链接绕过项目入口。 */
test('项目查询、编辑、归档恢复和任务派生', async ({ page, request }) => {
  const name = '管理 ' + Date.now(), api = (process.env.DOJO_API_URL || 'http://127.0.0.1:8000') + '/api/v1';
  const response = await request.post(api + '/projects', { data: { name } });
  expect(response.ok()).toBeTruthy(); const p = (await response.json()).id;
  try {
    await page.goto('/projects');
    await page.getByRole('textbox', { name: '搜索项目', exact: true }).fill(name);
    await expect(page.locator('.projectgrid .taskcard')).toHaveCount(1);
    await page.getByRole('button', { name: /^编\s*辑$/ }).click();
    await page.getByLabel('项目名称').fill(name + ' 更新');
    await page.getByRole('dialog').getByRole('button', { name: /确\s*定/ }).click();
    await expect(page.getByRole('link', { name: name + ' 更新', exact: true })).toBeVisible();
    await page.getByRole('button', { name: /^归\s*档$/ }).click();
    await expect(page.getByRole('button', { name: /^恢\s*复$/ })).toBeVisible();
    await page.getByRole('button', { name: '已归档', exact: true }).click();
    await expect(page.locator('.projectgrid .taskcard')).toHaveCount(1);
    await page.getByRole('button', { name: /^恢\s*复$/ }).click();
    await expect(page.locator('.projectgrid .taskcard')).toHaveCount(0);
    await page.getByRole('button', { name: '全部项目', exact: true }).click();
    await page.getByRole('link', { name: '进入项目', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/projects/${p}/tasks$`));
    await page.getByRole('button', { name: '新建任务', exact: true }).click();
    await page.getByLabel('任务名称').fill('baseline');
    await page.getByRole('combobox',{name:'科研案例',exact:true}).click();await page.getByRole('option').first().click();
    await page.getByRole('dialog').getByRole('button', { name: '创建并进入原始处理',exact:true }).click();
    await page.goto(`/projects/${p}/tasks`);
    await page.getByRole('button',{name:'baseline 更多操作',exact:true}).click();await page.getByRole('menuitem',{name:'派生任务',exact:true}).click();
    await page.getByLabel('任务名称').fill('child');
    await page.getByRole('dialog').getByRole('button', { name: '派生并进入原始处理',exact:true }).click();
    await page.goto(`/projects/${p}/tasks`);
    await expect(page.getByRole('link', { name: 'child', exact: true })).toBeVisible();
    await expect(page.locator('.tasktable .task-name')).toHaveCount(2);
    await expect(page.locator('.tasktable .ministeps')).toHaveCount(2);
  } finally { await request.patch(`${api}/projects/${p}`, { data: { archived: true } }); }
});
