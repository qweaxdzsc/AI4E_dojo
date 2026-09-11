import {test,expect} from '@playwright/test';
import fs from 'node:fs';import path from 'node:path';
/** 从平台选择冻结准备输入，执行正式模型的真实 CPU TorchVista 跟踪。 */
test('正式模型检查操作到沙箱图形渲染',async({page},info)=>{
 test.setTimeout(300000);
 const e=JSON.parse(fs.readFileSync(path.resolve('../../.context/mvp/web-integrated-results/shapenet_car_transolver3_surface.json'),'utf8'));
 const errors:string[]=[];page.on('pageerror',error=>errors.push(error.message));await page.goto(`/projects/${e.project}/tasks/${e.task}/3`);
 for(const [binding,run] of [['train.manifest',e.stages.rawprep.id],['train.preparation',e.stages.trainprep.id]]){await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:binding,exact:true})}).click();await page.locator('.ant-select-item-option').filter({hasText:run.slice(0,8)}).first().click();}
 await expect(page.locator('.execution-log')).toHaveCount(0);const submitted=page.waitForResponse(r=>r.url().endsWith('/model-inspections')&&r.request().method()==='POST');await page.getByRole('button',{name:'生成真实模型结构',exact:true}).click();const operation=await(await submitted).json();expect(operation.operation_id).toBeTruthy();
 const iframe=page.locator('iframe[title="真实模型结构"]');await expect(iframe).toBeVisible({timeout:270000});await expect(iframe).toHaveAttribute('sandbox','allow-scripts');const content=page.frameLocator('iframe[title="真实模型结构"]');await expect(content.locator('svg').first()).toBeVisible({timeout:30000});await expect.poll(()=>content.locator('svg g[class^="node_"]').count(),{timeout:30000}).toBeGreaterThan(0);expect(errors).toEqual([]);await page.screenshot({path:info.outputPath('real-torchvista.png'),fullPage:true});await info.attach('operation',{body:JSON.stringify(operation,null,2),contentType:'application/json'});
});
