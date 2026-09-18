/** 实际 Dojo Web → Vis → Trame 双层 iframe；不替换 API、页面或 VTK 场景。 */
import {test, expect, type Frame, type Page} from '@playwright/test';
import {writeFileSync} from 'node:fs';

const project=process.env.DOJO_TRAME_PROJECT;
const task=process.env.DOJO_TRAME_TASK;
const sample=process.env.DOJO_TRAME_SAMPLE||'1cff510c0630c3cc673ddeabdcc8c6e';
const file=process.env.DOJO_TRAME_FILE||'hexvelo_smpl.vtk';
const repeats=Number(process.env.DOJO_TRAME_REPEATS||30);
const route=`/projects/${project}/tasks/${task}`;

async function observe(page:Page){
 const ui=page.frameLocator('iframe[title="独立可视化应用"]').frameLocator('iframe[title="三维物理场 Trame 工作台"]');
 await expect(ui.locator('.phys-tree').getByText('基础显示',{exact:true})).toBeVisible({timeout:90000});
 const frame=page.frames().find(f=>f.url().includes('/api/phys/view/'))!;
 await frame.waitForFunction(()=>[...document.querySelectorAll('.phys-viewport span')].some((s:any)=>s.__physTracker?.view?.renderWindow));
 await frame.evaluate(()=>{
  const tracker:any=[...document.querySelectorAll('.phys-viewport span')].map((s:any)=>s.__physTracker).find(Boolean);
  (window as any).__responseProbe={tracker,loaded:0};
  window.addEventListener('phys-scene-ready',()=>{(window as any).__responseProbe.loaded++;});
 });
 return {ui,frame};
}
async function actors(frame:Frame){
 return frame.evaluate(()=>{
  const rw=(window as any).__responseProbe.tracker.view.renderWindow;
  return rw.getRenderers().filter((r:any)=>r.getLayer()===0).map((r:any)=>({
   camera:Array.from(r.getActiveCamera().getPosition()),
   actors:r.getActors().map((a:any)=>({visible:Boolean(a.getVisibility()),scalar:Boolean(a.getMapper()?.getScalarVisibility()),points:a.getMapper()?.getInputData()?.getNumberOfPoints()||0})),
  }));
 });
}
async function waitActor(frame:Frame, predicate:{points:number;visible?:boolean;scalar?:boolean;view?:number}){
 await frame.waitForFunction(p=>{
  const rw=(window as any).__responseProbe.tracker.view.renderWindow;
  const renderer=rw.getRenderers().filter((r:any)=>r.getLayer()===0)[p.view||0];
  if(!renderer)return false;
  // 首次加载隐藏对象时 Trame 不传它的几何；同时在重开用例核对眼睛与可见子对象。
  if(p.visible===false)return !renderer.getActors().some((a:any)=>a.getMapper()?.getInputData()?.getNumberOfPoints()===p.points&&a.getVisibility());
  return renderer.getActors().some((a:any)=>{
   const m=a.getMapper();return m?.getInputData()?.getNumberOfPoints()===p.points &&
   (p.visible===undefined||Boolean(a.getVisibility())===p.visible)&&
   (p.scalar===undefined||Boolean(m.getScalarVisibility())===p.scalar);
  });
 },predicate,{timeout:5000});
 // 场景完成后再跨两个绘制帧；仍不把这个计时称为 GPU 完成时间。
 await frame.evaluate(()=>new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r()))));
}

