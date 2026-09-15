import {test,expect} from '@playwright/test';
import {inferenceFixture} from './inference-fixture';
import {mkdirSync,writeFileSync} from 'node:fs';
const root='/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/ui';
for(const [width,height] of [[1672,941],[1440,900],[1920,1080]])test(`推理参考图 ${width}x${height}`,async({page})=>{
 await page.setViewportSize({width,height});await inferenceFixture(page);await page.goto('/projects/p/tasks/t/infer');await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();await page.getByRole('tab',{name:/验证集/}).click();await page.getByRole('checkbox',{name:/全部筛选范围/}).check();await page.getByRole('checkbox',{name:'选择检查点 ckpt_127000 · train1',exact:true}).check();await page.getByRole('checkbox',{name:'选择检查点 ckpt_126000 · train2',exact:true}).check();await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(5);
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
