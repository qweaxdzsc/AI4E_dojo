/** 独立物理工作台真实浏览器验收；数据与输出全部位于显式运行目录。 */
const {chromium, expect} = require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
(async () => {
 const base=process.env.VIS_BROWSER_URL || 'http://127.0.0.1:18091';
 const context=process.env.VIS_CONTEXT;
 const root=process.env.VIS_EVIDENCE_ROOT;
 if(!context||!root)throw new Error('VIS_CONTEXT 与 VIS_EVIDENCE_ROOT 必须显式指定');
 fs.mkdirSync(root,{recursive:true});
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1600,height:1100}});
 const assetName='浏览器真实物理场 '+Date.now();
 const sessions=[]; page.on('response', async r=>{if(r.url().endsWith('/api/phys/sessions') && r.request().method()==='POST' && r.ok()){const v=await r.json(); sessions.push(v.session_id);}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 try {
  await page.goto(`${base}/workspace/#/phys?embed=1&context=${context}`);
  if(process.env.VIS_RENDERER === 'remote') {
    await page.getByRole('combobox',{name:'渲染方式'}).press('ArrowDown');
    await page.getByText('远程渲染',{exact:true}).click();
  }
  const created=page.waitForResponse(r=>r.url().endsWith('/api/phys/sessions')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'新建工作区'}).click();
  const session=await (await created).json();
  if(!session.session_id)throw new Error(JSON.stringify(session));
  const frame=page.frameLocator('iframe');
  await frame.getByText('Apply 显示',{exact:true}).waitFor({timeout:45000});
  await frame.getByLabel('字段名（空为纯色）').click();
  await frame.getByRole('option', {name: 'RTData', exact: true}).click();
  await frame.getByText('Apply 显示',{exact:true}).click();
  const canvas=frame.locator('canvas').first();
  await expect(canvas).toBeVisible();
  const box=await canvas.boundingBox();
  await page.mouse.move(box.x+box.width*.45,box.y+box.height*.45);
  await page.mouse.down();await page.mouse.move(box.x+box.width*.62,box.y+box.height*.6,{steps:12});await page.mouse.up();
  await page.getByRole('button',{name:'保存配置',exact:true}).click();
  await page.getByLabel('可视化名称').fill(assetName);
  const savingResponse = page.waitForResponse(r => r.url().endsWith('/api/visualizations') && r.request().method() === 'POST');
  await page.getByRole('button',{name:'确 定'}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0,{timeout:15000});
  const saved = await (await savingResponse).json();
  if(!saved.visualization_id) throw new Error(JSON.stringify(saved));
  const detail=await (await page.request.get(`${base}/api/visualizations/${saved.visualization_id}?context_id=${context}`)).json();
  if(detail.spec.layers[0].field.name!=='RTData')throw new Error('显示字段未保存');
  await page.screenshot({path:path.join(root,'physical-scalar.png')});
  await page.getByRole('button',{name:'显式导出'}).click();
  const download=page.getByRole('link',{name:'view.png'});
  await expect(download).toBeVisible({timeout:45000});
  const file=await page.request.get(new URL(await download.getAttribute('href'), base).href);
  if(!file.ok())throw new Error('PNG 下载失败');
  fs.writeFileSync(path.join(root,'download.png'),await file.body());
  await page.getByRole('button',{name:'录制视口',exact:true}).click();
  for(let i=0;i<4;i++){
   await page.mouse.move(box.x+box.width*.45,box.y+box.height*.45);await page.mouse.down();await page.mouse.move(box.x+box.width*.55,box.y+box.height*.55,{steps:10});await page.mouse.up();
  }
  await page.getByRole('button',{name:'停止录制'}).click();
  const webm=page.getByRole('link',{name:'recording.webm'});
  await expect(webm).toBeVisible({timeout:15000});
  fs.writeFileSync(path.join(root,'recording.webm'),await (await page.request.get(new URL(await webm.getAttribute('href'), base).href)).body());
  require('node:child_process').execFileSync('uv', ['run', '--no-sync', 'python', '-c',
    'import imageio.v2 as io,sys; frame=io.get_reader(sys.argv[1]).get_data(0); assert frame.shape[:2]==(720,1280) and frame.std()>5, str(frame.shape)',
    path.join(root,'recording.webm')], {cwd:path.resolve(__dirname,'../..')});
  // 浏览器重新加载后通过任务索引找回配置，不依赖旧工作进程。
  await page.reload();
  await page.request.delete(base+'/api/phys/sessions/'+session.session_id+'?context_id='+context);
  await page.getByRole('combobox',{name:'已保存可视化'}).click();
  await page.getByText(assetName+' · r1',{exact:true}).click();
  await page.frameLocator('iframe').getByText('Apply 显示',{exact:true}).waitFor({timeout:45000});
  const reopened = page.frameLocator('iframe');
  await reopened.getByText('拾取所选节点实体（单击视口）',{exact:true}).click();
  const pickingBox=await reopened.locator('canvas').first().boundingBox();
  await page.mouse.click(pickingBox.x+pickingBox.width*.5,pickingBox.y+pickingBox.height*.5);
  await expect(reopened.locator('pre').filter({hasText:'"id":'})).toBeVisible();
  await reopened.getByLabel('X,Y,Z', {exact:true}).fill('0,0,0');
  await reopened.getByText('查询坐标',{exact:true}).click();
  await expect(reopened.locator('pre').filter({hasText:'RTData'})).toBeVisible();
  await reopened.getByText('Apply 处理',{exact:true}).click();
  await expect(reopened.getByText('filter-1 · slice',{exact:true})).toBeVisible();
  if(errors.length)throw new Error(errors.join('\n'));
  fs.writeFileSync(path.join(root,'browser-results.json'),JSON.stringify({status:'passed',source:'analytic VTK volume',renderer:process.env.VIS_RENDERER||'local',asset:saved.visualization_id,checks:['render','scalar apply','camera drag','save','PNG download','WebM recording','reload and reopen','coordinate probe','entity picking','slice Apply'],errors},null,2));
  console.log('PASS',saved.visualization_id);
 }catch(e){await page.screenshot({path:path.join(root,'failure.png')});throw e;}finally{for(const id of sessions)await page.request.delete(base+'/api/phys/sessions/'+id+'?context_id='+context);await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
