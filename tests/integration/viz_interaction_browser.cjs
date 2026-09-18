/** 八项交互修复的真实浏览器验收；沿现有 Vis 页面进入 Trame，保留截图与失败证据。 */
const {chromium,expect}=require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs=require('node:fs');
const root=process.env.VIS_EVIDENCE_ROOT,context=process.env.VIS_CONTEXT;
const base=process.env.VIS_BROWSER_URL||'http://127.0.0.1:7999';
if(!root||!context)throw Error('需要独立证据目录和测试上下文');
(async()=>{
 const browser=await chromium.launch();const page=await browser.newPage({viewport:{width:1672,height:941}});page.setDefaultTimeout(30000);
 const errors=[],sessions=[];page.on('pageerror',e=>errors.push(e.message));
 page.on('response',async r=>{if(r.url().endsWith('/api/phys/sessions')&&r.request().method()==='POST'&&r.ok())sessions.push((await r.json()).session_id)});
 const command=async body=>{const r=await page.request.post(`${base}/api/phys/sessions/${sessions.at(-1)}/commands`,{data:{context_id:context,command:body}});expect(r.ok(),await r.text()).toBe(true);return r.json()};
 try{
  await page.goto(`${base}/workspace/#/phys?embed=1&context=${context}`);
  if(process.env.VIS_RENDERER==='remote'){await page.getByRole('combobox',{name:'渲染方式'}).press('ArrowDown');await page.getByText('远程渲染',{exact:true}).click();}
  await page.getByRole('button',{name:'新建工作区',exact:true}).click();
  const frame=page.frameLocator('iframe');await frame.locator('.phys-tree').waitFor();
  // 基础资产属性应用与顶部即时切换分别验证；先留下纯色基线。
  await page.waitForTimeout(700);
  await frame.locator('.phys-viewport').screenshot({path:`${root}/base-plain.png`});
  const baseBefore=await command({operation:'snapshot'});
  await frame.getByLabel('着色变量',{exact:true}).click();
  await frame.getByRole('option').filter({hasText:'(point)'}).first().click();
  expect((await command({operation:'snapshot'})).spec.layers).toEqual(baseBefore.spec.layers);
  await frame.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>Boolean((await command({operation:'snapshot'})).spec.layers[0].field)).toBe(true);
  await page.waitForTimeout(700);
  await frame.locator('.phys-viewport').screenshot({path:`${root}/base-colored.png`});
  if(process.env.VIS_RENDERER!=='remote'){
   expect(await frame.locator('.phys-viewport').evaluate(el=>{
    const t=[...el.querySelectorAll('span')].map(s=>s.__physTracker).find(Boolean);
    return t.view.renderWindow.getRenderers().some(r=>r.getActors().some(a=>a.getMapper()?.getScalarVisibility()&&a.getMapper()?.getInputData()?.getPointData().getArrayByName('__vis_scalar')));
   })).toBe(true);
  }
  await frame.getByLabel('着色物理量',{exact:true}).click();
  await frame.getByRole('option',{name:'纯色',exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.layers[0].field||null).toBe(null);
  await frame.getByLabel('着色物理量',{exact:true}).click();
  await frame.getByRole('option').filter({hasText:'(point)'}).first().click();
  await expect.poll(async()=>Boolean((await command({operation:'snapshot'})).spec.layers[0].field)).toBe(true);
  await frame.getByText('色标设置',{exact:true}).filter({visible:true}).click();
  await frame.getByLabel('色标方向',{exact:true}).click();
  await frame.getByRole('option',{name:'横向',exact:true}).click();
  await frame.getByLabel('色标位置',{exact:true}).click();
  await frame.getByRole('option',{name:'底部',exact:true}).click();
  await frame.getByRole('button',{name:'应用',exact:true}).click();
  await page.waitForTimeout(700);
  await page.screenshot({path:`${root}/legend-horizontal.png`});
  await frame.getByLabel('色标方向',{exact:true}).click();
  await frame.getByRole('option',{name:'纵向',exact:true}).click();
  await frame.getByLabel('色标位置',{exact:true}).click();
  await frame.getByRole('option',{name:'右侧',exact:true}).click();
  await frame.getByRole('button',{name:'应用',exact:true}).click();
  // 真实保存与下载链路，检查导出表单的透明请求，而不直接调用生产器。
  await frame.getByRole('button',{name:'文件',exact:true}).click();
  await frame.getByText('保存配置',{exact:true}).click();
  await page.getByLabel('可视化名称').fill(`显示验收 ${Date.now()}`);
  await page.getByRole('button',{name:'确 定',exact:true}).click();
  await expect(page.getByRole('dialog')).toHaveCount(0);
  await frame.getByRole('button',{name:'导出',exact:true}).click();
  await frame.getByText('图片 / 数据',{exact:true}).click();
  await page.getByRole('checkbox',{name:'透明背景'}).check();
  await page.getByRole('dialog').getByRole('button',{name:/生\s*成/}).click();
  const link=page.getByRole('link',{name:'view.png',exact:true});
  await expect(link).toBeVisible({timeout:90000});
  const download=await page.request.get(new URL(await link.getAttribute('href'),base).href);
  expect(download.ok()).toBe(true);fs.writeFileSync(`${root}/transparent-export.png`,await download.body());
  await frame.getByRole('button',{name:'切面',exact:true}).click();
  await expect(frame.getByText('显示辅助平面',{exact:true})).toBeVisible();
  const original=await command({operation:'snapshot'});const parent=original.spec.pipeline[0].id;
  await frame.getByLabel('着色变量',{exact:true}).click();
  const option=frame.getByRole('option').filter({hasText:'(point)'}).first();await option.click();
  await frame.getByRole('button',{name:'应用',exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.pipeline.length).toBe(2);
  const applied=await command({operation:'snapshot'});const slice=applied.spec.pipeline.find(n=>n.type==='slice');
  expect(applied.spec.layers.find(l=>l.input===slice.id).field).toBeTruthy();
  expect(applied.spec.layers.find(l=>l.input===parent)).toEqual(original.spec.layers.find(l=>l.input===parent));
  await frame.getByText('显示辅助平面',{exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).attachments.plane_widget.visible).toBe(false);
  await frame.getByText('显示辅助平面',{exact:true}).click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).attachments.plane_widget.visible).toBe(true);
  await expect.poll(()=>frame.locator('.phys-viewport').evaluate(el=>Boolean([...el.querySelectorAll('span')].map(s=>s.__physTracker).find(Boolean)?.planeWidget?.hitGeometry?.axis_x))).toBe(true);
  // 屏幕真实拖动轴；通过已发布几何选取轴端，不能用命令代替鼠标验收。
  for(const dragKind of ['translation','rotation']){
   const point=await frame.locator('.phys-viewport').evaluate((el,dragKind)=>{
    const t=[...el.querySelectorAll('span')].map(s=>s.__physTracker).find(Boolean);
    const r=t.view?.renderWindow.getRenderers().find(r=>r.getLayer()===0),v=t.view?.renderWindow.getViews()[0],sz=v?.getSize();
    const project=p=>{
      if(v){const d=v.worldToDisplay(...p,r);return [d[0]/sz[0],d[1]/sz[1]];}
      const e=t.cameras.find(e=>e.layer===0),c=e.camera,box=el.getBoundingClientRect();
      const sub=(a,b)=>a.map((v,i)=>v-b[i]),dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0),norm=a=>a.map(v=>v/Math.hypot(...a)),cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
      const forward=norm(sub(c.focal_point,c.position)),right=norm(cross(forward,c.view_up)),up=cross(right,forward),delta=sub(p,c.position);
      const scale=c.parallel_projection?c.parallel_scale:dot(delta,forward)*Math.tan((e.view_angle||30)*Math.PI/360);
      return [(1+dot(delta,right)/scale/(box.width/box.height))/2,(1+dot(delta,up)/scale)/2];
    };
    for(const name of (dragKind==='translation'?['axis_x','axis_y','axis_z']:['rotate_y','rotate_z'])){
     const tri=t.planeWidget.hitGeometry[name];
     for(let i=0;i<tri.length;i+=9){const p=[0,1,2].map(k=>(tri[i+k]+tri[i+3+k]+tri[i+6+k])/3);const [x,y]=project(p);
      if(x>.1&&x<.9&&y>.1&&y<.9&&physHitHandle(t.planeWidget,t.worldRay(x,y))===name)return {x,y};}
    }throw Error('没有可点击的轴');
   },dragKind);
   const box=await frame.locator('.phys-viewport').boundingBox();
   const before=await command({operation:'snapshot'});
   const coordinate=dragKind==='translation'?'原点 ':'法向（无量纲） ';
   const origin=await Promise.all([...'XYZ'].map(a=>frame.getByLabel(coordinate+a,{exact:true}).inputValue()));
   await page.mouse.move(box.x+box.width*point.x,box.y+box.height*(1-point.y));await page.mouse.down();await page.mouse.move(box.x+box.width*point.x+35,box.y+box.height*(1-point.y)+20,{steps:8});await page.mouse.up();
   await expect.poll(async()=>JSON.stringify(await Promise.all([...'XYZ'].map(a=>frame.getByLabel(coordinate+a,{exact:true}).inputValue())))).not.toBe(JSON.stringify(origin));
   const after=await command({operation:'snapshot'});expect(after.spec.pipeline).toEqual(before.spec.pipeline);expect(after.spec.views).toEqual(before.spec.views);
   await frame.getByRole('button',{name:'取消修改',exact:true}).click();
   await expect(frame.locator('.phys-draft-badge')).toBeHidden();
   await page.waitForTimeout(300);
  }
  for(const [w,h] of [[1440,900],[1672,941],[1920,1080]]){
   await page.setViewportSize({width:w,height:h});await page.waitForTimeout(300);
   await page.screenshot({path:`${root}/plane-${w}-${process.env.VIS_RENDERER||'local'}.png`});
   const overflow=await frame.locator('.phys-properties').evaluate(e=>({width:e.clientWidth,scroll:e.scrollWidth,items:[...e.querySelectorAll('*')].filter(n=>n.getBoundingClientRect().right>e.getBoundingClientRect().right+2).map(n=>({tag:n.tagName,cls:n.className,width:n.getBoundingClientRect().width})).slice(0,20)}));
   fs.writeFileSync(`${root}/overflow.json`,JSON.stringify(overflow,null,2));
   expect(overflow.scroll<=overflow.width+2).toBe(true);
  }
  await frame.locator('.phys-tree').getByText('基础显示',{exact:true}).click();
  await frame.getByRole('button',{name:'流线',exact:true}).click();
  for(const kind of ['线段','球体','平面']){
   await frame.getByRole('button',{name:'起点类型 '+kind,exact:true}).click();
   await expect(frame.getByLabel(({线段:'种子起点 X',球体:'球心 X',平面:'平面原点 X'})[kind],{exact:true})).toBeVisible();
   const preview=frame.getByRole('button',{name:'预览种子',exact:true});if(await preview.isVisible())await preview.click();
   await expect(frame.getByRole('button',{name:'隐藏预览',exact:true})).toBeVisible();
   // 参数回填后等待远程图像绘制稳定再截屏，不把上一种形状作为当前证据。
   await page.waitForTimeout(1500);
   await page.screenshot({path:`${root}/seed-${kind}-${process.env.VIS_RENDERER||'local'}.png`});
   expect((await command({operation:'snapshot'})).spec.pipeline.length).toBe(2);
  }
  await frame.getByRole('button',{name:'取消修改',exact:true}).click();
  await frame.getByRole('button',{name:'Probe',exact:true}).click();
  await expect(frame.locator('.phys-draft-badge')).toBeVisible();
  await page.screenshot({path:`${root}/probe-${process.env.VIS_RENDERER||'local'}.png`});
  await frame.getByRole('button',{name:'取消修改',exact:true}).click();
  await frame.getByRole('button',{name:'矢量图',exact:true}).click();
  await frame.getByRole('button',{name:'大小方式 固定',exact:true}).click();
  await frame.getByRole('button',{name:'采样方式 空间均匀',exact:true}).click();
  await frame.getByLabel('空间间距',{exact:true}).fill('0.1');
  await frame.getByLabel('空间间距',{exact:true}).press('Tab');
  for(const shape of ['箭头','圆锥','线段']){
   await frame.getByRole('button',{name:'符号形状 '+shape,exact:true}).click();
   await page.screenshot({path:`${root}/glyph-${shape}.png`});
  }
  await frame.getByRole('button',{name:'取消修改',exact:true}).click();
  // 独立隐藏父级后删除唯一可见子集，场景保持深色空视图。
  await command({operation:'display',id:parent,view:0,visible:false});
  await frame.locator('.phys-tree').getByText('切面 1',{exact:true}).click();
  const row=frame.locator('.phys-tree').getByText('切面 1',{exact:true}).locator('xpath=ancestor::div[contains(@class,"phys-node")]');
  await row.getByRole('button').last().click();
  const confirm=frame.getByRole('dialog').getByRole('button').filter({hasText:/删除|确定/}).last();await confirm.click();
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.pipeline.length).toBe(1);
  await expect(frame.getByRole('button',{name:'确认删除',exact:true})).toBeHidden();
  await page.waitForTimeout(700);
  await frame.locator('.phys-viewport').screenshot({path:`${root}/deleted-viewport.png`});
  await page.screenshot({path:`${root}/deleted-${process.env.VIS_RENDERER||'local'}.png`});
  const emptyBefore=await command({operation:'snapshot'});
  await command({operation:'source_remove',id:emptyBefore.spec.sources[0].id,cascade:true});
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.pipeline.length).toBe(0);
  await frame.getByRole('button',{name:'视图设置',exact:true}).click();
  const background=frame.getByLabel('背景颜色',{exact:true});
  await background.fill('#102030');await background.press('Tab');
  await expect.poll(async()=>(await command({operation:'snapshot'})).spec.views[0].background).toEqual([16/255,32/255,48/255]);
  await frame.getByRole('button',{name:'恢复默认背景',exact:true}).click();
  await page.mouse.click(1100,200);await page.waitForTimeout(500);
  await frame.locator('.phys-viewport').screenshot({path:`${root}/empty-sources.png`});
  expect(errors).toEqual([]);fs.writeFileSync(`${root}/result-${process.env.VIS_RENDERER||'local'}.json`,JSON.stringify({passed:true,errors},null,2));
 }catch(e){await page.screenshot({path:`${root}/failure-${process.env.VIS_RENDERER||'local'}.png`});console.error(e,errors);process.exitCode=1;}
 finally{for(const id of sessions)await page.request.delete(`${base}/api/phys/sessions/${id}?context_id=${context}`);await browser.close();}
})();