test('真实原始处理 iframe：字段、独立显隐、切面草稿与应用响应',async({page},info)=>{
 test.skip(!project||!task,'通过 DOJO_TRAME_PROJECT/TASK 显式选择真实任务');
 test.setTimeout(300000);
 page.setDefaultTimeout(12000);
 await page.setViewportSize({width:1920,height:1080});
 const errors:string[]=[],rows:{kind:string;ms:number}[]=[],devUpdates:any[]=[];
 page.on('websocket',ws=>ws.on('framereceived',({payload})=>{
  try{const m=JSON.parse(payload.toString());if(['update','full-reload'].includes(m.type))devUpdates.push({at:Date.now(),type:m.type,paths:m.updates?.map((u:any)=>u.path)});}catch{/* VTK 二进制消息不属于开发服务器更新。 */}
 }));
 page.on('pageerror',e=>errors.push(e.message));
 try{
  await page.goto(route+'/rawprep');
  await page.getByRole('button',{name:'param0',exact:true}).click();
  await page.getByRole('button',{name:sample,exact:true}).click();
  await page.getByRole('button',{name:'预览 '+file,exact:true}).click();
  const {ui,frame}=await observe(page);
  const basePoints=(await actors(frame))[0].actors.find((a:any)=>a.points>100)!.points;
  const measure=async(kind:string,action:()=>Promise<any>,done:()=>Promise<any>)=>{
   const start=Date.now();await action();await done();rows.push({kind,ms:Date.now()-start});
   await expect(ui.locator('.phys-error')).toBeHidden();
  };
  for(let i=0;i<repeats;i++){
   const colored=i%2===0;
   await ui.getByLabel('着色物理量',{exact:true}).click();
   await measure('field',()=>ui.getByRole('option',{name:colored?'point_vectors (point)':'纯色',exact:true}).click(),()=>waitActor(frame,{points:basePoints,scalar:colored}));
  }
  for(let i=0;i<repeats;i++){
   const visible=i%2===1;
   await measure('visibility',()=>ui.getByRole('button',{name:(visible?'显示':'隐藏')+' 基础显示',exact:true}).click(),()=>waitActor(frame,{points:basePoints,visible}));
  }
  await page.screenshot({path:info.outputPath('01-base.png')});
  for(let i=0;i<repeats;i++){
   const initial=(await actors(frame))[0].actors.length;
   await measure('slice-draft',()=>ui.getByRole('button',{name:'切面',exact:true}).click(),async()=>{
    await expect(ui.getByLabel('原点 X',{exact:true})).toBeVisible();
    await frame.waitForFunction(n=>(window as any).__responseProbe.tracker.view.renderWindow.getRenderers().filter((r:any)=>r.getLayer()===0)[0].getActors().length>n,initial,{timeout:5000});
    await frame.evaluate(()=>new Promise<void>(r=>requestAnimationFrame(()=>requestAnimationFrame(()=>r()))));
   });
   const draftName=await ui.locator('.phys-object-title').innerText();
   if(i===0){
    await ui.getByRole('button',{name:'切面',exact:true}).click();
    await expect(ui.locator('.phys-draft-badge').filter({visible:true})).toHaveCount(1);
    await page.screenshot({path:info.outputPath('02-draft-handles.png')});
   }
   if(i===repeats-1)break;
   await ui.getByRole('button',{name:'删除 '+draftName+' *',exact:true}).click();
   await ui.getByRole('button',{name:'确认删除',exact:true}).click();
   await expect(ui.locator('.phys-tree').getByText(draftName+' *',{exact:true})).toHaveCount(0);
   await ui.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
   await expect.poll(async()=>(await actors(frame))[0].actors.length).toBe(initial);
  }
  const sliceName=await ui.locator('.phys-object-title').innerText();
  // 在双层 iframe 里真实拖动手柄，核对最终坐标回填；不直接调用服务器命令。
  const handle=await frame.evaluate(()=>{
   const t=(window as any).__responseProbe.tracker,w=t.planeWidget;
   const renderer=t.view.renderWindow.getRenderers().find((r:any)=>r.getLayer()===0);
   const view=t.view.renderWindow.getViews()[0],size=view.getSize();
   const length=Math.max(w.bounds[1]-w.bounds[0],w.bounds[3]-w.bounds[2],w.bounds[5]-w.bounds[4])*.55;
   for(let axis=0;axis<3;axis++){
    const point=[...w.origin];point[axis]+=length*.3;
    const d=view.worldToDisplay(...point,renderer),x=d[0]/size[0],y=d[1]/size[1];
    if(x>.1&&x<.9&&y>.1&&y<.9&&(window as any).physHitHandle(w,t.worldRay(x,y)))return {x,y};
   }
   return null;
  });
  expect(handle).not.toBeNull();
  const viewport=await ui.locator('.phys-viewport').boundingBox();
  const oldOrigin=await ui.getByLabel('原点 X',{exact:true}).inputValue();
  await page.mouse.move(viewport!.x+handle!.x*viewport!.width,viewport!.y+(1-handle!.y)*viewport!.height);
  await page.mouse.down();
  await page.mouse.move(viewport!.x+handle!.x*viewport!.width+24,viewport!.y+(1-handle!.y)*viewport!.height+18,{steps:10});
  await page.mouse.up();
  await expect.poll(()=>ui.getByLabel('原点 X',{exact:true}).inputValue()).not.toBe(oldOrigin);
  for(const [index,axis] of ['X','Y','Z'].entries()){
   await ui.getByLabel('原点 '+axis,{exact:true}).fill('0');await ui.getByLabel('原点 '+axis,{exact:true}).press('Tab');
   await frame.waitForFunction(i=>(window as any).__responseProbe.tracker.planeWidget.origin[i]===0,index);
  }
  await measure('slice-apply',()=>ui.getByRole('button',{name:'应用',exact:true}).click(),async()=>{
   await expect(ui.getByRole('button',{name:'隐藏 '+sliceName,exact:true})).toBeEnabled();
   await expect.poll(async()=>(await actors(frame))[0].actors.filter((a:any)=>a.points>100&&a.points!==basePoints).length).toBe(1);
  });
  const slicePoints=(await actors(frame))[0].actors.find((a:any)=>a.points>100&&a.points!==basePoints)!.points;
  const initialSlice=await actors(frame);
  for(let i=1;i<repeats;i++){
   await ui.getByLabel('原点 X',{exact:true}).fill(i%2?'0.01':'0');await ui.getByLabel('原点 X',{exact:true}).press('Tab');
   const seq=await frame.evaluate(()=>(window as any).__responseProbe.loaded);
   await measure('slice-apply',()=>ui.getByRole('button',{name:'应用',exact:true}).click(),async()=>{
    await frame.waitForFunction(n=>(window as any).__responseProbe.loaded>n,seq,{timeout:5000});
    await expect(ui.locator('.phys-draft-badge').filter({visible:true})).toHaveCount(0);
   });
  }
  await ui.getByLabel('原点 X',{exact:true}).fill('0');await ui.getByLabel('原点 X',{exact:true}).press('Tab');
  await ui.getByRole('button',{name:'应用',exact:true}).click();
  await expect(ui.locator('.phys-draft-badge').filter({visible:true})).toHaveCount(0);
  writeFileSync(info.outputPath('slice-debug.json'),JSON.stringify({initialSlice,finalSlice:await actors(frame),widget:await frame.evaluate(()=>(window as any).__responseProbe.tracker.planeWidget)},null,2));
  await waitActor(frame,{points:slicePoints,visible:true});
  const usable=await actors(frame);
  await ui.getByLabel('法向（无量纲） X',{exact:true}).fill('0');await ui.getByLabel('法向（无量纲） X',{exact:true}).press('Tab');
  await ui.getByRole('button',{name:'应用',exact:true}).click();
  await expect(ui.locator('.phys-error')).toContainText(/normal|法向/);
  expect(await actors(frame)).toEqual(usable);
  await ui.getByLabel('法向（无量纲） X',{exact:true}).fill('1');await ui.getByLabel('法向（无量纲） X',{exact:true}).press('Tab');
  await ui.getByRole('button',{name:'应用',exact:true}).click();
  await expect(ui.locator('.phys-error')).toBeHidden();
  await ui.getByRole('button',{name:'隐藏 基础显示',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:false});
  await waitActor(frame,{points:slicePoints,visible:true});
  await page.screenshot({path:info.outputPath('03-parent-hidden-child-visible.png')});
  await ui.getByRole('button',{name:'隐藏 '+sliceName,exact:true}).click();
  await waitActor(frame,{points:slicePoints,visible:false});
  await page.screenshot({path:info.outputPath('04-both-hidden.png')});
  await ui.getByRole('button',{name:'显示 基础显示',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:true});
  await waitActor(frame,{points:slicePoints,visible:false});
  await ui.getByRole('button',{name:'显示 '+sliceName,exact:true}).click();
  await waitActor(frame,{points:slicePoints,visible:true});
  // 鼠标普通经过不得触发额外场景同步。
  await ui.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
  const box=await ui.locator('.phys-viewport').boundingBox();
  const before=await frame.evaluate(()=>(window as any).__responseProbe.loaded);
  for(let i=0;i<60;i++)await page.mouse.move(box!.x+box!.width*(.2+i/150),box!.y+box!.height*.7);
  expect(await frame.evaluate(()=>(window as any).__responseProbe.loaded)-before).toBeLessThanOrEqual(1);
  await page.setViewportSize({width:1440,height:1000});
  await page.screenshot({path:info.outputPath('05-web-1440.png')});
  expect(errors).toEqual([]);
  const summary=Object.fromEntries(['field','visibility','slice-draft','slice-apply'].map(kind=>{
   const values=rows.filter(r=>r.kind===kind).map(r=>r.ms),sorted=[...values].sort((a,b)=>a-b);
   return [kind,{count:values.length,first:values[0],p50:sorted[Math.ceil(sorted.length*.5)-1],p95:sorted[Math.ceil(sorted.length*.95)-1],max:sorted.at(-1)}];
  }));
  writeFileSync(info.outputPath('timings.json'),JSON.stringify({route,basePoints,slicePoints,rows,summary,errors,endpoint:'browser vtk.js scene plus two animation frames'},null,2));
  for(const kind of ['field','visibility','slice-draft'])expect((summary[kind] as any).p95).toBeLessThan(1000);
 }finally{
  writeFileSync(info.outputPath('partial-timings.json'),JSON.stringify({rows,errors,devUpdates},null,2));
  const lastFrame=page.frames().find(f=>f.url().includes('/api/phys/view/'));
  if(lastFrame){
   writeFileSync(info.outputPath('last-ui.json'),JSON.stringify(await lastFrame.evaluate(()=>{
    const t=(window as any).__responseProbe?.tracker;
    return {widget:t?.planeWidget,rootKeys:Object.keys(t?.$root?.$data||{}),inputs:[...document.querySelectorAll('input')].map(e=>({label:e.getAttribute('aria-label'),value:e.value})),text:document.querySelector('.phys-error')?.textContent};
   }).catch(()=>null),null,2));
   await page.screenshot({path:info.outputPath('last-ui.png')}).catch(()=>{});
  }
  await page.getByRole('button',{name:'Close',exact:true}).click().catch(()=>{});
 }
});

