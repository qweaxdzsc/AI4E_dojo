import {test,expect} from '@playwright/test';
/** 明确标记的组件契约夹具，验证绘图与日志交互，不代替真实训练验收。 */
test('真实坐标绘图不将不规则 epoch 等距排列，单点仍可见',async({page})=>{
 await page.route('**/api/v1/**',route=>route.fulfill({json:[]}));
 await page.route('**/runs/fixture-run/metrics',route=>route.fulfill({json:{status:'succeeded',history:[{epoch:1,loss:3,updates:4,learning_rate:0.01},{epoch:2,loss:2,updates:7,learning_rate:0.005},{epoch:10,loss:1,updates:30,learning_rate:0}]}}));
 await page.route('**/runs/fixture-run/events',route=>route.fulfill({contentType:'text/event-stream',body:'data: '+JSON.stringify({status:'succeeded',text:'2026-09-14 10:00:00,123 INFO fixture ready\n[ERROR] fixture issue\nlegacy raw line'})+'\n\n'}));
 await page.route('**/runs/fixture-run/log',route=>route.fulfill({json:{text:'2026-09-14 10:00:00,123 INFO fixture ready\n[ERROR] fixture issue\nlegacy raw line'}}));
 await page.route('**/api/v1/projects/fixture/runs**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/metrics')||url.pathname.endsWith('/log')||url.pathname.endsWith('/events'))return route.fallback();
  return route.fulfill({json:[{id:'fixture-run',status:'succeeded',stages:['train']}]});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {TrainingMonitor}=await import('/src/modules/executions/TrainingMonitor.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(TrainingMonitor,{project:'fixture',task:'fixture',initialRun:'fixture-run'}))});
 await expect(page.getByRole('button',{name:'开始训练'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'准备并训练'})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'从检查点继续'})).toHaveCount(0);
 await expect(page.getByRole('combobox',{name:'已准备完成的数据集'})).toHaveCount(0);
 await expect(page.getByRole('combobox',{name:'查看运行'})).toBeVisible();
 const chart=page.getByRole('img',{name:'真实训练 Loss 曲线'});await expect(chart.locator('circle')).toHaveCount(3);
 const xs=await chart.locator('circle').evaluateAll(nodes=>nodes.map(n=>Number(n.getAttribute('cx'))));expect((xs[1]-xs[0])/(xs[2]-xs[0])).toBeCloseTo(1/9,5);
 for (const [tab, field, expected] of [['Loss','loss',['3','2','1']],['更新步','updates',['4','7','30']],['学习率','learning_rate',['0.01','0.005','0']]] as const) {
  await page.getByRole('tab',{name:tab,exact:true}).click();
  const current=page.getByRole('img',{name:`真实训练 ${tab} 曲线`,exact:true});
  await expect(current.locator('circle')).toHaveCount(3);
  expect(await current.locator('circle').evaluateAll(nodes=>nodes.map(n=>n.getAttribute('data-value')))).toEqual(expected);
  await page.getByRole('button',{name:`${tab}曲线配置`,exact:true}).click();
  const dialog=page.getByRole('dialog',{name:`${tab}曲线配置`});await expect(dialog).toBeVisible();
  await expect(dialog.locator('input,select,textarea')).toHaveCount(0);
  await dialog.getByRole('button',{name:'Close'}).click();
 }
 await page.getByRole('tab',{name:'Loss',exact:true}).click();
 await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'日志级别'})}).click();await page.getByText('ERROR',{exact:true}).click();await expect(page.getByLabel('运行日志内容')).toHaveText('[ERROR] fixture issue');await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'日志级别'})}).click();await page.locator('.ant-select-item-option').filter({hasText:'全部'}).click();
 await page.getByRole('textbox',{name:'搜索日志'}).fill('issue');await expect(page.getByLabel('运行日志内容')).toHaveText('[ERROR] fixture issue');
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'下载日志'}).click();expect((await download).suggestedFilename()).toBe('run-fixture-run.log');
 await page.getByRole('textbox',{name:'搜索日志'}).fill('');await page.getByRole('button',{name:'清空显示'}).click();await expect(page.getByLabel('运行日志内容')).toHaveText('无匹配日志');
 await page.route('**/runs/fixture-run/metrics',route=>route.fulfill({json:{status:'succeeded',history:[{epoch:7,loss:.25}]}}));await expect(chart.locator('circle')).toHaveCount(1);await expect(chart.locator('circle')).toHaveAttribute('cx','420');
});

