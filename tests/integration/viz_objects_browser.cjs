/** 对象工作台真实浏览器流程；失败保存截图，结束释放本次会话。 */
const {chromium,expect}=require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs=require('node:fs');
const root=process.env.VIS_EVIDENCE_ROOT;
if(!root)throw new Error('必须提供 VIS_EVIDENCE_ROOT');
const base=process.env.VIS_BROWSER_URL||'http://127.0.0.1:18093';
const context=process.env.VIS_CONTEXT||JSON.parse(fs.readFileSync(root+'/context.json')).context_id;
(async()=>{
 const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:1000}});const errors=[],ids=[];
 if(process.env.VIS_DEBUG)await p.route('**/trame-vtk.js',async route=>{const response=await route.fetch();const body=(await response.text()).replace('t[r[0]].apply(null,LD(a,r[1]))',"(typeof t[r[0]]==='function'?t[r[0]].apply(null,LD(a,r[1])):(()=>{throw Error('SYNC '+JSON.stringify({type:e.type,id:e.id,method:r[0],actual:t.getClassName()}))})())");await route.fulfill({response,body});});
 p.on('pageerror',e=>errors.push(e.stack||e.message));p.on('console',m=>{if(m.type()==='error')errors.push(m.text())});
 p.on('response',async r=>{if(r.url().endsWith('/api/phys/sessions')&&r.request().method()==='POST'&&r.ok())ids.push((await r.json()).session_id)});
 const command=async body=>{const r=await p.request.post(`${base}/api/phys/sessions/${ids.at(-1)}/commands`,{data:{context_id:context,command:body},maxRetries:body.operation==='snapshot'?2:0});if(!r.ok())throw new Error(await r.text());return r.json();};
 const xyz=async(f,label,values)=>{for(const [i,axis] of [...'XYZ'].entries())await f.getByLabel(`${label} ${axis}`,{exact:true}).fill(String(values[i]));};
 const readXYZ=async(f,label)=>Promise.all([...'XYZ'].map(axis=>f.getByLabel(`${label} ${axis}`,{exact:true}).inputValue().then(Number)));
 const menu=async(f,name,item)=>{await f.getByRole('button',{name,exact:true}).click();await f.getByText(item,{exact:true}).click();};
 try{
  await p.goto(`${base}/workspace/#/phys?embed=1&context=${context}`);
  if(process.env.VIS_RENDERER==='remote'){await p.getByRole('combobox',{name:'渲染方式'}).press('ArrowDown');await p.getByText('远程渲染',{exact:true}).click();}
  await p.getByRole('button',{name:'新建工作区'}).click();
  const f=p.frameLocator('iframe');await f.locator('.phys-tree').waitFor({timeout:30000});await expect(f.locator('.phys-viewport canvas').first()).toBeVisible();
  await p.screenshot({path:root+'/workbench-initial.png'});
  await f.getByLabel('着色物理量',{exact:true}).click();await f.getByRole('option',{name:'temperature (point)',exact:true}).click();
  await expect.poll(async()=>((await command({operation:'snapshot'})).spec.layers[0].field||{}).name).toBe('temperature');
  await f.getByRole('button',{name:'切面',exact:true}).click();await xyz(f,'原点',[0,0,0]);await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.pipeline.filter(n=>n.type==='slice').length).toBe(1);
  const priorSlice=(await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice');
  await xyz(f,'法向（无量纲）',[0,0,0]);await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect(f.locator('.phys-error')).toBeVisible();expect((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice')).toEqual(priorSlice);
  await f.locator('.phys-tree').getByText('基础显示',{exact:true}).click();await f.locator('.phys-tree').getByText('切面 1 *',{exact:true}).click();expect(await readXYZ(f,'法向（无量纲）')).toEqual([0,0,0]);
  await xyz(f,'法向（无量纲）',[1,0,0]);await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>((await command({operation:'snapshot'})).attachments.plane_widget||{}).visible).toBe(true);
  const handles=((await command({operation:'snapshot'})).attachments.plane_widget.handles||[]);
  for(const name of ['plane','axis_x','axis_y','axis_z','rotate_x','rotate_y','rotate_z'])expect(handles).toContain(name);
  const appliedSlice=(await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice');
  const appliedMesh=(await command({operation:'snapshot'})).datasets[appliedSlice.id];
  await f.getByRole('button',{name:'对齐Y方向',exact:true}).click();
  expect(await readXYZ(f,'法向（无量纲）')).toEqual([0,1,0]);
  expect(await readXYZ(f,'原点')).toEqual(appliedSlice.parameters.origin);
  await expect(f.locator('.phys-draft-badge')).toBeVisible();
  expect((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice').parameters.normal).toEqual(appliedSlice.parameters.normal);
  expect((await command({operation:'snapshot'})).datasets[appliedSlice.id]).toEqual(appliedMesh);
  const dragged=await command({operation:'plane_drag',handle:'axis_x',origin:appliedSlice.parameters.origin,normal:[0,1,0],start:[[0,0,0],[4,0,0]],end:[[1,0,0],[5,0,0]],input:appliedSlice.input,view:0});
  expect(dragged.origin[0]).not.toBe(appliedSlice.parameters.origin[0]);
  expect((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice').parameters.origin).toEqual(appliedSlice.parameters.origin);
  expect((await command({operation:'snapshot'})).datasets[appliedSlice.id]).toEqual(appliedMesh);
  const ox=dragged.origin[0],oy=dragged.origin[1],oz=dragged.origin[2];
  const rotated=await command({operation:'plane_drag',handle:'rotate_x',origin:dragged.origin,normal:[0,1,0],start:[[ox+1,oy+1,oz],[ox-1,oy+1,oz]],end:[[ox+1,oy,oz+1],[ox-1,oy,oz+1]],input:appliedSlice.input,view:0});
  if(Math.abs(rotated.normal[1]-1)<1e-5)throw new Error('rotate did not change normal');
  expect((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='slice').parameters.normal).toEqual(appliedSlice.parameters.normal);
  await xyz(f,'原点',dragged.origin);await xyz(f,'法向（无量纲）',rotated.normal);
  await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>{const n=(await command({operation:'snapshot'})).spec.pipeline.find(x=>x.type==='slice');return JSON.stringify([n.parameters.origin,n.parameters.normal]);}).toBe(JSON.stringify([dragged.origin,rotated.normal]));
  await f.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
  await f.getByRole('button',{name:'流线',exact:true}).click();
  await f.getByRole('button',{name:'起点类型 球体',exact:true}).click();
  await xyz(f,'球心',[0,0,0]);await f.getByLabel('半径',{exact:true}).fill('1');
  await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>Object.values((await command({operation:'snapshot'})).attachments.seeds||{}).some(Boolean)).toBe(true);
  await f.getByRole('button',{name:'起点类型 平面',exact:true}).click();
  await xyz(f,'平面原点',[0,0,0]);await xyz(f,'平面法向',[0,0,1]);
  await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='streamline').parameters||{}).seed_type).toBe('plane');
  await f.getByRole('button',{name:'起点类型 命名面',exact:true}).click();
  await f.getByLabel('命名面',{exact:true}).click();await f.getByRole('option',{name:/切面/}).click();
  await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>((await command({operation:'snapshot'})).spec.pipeline.find(n=>n.type==='streamline').parameters.seed_surface||{}).kind).toBe('object');
  const streamRow=f.locator('.phys-tree').getByText(/流线/);
  await streamRow.locator('xpath=ancestor::div[contains(@class,"phys-node")]').getByRole('button').first().click();
  await expect.poll(async()=>Object.values((await command({operation:'snapshot'})).attachments.seeds||{}).some(Boolean)).toBe(false);
  await f.locator('.phys-tree').getByText('切面 1',{exact:true}).click();
  await f.getByRole('button',{name:'上下分割',exact:true}).click();await expect.poll(async()=>(await command({operation:'snapshot'})).spec.views.length).toBe(2);
  await f.getByRole('button',{name:'左右分割',exact:true}).click();await expect.poll(async()=>(await command({operation:'snapshot'})).spec.views.length).toBe(3);
  // 真实鼠标操作必须回写所属视图相机，不能只验证工具栏按钮。
  await f.getByText('RenderView3',{exact:true}).click();
  const cameras=(await command({operation:'snapshot'})).spec.views.map(v=>v.camera);
  const box=await f.locator('.phys-viewport').boundingBox();
  await p.mouse.move(box.x+box.width*.75,box.y+box.height*.75);await p.mouse.down();await p.mouse.move(box.x+box.width*.82,box.y+box.height*.8,{steps:12});await p.mouse.up();
  if(process.env.VIS_DEBUG)console.log('local cameras', JSON.stringify(await f.locator('.phys-viewport').evaluate(el=>[...el.querySelectorAll('span')].map(s=>s.__physTracker).filter(Boolean).map(t=>({pointer:window.__visPointer,ids:t.viewIds,renderers:t.view.renderWindow.getRenderers().map(r=>({layer:r.getLayer(),viewport:r.getViewport(),camera:r.getActiveCamera().getPosition()}))})))));
  await expect.poll(async()=>JSON.stringify((await command({operation:'snapshot'})).spec.views[2].camera),{timeout:10000}).not.toBe(JSON.stringify(cameras[2]));
  expect((await command({operation:'snapshot'})).spec.views[0].camera).toEqual(cameras[0]);
  for(const mode of ['平移','缩放']){
    await f.getByRole('button',{name:mode,exact:true}).click();
    const before=(await command({operation:'snapshot'})).spec.views[2].camera;
    await p.mouse.move(box.x+box.width*.7,box.y+box.height*.7);await p.mouse.down();await p.mouse.move(box.x+box.width*.73,box.y+box.height*.75,{steps:8});await p.mouse.up();
    await expect.poll(async()=>JSON.stringify((await command({operation:'snapshot'})).spec.views[2].camera)).not.toBe(JSON.stringify(before));
  }
  await f.getByText('相机联动',{exact:true}).click();await f.getByRole('button',{name:'顶',exact:true}).click();
  await expect.poll(async()=>{const views=(await command({operation:'snapshot'})).spec.views;return JSON.stringify(views[0].camera)===JSON.stringify(views[2].camera)}).toBe(true);
  await f.getByText('相机联动',{exact:true}).click();
  await f.locator('.phys-tree').getByText('基础显示',{exact:true}).click();await f.getByRole('button',{name:'Probe',exact:true}).click();await xyz(f,'空间坐标',[1,1,1]);await f.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>Object.values((await command({operation:'snapshot'})).probes).some(r=>r.valid)).toBe(true);
  await f.getByRole('button',{name:'在模型上拾取位置',exact:true}).click();const pickBox=await f.locator('.phys-viewport').boundingBox();await p.mouse.click(pickBox.x+pickBox.width*.75,pickBox.y+pickBox.height*.75);
  await expect.poll(async()=>Math.max(...(await readXYZ(f,'空间坐标')).map(Math.abs))).toBeCloseTo(4,3);
  const picked=(await readXYZ(f,'空间坐标'));expect(Math.max(...picked.map(Math.abs))).toBeCloseTo(4,3);
  await xyz(f,'空间坐标',[1,1,1]);await f.getByRole('button',{name:'应用',exact:true}).click();
  await f.getByRole('button',{name:'下一帧',exact:true}).click();await expect.poll(async()=>(await command({operation:'snapshot'})).spec.time.value).toBe(.1);
  await menu(f,'文件','保存配置');await p.getByRole('dialog').waitFor({timeout:10000});await p.getByLabel('可视化名称').fill('对象工作台浏览器 '+Date.now());
  const savedResponse=p.waitForResponse(r=>r.url().endsWith('/api/visualizations')&&r.request().method()==='POST');await p.getByRole('button',{name:'确 定',exact:true}).click();const saved=await(await savedResponse).json();if(!saved.visualization_id)throw new Error(JSON.stringify(saved));
  await expect(p.getByRole('dialog')).toHaveCount(0);await p.waitForTimeout(1000);await p.screenshot({path:root+'/workbench-objects.png'});
  await f.getByRole('button',{name:'动画',exact:true}).click();await p.getByRole('dialog').waitFor();await p.getByRole('button',{name:/生\s*成/}).click();
  await expect(p.getByRole('link',{name:'animation.mp4'})).toBeVisible({timeout:60000});const link=p.getByRole('link',{name:'animation.mp4'});const file=await p.request.get(new URL(await link.getAttribute('href'),base).href);fs.writeFileSync(root+'/animation.mp4',await file.body());
  await p.reload();await p.getByRole('combobox',{name:'已保存可视化'}).fill(saved.name);await p.getByText(saved.name+' · r'+saved.revision,{exact:true}).click();await f.locator('.phys-tree').getByText('Probe 1',{exact:true}).waitFor({timeout:30000});
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.views.length).toBe(3);
  for(const width of [1440,1920]){await p.setViewportSize({width,height:1080});await p.waitForTimeout(500);await p.screenshot({path:root+`/workbench-${width}.png`});expect(await f.locator('.phys-workbench').evaluate(el=>el.scrollWidth<=el.clientWidth)).toBe(true);}
  await menu(f,'导出','录制实际操作');await expect(p.getByText('正在录制实际操作',{exact:true})).toBeVisible();
  await f.getByRole('button',{name:'正',exact:true}).click();await p.waitForTimeout(700);await f.getByRole('button',{name:'右',exact:true}).click();await p.waitForTimeout(700);await p.getByRole('button',{name:'停止录制',exact:true}).click();
  await expect(p.getByRole('link',{name:'recording.webm'})).toBeVisible({timeout:20000});const recording=await p.request.get(new URL(await p.getByRole('link',{name:'recording.webm'}).getAttribute('href'),base).href);fs.writeFileSync(root+'/recording.webm',await recording.body());
  if(process.env.VIS_CHECK_UPLOAD==='1'){
    const before=(await command({operation:'snapshot'})).spec;
    await menu(f,'文件','导入结果');await p.getByRole('dialog').waitFor();await p.locator('input[type=file]').setInputFiles(root+'/frame0.vti');
    await expect(p.getByRole('dialog').getByRole('button',{name:'确 定',exact:true})).toBeEnabled({timeout:30000});await p.getByRole('dialog').getByRole('button',{name:'确 定',exact:true}).click();
    await expect(p.getByRole('dialog')).toHaveCount(0,{timeout:30000});
    await expect.poll(async()=>(await command({operation:'snapshot'})).spec.sources.length).toBe(before.sources.length+1);
    expect((await command({operation:'snapshot'})).spec.views).toEqual(before.views);
  }
  await p.setViewportSize({width:900,height:900});await expect(f.getByRole('button',{name:'更多分析',exact:true})).toBeVisible();await expect(f.getByRole('button',{name:'切面',exact:true})).toHaveCount(0);await p.screenshot({path:root+'/workbench-900.png'});if(process.env.VIS_DEBUG)console.log('afterresize',JSON.stringify(await f.locator('.phys-viewport').evaluate(el=>[...el.querySelectorAll('span')].map(s=>s.__physTracker).filter(Boolean).map(t=>t.view.renderWindow.getRenderers().map(r=>({layer:r.getLayer(),viewport:r.getViewport(),pos:r.getActiveCamera().getPosition(),up:r.getActiveCamera().getViewUp()}))))),JSON.stringify((await command({operation:'snapshot'})).spec.views));
  if(process.env.VIS_RENDERER !== 'remote') {
    await expect.poll(() => f.locator('.phys-viewport').evaluate(el => {
      const trackers = [...el.querySelectorAll('span')].map(s => s.__physTracker).filter(Boolean);
      return trackers.length > 0 && trackers.every(t => t.cameras.length > 0 && t.cameras.every(entry => {
        const renderer = t.view.renderWindow.getRenderers().find(r => r.getLayer() === entry.layer && r.getViewport().every((v, i) => Math.abs(v - entry.viewport[i]) < 1e-8));
        return renderer && renderer.getActiveCamera().getPosition().every((v, i) => Math.abs(v - entry.camera.position[i]) < 1e-6);
      }));
    })).toBe(true);
  }
  if(errors.length)throw new Error(errors.join('\n'));
  fs.writeFileSync(root+'/objects-browser-results.json',JSON.stringify({status:'passed',renderer:process.env.VIS_RENDERER||'local',asset:saved.visualization_id,checks:['object tree','scalar coloring','slice Apply','invalid Apply rollback','draft switching','plane widget preview','streamline seeds','three views','rotate/pan/zoom','camera isolation/linking','spatial probe','time step','save/reopen','1440/1920 layout','MP4 download','WebM recording'],errors},null,2));
  console.log('PASS objects browser');
 }catch(e){await p.screenshot({path:root+'/objects-failure.png'});console.log('Browser errors',errors);for(const f of p.frames()){console.log((await f.locator('body').innerText()).slice(-1800));console.log(await f.evaluate(()=>{const all=[];const walk=c=>{if(!c)return;if(c.$options?.name==='phys-camera-tracker'||c.viewIds)all.push({name:c.$options.name,ids:c.viewIds,renderers:c.view?.renderWindow?.getRenderers().map(r=>({layer:r.getLayer(),bounds:r.getViewport(),pos:r.getActiveCamera().getPosition()}))});for(const child of c.$children||[])walk(child)};walk(document.querySelector('#app')?.__vue__);return all}));}throw e;}
 finally{for(const id of ids)await p.request.delete(`${base}/api/phys/sessions/${id}?context_id=${context}`);await b.close();}
})().catch(e=>{console.error(e);process.exit(1)});