test('真实后处理 iframe：导入、多视图、十次 Tab 切换与保存重开',async({page},info)=>{
 test.skip(!project||!task,'通过 DOJO_TRAME_PROJECT/TASK 显式选择真实任务');
 test.setTimeout(180000);page.setDefaultTimeout(15000);
 const opened:string[]=[],closed:string[]=[],errors:string[]=[];
 let sourceId='';
 page.on('pageerror',e=>errors.push(e.message));
 page.on('response',async r=>{
  if(!r.ok())return;
  if(r.url().endsWith('/assets')&&r.request().method()==='POST')sourceId=(await r.json()).asset_id;
  if(r.url().endsWith('/visualizations/sessions')&&r.request().method()==='POST')opened.push((await r.json()).session_id);
  if(r.url().includes('/visualizations/sessions/')&&r.request().method()==='DELETE')closed.push(r.url().split('/').at(-1)!);
 });
 try{
  await page.setViewportSize({width:1920,height:1080});
  await page.goto(route+'/rawprep');
  await page.getByRole('button',{name:'param0',exact:true}).click();await page.getByRole('button',{name:sample,exact:true}).click();
  await page.getByRole('button',{name:'预览 '+file,exact:true}).click();await observe(page);
  expect(sourceId).not.toBe('');
  await page.getByRole('button',{name:'Close',exact:true}).click();
  await expect.poll(()=>closed.includes(opened[0])).toBe(true);
  await page.goto(route+'/post');
  await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();
  const outer=page.frameLocator('iframe[title="独立可视化应用"]');
  const ui=outer.frameLocator('iframe[title="三维物理场 Trame 工作台"]');
  await expect(ui.getByRole('button',{name:'文件',exact:true})).toBeVisible({timeout:90000});
  const id=await page.locator('.phys-host').getAttribute('data-session-id');
  await ui.getByRole('button',{name:'文件',exact:true}).click();await ui.getByText('导入结果',{exact:true}).click();
  await outer.getByRole('combobox',{name:'结果资产',exact:true}).fill(sourceId);
  await outer.locator('.ant-select-item-option').filter({hasText:sourceId}).click();
  await outer.getByRole('dialog').getByRole('button',{name:'确 定',exact:true}).click();
  const {frame}=await observe(page);
  expect(await page.locator('.phys-host').getAttribute('data-session-id')).toBe(id);
  await ui.getByRole('button',{name:'适窗',exact:true}).click();
  await expect.poll(async()=>(await actors(frame))[0].camera).not.toEqual([1,1,1]);
  const basePoints=(await actors(frame))[0].actors.find((a:any)=>a.points>100)!.points;
  await ui.getByRole('button',{name:'切面',exact:true}).click();
  await expect(ui.getByLabel('原点 X',{exact:true})).toBeVisible();
  await ui.getByRole('button',{name:'应用',exact:true}).click();
  await expect(ui.getByRole('button',{name:'隐藏 切面 1',exact:true})).toBeEnabled();
  const childPoints=(await actors(frame))[0].actors.find((a:any)=>a.points>100&&a.points!==basePoints)!.points;
  await ui.getByRole('button',{name:'隐藏 基础显示',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:false});await waitActor(frame,{points:childPoints,visible:true});
  // 新窗口复制活动视图，随后各自修改字段和显隐。
  await ui.locator('[title="新建窗口"]').click();
  await expect.poll(async()=>(await actors(frame)).length).toBe(2);
  await ui.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
  await ui.getByRole('button',{name:'显示 基础显示',exact:true}).click();
  await ui.getByLabel('着色物理量',{exact:true}).click();await ui.getByRole('option',{name:'point_vectors (point)',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:true,scalar:true,view:1});
  await waitActor(frame,{points:basePoints,visible:false,scalar:false,view:0});
  const before=await actors(frame);
  for(let i=0;i<10;i++){
   await page.getByRole('tab',{name:'结果文件',exact:true}).click();
   await page.getByRole('tab',{name:'三维物理场可视化',exact:true}).click();
  }
  expect(await page.locator('.phys-host').getAttribute('data-session-id')).toBe(id);
  expect(page.frames()).toContain(frame);expect(await actors(frame)).toEqual(before);
  // 返回后继续在 iframe 点击，不能只证明它仍挂载。
  await ui.getByRole('button',{name:'隐藏 基础显示',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:false,view:1});
  await ui.getByRole('button',{name:'显示 基础显示',exact:true}).click();
  await waitActor(frame,{points:basePoints,visible:true,view:1});
  await page.screenshot({path:info.outputPath('post-two-views-1920.png')});
  await ui.getByRole('button',{name:'文件',exact:true}).click();await ui.getByText('保存配置',{exact:true}).click();
  const name='响应复测-独立显隐-'+Date.now();
  await outer.getByRole('textbox',{name:'可视化名称',exact:true}).fill(name);
  await outer.getByRole('dialog').filter({visible:true}).getByRole('button',{name:'确 定',exact:true}).click();
  await expect(outer.getByRole('textbox',{name:'可视化名称',exact:true})).toBeHidden();
  await ui.getByRole('button',{name:'文件',exact:true}).click();await ui.getByText('打开已保存配置',{exact:true}).click();
  await outer.getByRole('combobox',{name:'打开配置资产',exact:true}).click();await outer.getByText(name+' · r1',{exact:true}).click();
  await expect.poll(()=>page.locator('.phys-host').getAttribute('data-session-id')).not.toBe(id);
  const restored=await observe(page);
  await expect(restored.ui.getByRole('button',{name:'显示 基础显示',exact:true})).toBeEnabled();
  await waitActor(restored.frame,{points:basePoints,visible:false,view:0});
  await waitActor(restored.frame,{points:childPoints,visible:true,view:0});
  await waitActor(restored.frame,{points:basePoints,visible:true,scalar:true,view:1});
  await page.setViewportSize({width:1440,height:1000});
  await expect.poll(async()=>restored.ui.locator('.phys-viewport').evaluate(e=>e.clientHeight)).toBeGreaterThan(300);
  await page.screenshot({path:info.outputPath('post-restored-1440.png')});
  writeFileSync(info.outputPath('post-evidence.json'),JSON.stringify({route,name,id,reopened:await page.locator('.phys-host').getAttribute('data-session-id'),before,restored:await actors(restored.frame),errors},null,2));
  expect(errors).toEqual([]);
  await page.getByRole('menuitem',{name:'项目管理',exact:true}).click();
  await expect.poll(()=>closed.length).toBe(opened.length);
 }finally{
  for(const id of opened)await page.request.delete(`/api/v1/projects/${project}/tasks/${task}/visualizations/sessions/${id}`);
 }
});

