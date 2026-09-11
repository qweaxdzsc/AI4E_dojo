import {test,expect} from '@playwright/test';
import {readFileSync} from 'node:fs';
import {resolve} from 'node:path';
/** 实际 NASA 两模型差值来自已成功研究运行，浏览器不生成替代数组。 */
test('真实同身份 NASA 差值显示',async({page},testInfo)=>{
 const evidence=JSON.parse(readFileSync(process.env.DOJO_DIFFERENCE_EVIDENCE||resolve('../../.context/mvp/web-integrated-results/nasa-http-difference.json'),'utf8'));
 expect(evidence.exact_difference).toBe(true);const asset=evidence.operation.result_refs[0];const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('/projects');
 await page.evaluate(async asset=>{const React=await import('/node_modules/.vite/deps/react.js' as any),ReactDOM=await import('/node_modules/.vite/deps/react-dom_client.js' as any),{VisualizationWorkspace}=await import('/src/modules/visualization/index.ts' as any);const host=document.createElement('div');document.body.replaceChildren(host);(window as any).__differenceRoot=(ReactDOM.createRoot||ReactDOM.default.createRoot)(host);(window as any).__differenceRoot.render((React.createElement||React.default.createElement)(VisualizationWorkspace,{sources:[{...asset,name:'NASA 两模型同身份差值'}],mode:'comparison',onError:(e:Error)=>{(window as any).__differenceError=e.message;},onSceneChange:(s:any)=>{(window as any).__differenceScene=s;}}));},asset);
 await expect(page.getByRole('status')).toHaveCount(0,{timeout:120000});await expect(page.getByRole('alert')).toHaveCount(0);await expect(page.locator('.viz-canvas canvas')).toHaveCount(1);
 await expect(page.getByLabel('显示字段').locator('option')).not.toHaveCount(1);await page.getByLabel('显示字段').selectOption({index:1});await page.getByLabel('表示方式').selectOption('points');await page.waitForTimeout(500);
 const viewport=await page.locator('.viz-canvas').boundingBox(),workspace=await page.locator('.viz-workspace').boundingBox();expect(viewport!.height).toBeLessThan(workspace!.height);
 const image=await page.locator('.viz-canvas').screenshot({path:testInfo.outputPath('nasa-difference.png')});await testInfo.attach('真实NASA差值点云',{body:image,contentType:'image/png'});
 await page.getByRole('button',{name:'保存场景'}).click();const scene=await page.evaluate(()=>(window as any).__differenceScene);expect(scene.sources[0].revision).toBe(asset.revision);expect(scene.sources[0].member).toBe('difference.pt');expect(scene.viewports[0].field).toBeTruthy();expect(errors).toEqual([]);
 await page.evaluate(()=>(window as any).__differenceRoot.unmount());
});
