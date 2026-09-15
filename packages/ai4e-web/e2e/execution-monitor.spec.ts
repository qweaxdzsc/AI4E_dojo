import {test,expect} from '@playwright/test';
/** 明确标记的组件契约夹具，验证绘图与日志交互，不代替真实训练验收。 */
test('真实坐标绘图不将不规则 epoch 等距排列，单点仍可见',async({page})=>{
 await page.route('**/api/v1/**',route=>route.fulfill({json:[]}));
 await page.route('**/runs/fixture-run/metrics',route=>route.fulfill({json:{status:'succeeded',history:[{epoch:1,loss:3},{epoch:2,loss:2},{epoch:10,loss:1}]}}));
 await page.route('**/runs/fixture-run/events',route=>route.fulfill({contentType:'text/event-stream',body:'data: '+JSON.stringify({status:'succeeded',text:'2026-09-14 10:00:00,123 INFO fixture ready\n[ERROR] fixture issue\nlegacy raw line'})+'\n\n'}));
 await page.route('**/runs/fixture-run/log',route=>route.fulfill({json:{text:'2026-09-14 10:00:00,123 INFO fixture ready\n[ERROR] fixture issue\nlegacy raw line'}}));
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {TrainingMonitor}=await import('/src/modules/executions/TrainingMonitor.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(TrainingMonitor,{project:'fixture',run:'fixture-run',runs:[],inputs:[],onRun:()=>{},onStart:()=>{},onInput:()=>{},busy:false}))});
 const chart=page.getByRole('img',{name:'真实训练 Loss 曲线'});await expect(chart.locator('circle')).toHaveCount(3);
 const xs=await chart.locator('circle').evaluateAll(nodes=>nodes.map(n=>Number(n.getAttribute('cx'))));expect((xs[1]-xs[0])/(xs[2]-xs[0])).toBeCloseTo(1/9,5);
 await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'日志级别'})}).click();await page.getByText('ERROR',{exact:true}).click();await expect(page.getByLabel('运行日志内容')).toHaveText('[ERROR] fixture issue');await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'日志级别'})}).click();await page.locator('.ant-select-item-option').filter({hasText:'全部'}).click();
 await page.getByRole('textbox',{name:'搜索日志'}).fill('issue');await expect(page.getByLabel('运行日志内容')).toHaveText('[ERROR] fixture issue');
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'下载日志'}).click();expect((await download).suggestedFilename()).toBe('run-fixture-run.log');
 await page.getByRole('textbox',{name:'搜索日志'}).fill('');await page.getByRole('button',{name:'清空显示'}).click();await expect(page.getByLabel('运行日志内容')).toHaveText('无匹配日志');
 await page.route('**/runs/fixture-run/metrics',route=>route.fulfill({json:{status:'succeeded',history:[{epoch:7,loss:.25}]}}));await expect(chart.locator('circle')).toHaveCount(1);await expect(chart.locator('circle')).toHaveAttribute('cx','420');
});