test('真实宿主八项修复：子对象着色、辅助显隐与空场景删除',async({page},info)=>{
 test.skip(!project||!task,'需要指定隔离项目与真实数据任务');
 test.setTimeout(180000);
 await page.setViewportSize({width:1672,height:941});
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(route+'/rawprep');
 await page.getByRole('button',{name:process.env.DOJO_TRAME_PARAM||'param0',exact:true}).click();
 await page.getByRole('button',{name:sample,exact:true}).click();
 await page.getByRole('button',{name:'预览 '+file,exact:true}).click();
 const {ui,frame}=await observe(page);
 await ui.locator('.phys-viewport').screenshot({path:info.outputPath('host-base-plain.png')});
 await ui.getByLabel('着色变量',{exact:true}).click();
 await ui.getByRole('option').filter({hasText:'(point)'}).first().click();
 await ui.getByRole('button',{name:'应用',exact:true}).click();
 await frame.waitForFunction(()=>{
  const rw=(window as any).__responseProbe.tracker.view.renderWindow;
  return rw.getRenderers().some((r:any)=>r.getActors().some((a:any)=>a.getMapper()?.getScalarVisibility()&&a.getMapper()?.getInputData()?.getPointData().getArrayByName('__vis_scalar')));
 });
 await ui.locator('.phys-viewport').screenshot({path:info.outputPath('host-base-colored.png')});
 await ui.getByRole('button',{name:'切面',exact:true}).click();
 await ui.getByLabel('着色变量',{exact:true}).click();
 await ui.getByRole('option').filter({hasText:'(point)'}).first().click();
 await ui.getByRole('button',{name:'应用',exact:true}).click();
 await expect(ui.getByRole('button',{name:'隐藏 切面 1',exact:true})).toBeEnabled();
 await ui.getByText('显示辅助平面',{exact:true}).click();
 await frame.waitForFunction(()=>!(window as any).__responseProbe.tracker.planeWidget?.visible);
 await ui.getByText('显示辅助平面',{exact:true}).click();
 await frame.waitForFunction(()=>(window as any).__responseProbe.tracker.planeWidget?.visible);
 for(const [width,height] of [[1440,900],[1672,941],[1920,1080]]){
  await page.setViewportSize({width,height});
  await page.waitForTimeout(500);
  await expect(ui.getByRole('button',{name:'应用',exact:true})).toBeVisible();
  await page.screenshot({path:info.outputPath(`host-plane-${width}.png`)});
 }
 await page.getByRole('button',{name:/放\s*大/}).click();
 await expect(ui.getByRole('button',{name:'应用',exact:true})).toBeVisible();
 await page.screenshot({path:info.outputPath('host-maximized.png')});
 // 等高线自动/自定义模式与 Probe 真实拾取均在同一宿主中操作。
 await ui.getByRole('button',{name:'等高线',exact:true}).click();
 await expect(ui.getByLabel('等值级别数',{exact:true})).toHaveValue('10');
 await ui.getByRole('button',{name:'生成方式 自定义等值',exact:true}).click();
 await expect(ui.getByLabel('等值列表',{exact:true})).toBeVisible();
 await expect(ui.getByLabel('等值级别数',{exact:true})).toBeHidden();
 await ui.getByRole('button',{name:'取消修改',exact:true}).click();
 await ui.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
 await ui.getByRole('button',{name:'Probe',exact:true}).click();
 const coordinates=()=>Promise.all(['X','Y','Z'].map(axis=>ui.getByLabel('空间坐标 '+axis,{exact:true}).inputValue()));
 const initial=await coordinates();
 await ui.getByRole('button',{name:'在模型上拾取位置',exact:true}).click();
 const viewport=await ui.locator('.phys-viewport').boundingBox();
 await page.mouse.click(viewport!.x+viewport!.width*.5,viewport!.y+viewport!.height*.5);
 await expect.poll(coordinates).not.toEqual(initial);
 await page.screenshot({path:info.outputPath('host-probe-candidate.png')});
 await ui.getByRole('button',{name:'取消修改',exact:true}).click();
 await ui.locator('.phys-tree').getByText('切面 1',{exact:true}).click();
 await ui.getByRole('button',{name:'隐藏 基础显示',exact:true}).click();
 await ui.getByText('显示辅助平面',{exact:true}).click();
 const before=await actors(frame);
 await ui.getByRole('button',{name:'删除 切面 1',exact:true}).click();
 await ui.getByRole('button',{name:'确认删除',exact:true}).click();
 await expect(ui.locator('.phys-tree').getByText('切面 1',{exact:true})).toHaveCount(0);
 await expect(ui.getByRole('button',{name:'显示 基础显示',exact:true})).toBeVisible();
 await expect(ui.getByRole('button',{name:'确认删除',exact:true})).toBeHidden();
 await expect.poll(async()=>(await actors(frame)).length).toBe(1);
 expect((await actors(frame))[0].camera).toEqual(before[0].camera);
 await expect.poll(async()=>(await actors(frame))[0].actors.filter((a:any)=>a.visible&&a.points>0).length).toBe(0);
 await page.screenshot({path:info.outputPath('host-deleted-background.png')});
 expect(errors).toEqual([]);
 await page.getByRole('button',{name:'Close',exact:true}).click();
});
