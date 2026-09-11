import { test, expect } from '@playwright/test';
import path from 'node:path';
import fs from 'node:fs';
import { createHash } from 'node:crypto';

const api = (process.env.DOJO_API_URL || 'http://127.0.0.1:8002') + '/api/v1';
/** 从首页真实点击进入项目和任务，不用深链接跳过用户入口。 */
test('首页进入项目、进入任务及侧栏整行导航', async ({ page, request }, info) => {
  const name = `首页导航回归 ${Date.now()}`;
  const response = await request.post(api + '/projects', { data: { name, description: '真实持久化导航测试，结束后归档。' } });
  expect(response.ok()).toBeTruthy(); const project = await response.json();
  try {
    const created = await request.post(`${api}/projects/${project.id}/tasks`, { data: { name: '可进入的研究任务' } });
    expect(created.ok()).toBeTruthy(); const task = await created.json();
    await page.goto('/projects');
    await expect(page.getByRole('heading', { name: '项目管理', exact: true })).toBeVisible();
    const projectsMenu = page.getByRole('menuitem', { name: '项目管理', exact: true });
    const workbenchMenu = page.getByRole('menuitem', { name: '任务工作台', exact: true });
    await expect(projectsMenu).toHaveAttribute('aria-current', 'page');
    // 点击行内边缘而非只点击文字，防止视觉可点区域与链接不一致。
    await workbenchMenu.click({ position: { x: 8, y: 20 } });
    await expect(page).toHaveURL(/\/workbench(?:\?|$)/);
    await expect(page.getByRole('heading', { name: /任务工作台/ })).toBeVisible();
    await expect(page.getByText('请从项目的任务管理中选择任务，继续原始数据处理。')).toHaveCount(0);
    await projectsMenu.click({ position: { x: 8, y: 20 } });
    await expect(page).toHaveURL(/\/projects$/);
    await page.getByRole('textbox', { name: '搜索项目', exact: true }).fill(name);
    const card = page.locator('.projectgrid .taskcard').filter({ hasText: name });
    await expect(card).toHaveCount(1);
    await expect(card.locator('.projectfacts')).toContainText('任务数');
    await expect(card.locator('.projectfacts').getByText('1', { exact: true })).toBeVisible();
    await card.getByRole('link', { name: '进入项目', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/projects/${project.id}/tasks$`));
    await expect(page.getByRole('tab')).toHaveCount(6);
    await page.getByRole('link', { name: '进入工作台', exact: true }).click();
    await expect(page).toHaveURL(new RegExp(`/projects/${project.id}/tasks/${task.id}/1$`));
    await expect(page.locator('.workbench-steps .topstep')).toHaveCount(8);
    await expect(workbenchMenu).toHaveAttribute('aria-current', 'page');
    await page.reload();
    await expect(page.getByRole('heading', { name: new RegExp('^' + task.name) })).toBeVisible();
    await projectsMenu.click({ position: { x: 8, y: 20 } });
    await workbenchMenu.click({ position: { x: 8, y: 20 } });
    await expect(page).toHaveURL(new RegExp(`/projects/${project.id}/tasks/${task.id}/1$`));
    await page.screenshot({ path: info.outputPath('home-to-workbench.png'), fullPage: true });
  } finally {
    await request.patch(`${api}/projects/${project.id}`, { data: { archived: true } });
  }
});

/** 对照唯一整合HTML首页；真实业务数字不同，布局和装饰素材必须来自原型。 */
test('首页在两种桌面宽度下对照整合原型', async ({ browser, request }, info) => {
  const prefix = `首页布局回归 ${Date.now()}`; const ids: string[] = [];
  const actual = await browser.newPage(); const reference = await browser.newPage();
  const measurements: any[] = [];
  try {
    for (let i = 0; i < 4; i++) {
      const r = await request.post(api + '/projects', { data: { name: `${prefix} ${i}`, description: '真实项目的说明文本，布局对照不替代实际数据。' } });
      expect(r.ok()).toBeTruthy(); ids.push((await r.json()).id);
    }
    for (const width of [1440, 1920]) {
      await actual.setViewportSize({ width, height: 1000 }); await reference.setViewportSize({ width, height: 1000 });
      await reference.goto('file://' + path.resolve('../../docs/prototypes/dojo-web-integrated.html') + '#projects');
      await actual.goto((process.env.DOJO_WEB_URL || 'http://127.0.0.1:5174') + '/projects');
      await actual.getByRole('textbox', { name: '搜索项目', exact: true }).fill(prefix);
      await expect(actual.locator('.projectgrid .taskcard')).toHaveCount(4);
      await expect.poll(() => actual.locator('.projectcover').evaluateAll(images => images.every(e => (e as HTMLImageElement).complete && (e as HTMLImageElement).naturalWidth > 0))).toBeTruthy();
      const inspect = async (page: typeof actual) => page.evaluate(() => {
        const rect = (selector: string) => { const e = document.querySelector(selector); if (!e) throw new Error('missing ' + selector); const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return { x: r.x, y: r.y, width: r.width, height: r.height, background: s.backgroundColor, radius: s.borderRadius, font: s.fontSize }; };
        const elements = (selector: string) => Array.from(document.querySelectorAll(selector)).map(e => { const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, width: r.width, height: r.height }; });
        return { bar: rect('.projectbar'), grid: rect('.projectgrid'), card: rect('.taskcard'), cover: rect('.projectcover'), body: rect('.cardbody'), facts: rect('.projectfacts'), footer: rect('.cardfoot'), title: rect('.heading h1'), sidebarFooter: rect('.navbottom,.sidebar-footer'), header: rect('header'), menus: elements('.navitem'), controls: elements('.projectbar > *'), covers: Array.from(document.querySelectorAll<HTMLImageElement>('.projectcover')).map(e => ({ src: e.src, loaded: e.complete && e.naturalWidth > 0 })) };
      });
      const expected = await inspect(reference), current = await inspect(actual); measurements.push({ width, expected, current });
      for (const key of ['bar', 'card', 'cover', 'body', 'facts', 'footer', 'title', 'sidebarFooter', 'header'] as const) {
        for (const axis of ['x', 'y', 'width', 'height'] as const) expect(Math.abs(current[key][axis] - expected[key][axis]), `${width} ${key} ${axis}`).toBeLessThanOrEqual(2);
      }
      for (const [key, count] of [['menus', 2], ['controls', 5]] as const) {
        expect(current[key]).toHaveLength(count); expect(expected[key]).toHaveLength(count);
        for (let i = 0; i < count; i++) for (const axis of ['x', 'y', 'width', 'height'] as const) expect(Math.abs(current[key][i][axis] - expected[key][i][axis]), `${width} ${key}[${i}] ${axis}`).toBeLessThanOrEqual(2);
      }
      expect(current.card.radius).toBe(expected.card.radius); expect(current.card.background).toBe(expected.card.background);
      expect(current.covers.every(c => c.loaded)).toBeTruthy();
      const hashes = expected.covers.map(c => createHash('sha256').update(Buffer.from(c.src.split(',')[1], 'base64')).digest('hex'));
      for (const cover of current.covers) {
        const response = await request.get(cover.src); expect(response.ok()).toBeTruthy();
        expect(hashes).toContain(createHash('sha256').update(await response.body()).digest('hex'));
      }
      await actual.screenshot({ path: info.outputPath(`homepage-${width}.png`), fullPage: true });
      await reference.screenshot({ path: info.outputPath(`prototype-homepage-${width}.png`), fullPage: true });
    }
    await info.attach('homepage-measurements', { body: JSON.stringify(measurements, null, 2), contentType: 'application/json' });
  } finally {
    fs.writeFileSync(info.outputPath('homepage-measurements.json'), JSON.stringify(measurements, null, 2));
    await actual.close(); await reference.close();
    for (const id of ids) await request.patch(`${api}/projects/${id}`, { data: { archived: true } });
  }
});

/** 空项目从首页新建任务；最近任务失效后回到可用选择入口。 */
test('空项目新建任务后进入工作台，归档后不恢复失效任务', async ({ page, request }) => {
  const name = `首页空项目回归 ${Date.now()}`; let id: string | undefined;
  try {
    await page.goto('/projects');
    await page.getByRole('button', { name: '新建项目', exact: true }).click();
    await page.getByLabel('项目名称', { exact: true }).fill(name);
    const response = page.waitForResponse(r => r.url().endsWith('/api/v1/projects') && r.request().method() === 'POST');
    await page.getByRole('dialog').getByRole('button', { name: /确\s*定/ }).click();
    const result = await response; expect(result.ok()).toBeTruthy(); id = (await result.json()).id;
    await page.getByRole('textbox', { name: '搜索项目', exact: true }).fill(name);
    await page.locator('.taskcard').filter({ hasText: name }).getByRole('link', { name: '进入项目', exact: true }).click();
    await page.getByRole('button', { name: '创建第一个任务', exact: true }).click();
    await page.getByLabel('任务名称', { exact: true }).fill('从首页创建的任务');
    await page.getByRole('combobox',{name:'科研案例',exact:true}).click();await page.getByRole('option').first().click();
    await page.getByRole('dialog').getByRole('button', { name: '创建并进入原始处理',exact:true }).click();
    await expect(page.locator('.workbench-steps .topstep')).toHaveCount(8);
    await expect(page.getByRole('heading', { name: /^从首页创建的任务/ })).toBeVisible();
    await page.getByRole('link', { name: '切换任务', exact: true }).click();
    await expect(page).toHaveURL(/\/workbench\?choose=1$/);
    await expect(page.getByRole('combobox', { name: '选择工作台项目', exact: true })).toBeVisible();
    expect((await request.patch(`${api}/projects/${id}`, { data: { archived: true } })).ok()).toBeTruthy();
    await page.getByRole('menuitem', { name: '项目管理', exact: true }).click();
    await page.getByRole('menuitem', { name: '任务工作台', exact: true }).click();
    await expect(page).toHaveURL(/\/workbench$/);
    await expect(page.getByRole('link', { name: /继续上次任务：从首页创建的任务/ })).toHaveCount(0);
  } finally {
    if (id) await request.patch(`${api}/projects/${id}`, { data: { archived: true } });
  }
});
