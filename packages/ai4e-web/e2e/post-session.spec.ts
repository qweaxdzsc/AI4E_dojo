import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';
test('反复切换Tab保持iframe文档且退出回收',async({page})=>{const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post');await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();const frame=page.frameLocator('iframe[title="独立可视化应用"]');await frame.getByLabel('相机状态').fill('已经旋转');
 for(let i=0;i<10;i++){await page.getByRole('tab',{name:'结果文件',exact:true}).click();await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();}
 await expect(frame.getByLabel('相机状态')).toHaveValue('已经旋转');expect(state.creates).toBe(1);expect(state.closes).toBe(0);await page.getByRole('tab',{name:'结果文件',exact:true}).click();await page.getByLabel('搜索结果文件').fill('pressure.vtp');await page.getByRole('button',{name:'可视化',exact:true}).filter({visible:true}).first().click();await expect(page.locator('.phys-host iframe')).toBeVisible();expect(state.creates).toBe(1);
 await page.getByRole('link',{name:'← 上一步',exact:true}).click();await expect.poll(()=>state.closes).toBe(1);
});

test('三维页占满剩余视口且宿主iframe贴合',async({page})=>{
 await page.setViewportSize({width:1440,height:1000});
 await postFixture(page);
 await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();
 const frame=page.locator('iframe[title="独立可视化应用"]');
 await expect(frame).toBeVisible();
 await expect(page.getByRole('combobox',{name:'重新打开可视化'})).toHaveCount(0);
 const metrics=await page.evaluate(()=>{
  const host=document.querySelector('.phys-host') as HTMLElement;
  const iframe=document.querySelector('iframe[title="独立可视化应用"]') as HTMLElement;
  const stage=document.querySelector('.workbench-stage') as HTMLElement;
  const hr=host.getBoundingClientRect(),fr=iframe.getBoundingClientRect();
  return {hostHeight:hr.height,frameHeight:fr.height,hostBottom:hr.bottom,viewport:window.innerHeight,stageHeight:stage.getBoundingClientRect().height,stageOverflow:getComputedStyle(stage).overflowY,shellOverflow:getComputedStyle(document.querySelector('.platform-shell') as HTMLElement).overflowY};
 });
 expect(metrics.stageHeight).toBeGreaterThanOrEqual(1148);
 expect(metrics.hostHeight).toBeGreaterThan(840);
 expect(metrics.frameHeight).toBeGreaterThan(metrics.hostHeight*0.92);
 expect(metrics.hostBottom).toBeGreaterThan(metrics.viewport-90);
 expect(['auto','scroll']).toContain(metrics.stageOverflow);
 expect(metrics.shellOverflow).not.toBe('hidden');
});

test('显式重开替换iframe文档，同页hash地址不复用旧接管状态',async({page})=>{
 await postFixture(page);let created=0;
 await page.route('**/visualizations/sessions',route=>route.fulfill({json:{session_id:'s'+(++created),embed_url:'/post-test-frame#s'+created,status:'ready'}}));
 await page.goto('/projects/p/tasks/t/post');await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();
 const frame=page.frameLocator('iframe[title="独立可视化应用"]');await frame.getByLabel('相机状态').fill('旧文档');
 await frame.locator('body').evaluate(()=>window.parent.postMessage({type:'ai4e-vis:session-open',request_id:'reopen-test',visualization_id:'asset'},window.location.origin));
 await expect(page.locator('.phys-host')).toHaveAttribute('data-session-id','s2');
 await expect(frame.getByLabel('相机状态')).toHaveValue('初始');
 await page.getByRole('tab',{name:'结果文件',exact:true}).click();await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();expect(created).toBe(2);
});

test('会话满员后自动重试并挂上iframe',async({page})=>{
 await postFixture(page);let created=0;
 await page.route('**/visualizations/sessions',async route=>{
  if(route.request().method()!=='POST')return route.fallback();
  created++;
  if(created===1)return route.fulfill({status:400,json:{detail:'phys_session_capacity'}});
  return route.fulfill({json:{session_id:'ready'+created,embed_url:'/post-test-frame',status:'ready'}});
 });
 await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();
 await expect(page.locator('.phys-host')).toHaveAttribute('data-session-id','ready2');
 await expect(page.locator('iframe[title="独立可视化应用"]')).toBeVisible();
 expect(created).toBe(2);
});
