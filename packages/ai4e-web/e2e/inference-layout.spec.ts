import {test,expect} from '@playwright/test';
import {inferenceFixture} from './inference-fixture';
import {mkdirSync,writeFileSync} from 'node:fs';
const root='/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/ui';
for(const [width,height] of [[1672,941],[1440,900],[1920,1080]])test(`推理参考图 ${width}x${height}`,async({page})=>{
 await page.setViewportSize({width,height});await inferenceFixture(page);await page.goto('/projects/p/tasks/t/infer');await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();await page.getByRole('tab',{name:/验证集/}).click();await page.getByRole('checkbox',{name:/全部筛选范围/}).check();await page.getByRole('checkbox',{name:'选择检查点 ckpt_127000 · train0',exact:true}).check();await page.getByRole('checkbox',{name:'选择检查点 ckpt_122000 · train1',exact:true}).check();await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(5);
 mkdirSync(root,{recursive:true});await page.screenshot({path:`${root}/${width}x${height}.png`,animations:"disabled"});const bounds=await page.locator('[data-region]').evaluateAll(es=>Object.fromEntries(es.map(e=>{const r=e.getBoundingClientRect();return [(e as HTMLElement).dataset.region,{x:r.x,y:r.y,width:r.width,height:r.height}]})));writeFileSync(`${root}/${width}x${height}-regions.json`,JSON.stringify(bounds,null,2));
 await expect(page.locator('.inference-workspace')).toBeVisible();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

for(const state of ["default","empty","running","config","long"])test(`推理状态 ${state}`,async({page})=>{
 await page.setViewportSize({width:state==="long"?1000:1672,height:941});
 await inferenceFixture(page,{completed:["running","config"].includes(state),empty:state==="empty",longNames:state==="long",status:state==="running"?"running":"succeeded"});
 await page.goto('/projects/p/tasks/t/infer');
 await expect(page.locator('.inference-workspace')).toHaveAttribute('aria-busy','false');
 if(state==="long"){
   await page.locator('[data-region="checkpoints"] .infer-choice input').first().check();
   await page.getByRole('tab',{name:/验证集/}).click();
   await expect(page.locator('[data-region="samples"] .infer-choice')).toHaveCount(50);
 }
 if(state==="config"){
   await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(5);
   await page.locator('[data-region="table"]').getByRole('button',{name:'配置',exact:true}).click();
   await expect(page.getByRole('dialog')).toBeVisible();
   await expect(page.getByRole('dialog')).toHaveCSS('opacity','1');
   await expect(page.getByRole('dialog')).toHaveCSS('transform','none');
   const box=await page.getByRole('dialog').boundingBox();
   expect(box!.y).toBeGreaterThanOrEqual(0);expect(box!.y+box!.height).toBeLessThanOrEqual(941);
 }
 if(state==="running")await expect(page.locator('.infer-details').first()).toHaveAttribute('open','');
 if(state==="default"||state==="empty")await expect(page.getByRole('button',{name:'开始计算',exact:true})).toBeDisabled();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
 await page.screenshot({path:`${root}/state-${state}.png`,animations:'disabled'});
});

test('推理配置分行且标题不带序号',async({page})=>{
 await page.setViewportSize({width:1672,height:941});
 await inferenceFixture(page);
 await page.goto('/projects/p/tasks/t/infer');
 await expect(page.locator('.inference-workspace')).toHaveAttribute('aria-busy','false');
 const titles=await page.locator('.inference-workspace .infer-card h3').allTextContents();
 for(const title of titles)expect(title.trim(),title).not.toMatch(/^\d+\.\s/);
 await expect(page.locator('[data-region="checkpoints"] h3')).toContainText('Checkpoint');
 await expect(page.locator('[data-region="samples"] h3')).toContainText('样本');
 await expect(page.locator('[data-region="fields"] h3')).toContainText('物理量');
 await expect(page.locator('[data-region="metrics"] h3')).toContainText('指标');
 await expect(page.locator('[data-region="settings"] h3')).toHaveText('推理配置');
 await expect(page.locator('[data-region="table"] h3')).toHaveText('指标表格');
 await expect(page.locator('[data-region="chart"] h3')).toHaveText('折线图');
 const settings=page.locator('[data-region="settings"]');
 await expect(settings).toContainText('执行设备');
 await expect(settings).toContainText('查询块大小');
 await expect(settings.getByRole('combobox',{name:'推理设备'})).toBeVisible();
 await expect(settings.getByRole('spinbutton',{name:'推理查询块大小'})).toBeVisible();
 await expect(settings.getByRole('checkbox',{name:'评估指标'})).toBeVisible();
 await expect(settings.getByRole('checkbox',{name:'导出点云数据'})).toBeVisible();
 await expect(settings.getByRole('checkbox',{name:'导出VTK网格化数据'})).toBeVisible();
 await settings.getByRole('checkbox',{name:'导出VTK网格化数据'}).uncheck();
 await expect(settings.getByText('已关闭导出 VTK 网格化数据')).toBeVisible();
 await expect(settings.locator('.infer-vtk-note')).toBeVisible();
 const contained=await settings.evaluate(el=>{
  const box=el.getBoundingClientRect();
  const table=document.querySelector('[data-region="table"]')!.getBoundingClientRect();
  const overflow=el.scrollWidth>el.clientWidth+1||el.scrollHeight>el.clientHeight+1;
  return {overflow,belowTable:box.bottom>table.top+1,textClipped:[...el.querySelectorAll('h3,label,button,.infer-budget,.infer-vtk-note,.ant-alert')].some(node=>{
   const r=node.getBoundingClientRect();
   return r.width>0&&(r.right>box.right+2||r.bottom>box.bottom+2||r.left<box.left-2);
  })};
 });
 expect(contained.overflow).toBeFalsy();
 expect(contained.belowTable).toBeFalsy();
 expect(contained.textClipped).toBeFalsy();
 expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();
});

test('无VTK来源时网格化导出置灰',async({page})=>{
 await page.setViewportSize({width:1672,height:941});
 await inferenceFixture(page,{meshUnavailable:true});
 await page.goto('/projects/p/tasks/t/infer');
 await expect(page.locator('.inference-workspace')).toHaveAttribute('aria-busy','false');
 const mesh=page.locator('[data-region="settings"]').getByRole('checkbox',{name:'导出VTK网格化数据'});
 await expect(mesh).toBeDisabled();
 await expect(mesh).not.toBeChecked();
 await expect(page.getByText('当前训练集没有可还原的 VTK 网格')).toBeVisible();
 await expect(page.locator('[data-region="settings"]').getByRole('checkbox',{name:'导出点云数据'})).toBeEnabled();
});

test('样本目录缺少导出能力时网格化置灰',async({page})=>{
 await page.setViewportSize({width:1672,height:941});
 await inferenceFixture(page,{omitVtkExports:true});
 await page.goto('/projects/p/tasks/t/infer');
 await expect(page.locator('.inference-workspace')).toHaveAttribute('aria-busy','false');
 const mesh=page.locator('[data-region="settings"]').getByRole('checkbox',{name:'导出VTK网格化数据'});
 await expect(mesh).toBeDisabled();
 await expect(mesh).not.toBeChecked();
 await expect(page.getByText('当前训练集没有可还原的 VTK 网格')).toBeVisible();
});