test('进行中轮次显示在线分项，测试评估另列，无记录不编造',async({page})=>{
 let payload:any={status:'running',history:[]};
 await page.route('**/api/v1/**',route=>route.fulfill({json:[]}));
 await page.route('**/runs/live-run/metrics',route=>route.fulfill({json:payload}));
 await page.route('**/runs/live-run/events',route=>route.fulfill({contentType:'text/event-stream',body:'data: '+JSON.stringify({status:'running',text:''})+'\n\n'}));
 await page.route('**/runs/live-run/log',route=>route.fulfill({json:{text:''}}));
 await page.route('**/api/v1/projects/fixture/runs**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/metrics')||url.pathname.endsWith('/log')||url.pathname.endsWith('/events'))return route.fallback();
  return route.fulfill({json:[{id:'live-run',status:'running',stages:['train']}]});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {TrainingMonitor}=await import('/src/modules/executions/TrainingMonitor.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(TrainingMonitor,{project:'fixture',task:'fixture',initialRun:'live-run'}))});
 await expect(page.getByRole('img',{name:'真实训练 Loss 曲线'})).toHaveCount(0);
 await expect(page.getByText('尚无已记录的训练曲线')).toBeVisible();
 await expect(page.getByText('尚无在线分项或测试评估')).toBeVisible();
 payload={status:'running',history:[{epoch:1,loss:0.4,online:{loss:0.4,surface_pressure:0.2,volume_velocity:0.1}}]};
 await expect(page.getByRole('img',{name:'真实训练 Loss 曲线'}).locator('circle')).toHaveCount(1);
 await expect(page.getByRole('cell',{name:'在线'})).toHaveCount(2);
 await expect(page.getByRole('cell',{name:'测试评估'})).toHaveCount(0);
 await expect(page.getByRole('cell',{name:'surface_pressure'})).toBeVisible();
 payload={status:'running',history:[{epoch:1,loss:0.4,online:{loss:0.4,surface_pressure:0.2},evaluation:{metrics:{'surface_pressure/relative_l2':{value:0.08}}}}]};
 await expect(page.getByRole('cell',{name:'测试评估'})).toHaveCount(1);
 await expect(page.getByRole('cell',{name:'surface_pressure/relative_l2'})).toBeVisible();
});

/** 历史运行可缺少学习率；不能借 Loss 点数伪造另一条曲线。 */
test('曲线各自处理缺失值，学习率为零仍显示',async({page})=>{
 await page.route('**/api/v1/**',route=>route.fulfill({json:[]}));
 await page.route('**/runs/partial/metrics',route=>route.fulfill({json:{status:'succeeded',history:[{epoch:1,loss:2},{epoch:2,updates:8,learning_rate:0},{epoch:3,loss:1,learning_rate:null}]}}));
 await page.route('**/api/v1/projects/fixture/runs**',route=>new URL(route.request().url()).pathname.endsWith('/runs')?route.fulfill({json:[{id:'partial',stages:['train'],status:'succeeded'}]}):route.fallback());
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {TrainingMonitor}=await import('/src/modules/executions/TrainingMonitor.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(TrainingMonitor,{project:'fixture',task:'fixture',initialRun:'partial'}))});
 await expect(page.getByRole('img',{name:'真实训练 Loss 曲线'}).locator('circle')).toHaveCount(2);
 await page.getByRole('tab',{name:'学习率',exact:true}).click();
 const chart=page.getByRole('img',{name:'真实训练 学习率 曲线'});
 await expect(chart.locator('circle')).toHaveCount(1);await expect(chart.locator('circle')).toHaveAttribute('data-value','0');
 await page.getByRole('tab',{name:'更新步',exact:true}).click();await expect(page.getByRole('img',{name:'真实训练 更新步 曲线'}).locator('circle')).toHaveAttribute('data-value','8');
});
