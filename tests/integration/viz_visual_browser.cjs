/** 对照用户参考图检查真实工作台布局和表单，截图尺寸保持可复核。 */
const {chromium,expect}=require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs=require('node:fs');
(async()=>{
 const root=process.env.VIS_EVIDENCE_ROOT;if(!root)throw new Error('请指定证据目录');
 const base=process.env.VIS_BROWSER_URL||'http://127.0.0.1:18093';
 const context=JSON.parse(fs.readFileSync(root+'/context.json')).context_id;
 const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1672,height:940}});page.setDefaultTimeout(45000);
 const errors=[],sessions=[],metrics=[];page.on('pageerror',e=>errors.push(e.message));page.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 page.on('response',async r=>{if(r.url().endsWith('/api/phys/sessions')&&r.ok()&&r.request().method()==='POST')sessions.push((await r.json()).session_id)});
 const command=async body=>{const r=await page.request.post(`${base}/api/phys/sessions/${sessions.at(-1)}/commands`,{data:{context_id:context,command:body}});expect(r.ok(),await r.text()).toBe(true);return r.json()};
 try{
  await page.goto(`${base}/workspace/#/phys?embed=1&context=${context}`);await page.getByRole('button',{name:'新建工作区'}).click();
  const f=page.frameLocator('iframe');await f.locator('.phys-tree').getByText('基础显示',{exact:true}).waitFor();
  await f.getByLabel('着色物理量',{exact:true}).click();await f.getByRole('option',{name:'pressure.truth (point)',exact:true}).click();
  await f.getByRole('button',{name:'轴测',exact:true}).click();
  await f.getByRole('button',{name:'切面',exact:true}).click();
  for(const [i,axis]of [...'XYZ'].entries())await f.getByLabel(`原点 ${axis}`,{exact:true}).fill(String([0,.65,0][i]));
  await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.pipeline.some(n=>n.type==='slice')).toBe(true);
  expect((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice').parameters.origin).toEqual([0,.65,0]);
  await f.getByLabel('着色物理量',{exact:true}).click();await f.getByRole('option',{name:'pressure.truth (point)',exact:true}).click();
  // 同场多个色标分别布局；展示截图只开启切面色标，保持对象独立设置。
  await f.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
  await f.getByRole('button',{name:'色标',exact:true}).click();
  await f.locator('.phys-tree').getByText('切面 1',{exact:true}).click();
  await f.locator('.phys-property-scroll').evaluate(el=>el.scrollTop=0);
  await expect(f.getByText('显示辅助平面',{exact:true})).toBeVisible();
  for(const width of [1672,1440,1920,900]){
   await page.setViewportSize({width,height:width===1920?1080:width===1440?900:941});await page.waitForTimeout(900);
   const m=await f.locator('.phys-workbench').evaluate(el=>{const rect=selector=>{const r=el.querySelector(selector).getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}};return {width:el.clientWidth,creation:rect('.phys-creation'),sidebar:rect('.phys-sidebar'),viewbar:rect('.phys-viewbar'),viewport:rect('.phys-viewport'),properties:rect('.phys-property-scroll'),overflow:el.scrollWidth>el.clientWidth,icons:[...el.querySelectorAll('.phys-analysis-main .phys-icon')].filter(i=>i.complete && i.naturalWidth>0).length}});
    expect(m.overflow).toBe(false);expect(m.creation.height).toBeLessThanOrEqual(82);expect(m.viewbar.height).toBeLessThanOrEqual(70);expect(m.viewport.height).toBeGreaterThan(520);expect(m.properties.height).toBeGreaterThan(300);expect(m.properties.height).toBeLessThanOrEqual(480);expect(m.icons).toBe(7);
   if(width>1100){expect(m.sidebar.width/width).toBeGreaterThan(.21);expect(m.sidebar.width/width).toBeLessThan(.26)}
   else await expect(f.getByRole('button',{name:'更多分析',exact:true})).toBeVisible();
   await expect(f.getByRole('button',{name:'光照设置',exact:true})).toBeInViewport();
   metrics.push(m);await page.screenshot({path:root+`/reference-layout-${width}.png`});
  }
  expect(errors).toEqual([]);fs.writeFileSync(root+'/visual-results.json',JSON.stringify({status:'passed',metrics,errors},null,2));console.log('PASS reference layout');
 }catch(e){await page.screenshot({path:root+'/visual-failure.png'});console.error(errors);console.error((await page.locator('body').innerText()).slice(-1200));throw e}
 finally{for(const id of sessions)await page.request.delete(`${base}/api/phys/sessions/${id}`,{params:{context_id:context}});await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
