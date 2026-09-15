import {test, expect} from '@playwright/test';

const project = process.env.DOJO_TRAME_PROJECT;
const task = process.env.DOJO_TRAME_TASK;

/** 真实研究页面引用已有文件并登记来源；不训练、不改任务配置、不保存新版本。 */
test('原始VTK预览与后处理默认打开真实Trame', async ({page}, info) => {
  test.skip(!project || !task, '需要明确提供已有项目与任务，不能用跳过代替真实验收');
  await page.setViewportSize({width:1440,height:1000});
  const route = `/projects/${project}/tasks/${task}/`;
  const opened: string[] = [], closed: string[] = [];
  let sourceId = "";
  page.on('response', async response => {
    if (response.url().endsWith('/assets') && response.request().method()==='POST' && response.ok()) sourceId=(await response.json()).asset_id;
    if (response.url().endsWith('/visualizations/sessions') && response.request().method()==='POST' && response.ok()) opened.push((await response.json()).session_id);
    if (response.url().includes('/visualizations/sessions/') && response.request().method()==='DELETE' && response.ok()) closed.push(response.url().split('/').at(-1)!);
  });
  try {
    await page.goto(route+'1');
    await page.getByRole('button',{name:'param1',exact:true}).click();
    await page.locator('.folderrow').getByRole('button').filter({hasText:/^[0-9a-f]{32}$/}).first().click();
    await page.getByRole('button',{name:'预览 quadpress_smpl.vtk',exact:true}).click();
    const outer = page.frameLocator('iframe[title="独立可视化应用"]');
    const inner = outer.frameLocator('iframe[title="三维物理场 Trame 工作台"]');
    await expect(inner.locator('.phys-tree').getByText('基础显示',{exact:true})).toBeVisible({timeout:90000});
    await expect(page.locator('.viz-workspace')).toHaveCount(0);
    await expect(page.getByRole('combobox',{name:'预览字段',exact:true})).toHaveCount(0);
    await inner.getByLabel('着色物理量',{exact:true}).click();
    await inner.getByRole('option',{name:'point_scalars (point)',exact:true}).click();
    await inner.getByRole('button',{name:'轴测',exact:true}).click();
    await expect(inner.locator('canvas').first()).toBeVisible();
    const properties=inner.locator('.phys-property-scroll');
    await expect(properties).toBeVisible();
    await properties.evaluate(el=>{(el as HTMLElement).scrollTop=(el as HTMLElement).scrollHeight;});
    await expect(inner.locator('.phys-property-footer')).toBeVisible();
    await page.getByRole('button',{name:'放大到全屏幕'}).click();
    await expect.poll(async()=>inner.locator('.phys-viewport').evaluate(el=>(el as HTMLElement).offsetHeight)).toBeGreaterThan(200);
    await expect(inner.locator('.phys-tree')).toBeVisible();
    await expect(properties).toBeVisible();
    await page.getByRole('button',{name:'退出全屏幕'}).click();
    // WebSocket 场景与本地 VTK 画布异步刷新，截图等待本帧渲染稳定。
    await page.waitForTimeout(1000);
    await page.screenshot({path:info.outputPath('raw-vtk-trame.png')});
    await expect.poll(()=>opened.length).toBe(1);
    await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
    await expect.poll(()=>closed.includes(opened[0])).toBe(true);

    await page.goto(route+'6');
    await expect(inner.locator('.phys-tree')).toBeVisible({timeout:90000});
    await expect(page.locator('.post-visualization-layout>.phys-host')).toBeVisible();
    await expect(page.locator('.post-visualization-layout .viz-workspace')).toHaveCount(0);
    await expect.poll(()=>opened.length).toBe(2);
    // 在真实宿主菜单中追加受控来源，确认并非只展示空 iframe。
    await inner.getByRole('button',{name:'文件',exact:true}).click();
    await inner.getByText('导入结果',{exact:true}).click();
    await outer.getByRole('combobox',{name:'结果资产',exact:true}).fill(sourceId);
    await outer.locator('.ant-select-item-option').filter({hasText:sourceId}).click();
    await outer.getByRole('dialog').getByRole('button',{name:'确 定',exact:true}).click();
    await expect(inner.locator('.phys-tree').getByText('基础显示',{exact:true})).toBeVisible({timeout:90000});
    await expect.poll(()=>opened.length).toBe(2);
    await inner.getByLabel('着色物理量',{exact:true}).click();
    await inner.getByRole('option',{name:'point_scalars (point)',exact:true}).click();
    await inner.getByRole('button',{name:'视角',exact:true}).click();
    await inner.locator('.v-menu__content.menuable__content__active .v-list-item__title').filter({hasText:/^\s*轴测\s*$/}).click();
    await expect(inner.locator('.v-menu__content.menuable__content__active')).toHaveCount(0);
    await page.waitForTimeout(1000);
    await page.screenshot({path:info.outputPath('post-import-trame.png')});
    await page.getByRole('menuitem',{name:'项目管理',exact:true}).click();
    await expect.poll(()=>closed.includes(opened[1])).toBe(true);
  } finally {
    for (const id of opened) await page.request.delete(`/api/v1/projects/${project}/tasks/${task}/visualizations/sessions/${id}`);
  }
});

/** 迟到的建会话响应必须释放，不允许已关闭预览重新出现或泄漏工作进程。 */
test('关闭预览后回收迟到的会话', async ({page}) => {
  let release: () => void = () => {};
  const pending = new Promise<void>(resolve => {release=resolve;});
  const closed: string[] = [];
  await page.route('**/api/v1/projects', route => route.fulfill({json: []}));
  await page.route('**/api/v1/projects/fixture/tasks', route => route.fulfill({json: [{id:'task',name:'测试任务'}]}));
  await page.route('**/api/v1/projects/fixture/tasks/task/visualizations', route => route.fulfill({json:{items:[]}}));
  await page.route('**/api/v1/projects/fixture/tasks/task/visualizations/sessions', async route => {
    await pending;
    await route.fulfill({json:{session_id:'late',embed_url:'/fixture-view'}});
  });
  await page.route('**/api/v1/projects/fixture/tasks/task/visualizations/sessions/late', async route => {
    closed.push(route.request().method());await route.fulfill({json:{status:'closed'}});
  });
  await page.goto('/projects');
  const opening = page.waitForRequest(r=>r.url().endsWith('/visualizations/sessions') && r.method()==='POST');
  await page.evaluate(async () => {
    const {default: React} = await import('/node_modules/.vite/deps/react.js');
    const {default: DOM} = await import('/node_modules/.vite/deps/react-dom_client.js');
    const {VisualizationWorkspace} = await import('/src/modules/visualization/index.ts');
    const host=document.createElement('div');document.body.append(host);
    const root=DOM.createRoot(host);(window as any).__trameTestRoot=root;
    root.render(React.createElement(VisualizationWorkspace,{sources:[],scope:{project_id:'fixture',task_id:'task'}}));
  });
  await opening;
  await page.evaluate(()=>(window as any).__trameTestRoot.unmount());
  release();
  await expect.poll(()=>closed).toEqual(['DELETE']);
  await expect(page.locator('iframe[title="独立可视化应用"]')).toHaveCount(0);
});
