import {test,expect} from '@playwright/test';
import path from 'node:path';
/** 组件夹具隔离参数数量差异，仅核验可一一对应的控件尺寸及布局比例。 */
for(const width of [1440,1920])for(const stage of ['model','training'] as const){
 test(`${width} ${stage} 对照整合原型控件与面板`,async({page,browser},info)=>{
  await page.setViewportSize({width,height:1000});await page.route('**/api/v1/**',r=>r.fulfill({json:[]}));await page.goto('/');
  await page.evaluate(async({stage,width})=>{
   const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;
   const file=stage==='model'?'/src/modules/models/ModelPanel.tsx':'/src/modules/training/TrainingPanel.tsx';const module=await import(file);const Component=module[stage==='model'?'ModelPanel':'TrainingPanel'];
   document.body.innerHTML='<div id="fixture"></div>';const fixture=document.getElementById('fixture')!;fixture.style.cssText=`margin-left:259px;width:${width-283}px;container-type:inline-size`;
   createRoot(fixture).render(React.createElement(Component,{values:stage==='model'?{parameters:{dim:192,depth:8},sampling:{num_anchors:128}}:{optimizer:'adamw',learning_rate:.001,max_epochs:2,batch_size:1},capabilities:{training_options:{optimizer:['adamw']}},bindings:null,trace:null,onChange:()=>{},onTrace:()=>{},onCheck:()=>{},onSave:()=>{},busy:false}));
  },{stage,width});
  const reference=await browser.newPage({viewport:{width,height:1000}});await reference.goto('file://'+path.resolve('../../docs/prototypes/dojo-web-integrated.html')+'#workbench/'+(stage==='model'?3:4));
  const frame=reference.frameLocator('iframe:visible');const selector=stage==='model'?'.model-section input':'.train-field input';
  const expected=await frame.locator(selector).first().evaluate(e=>({height:e.getBoundingClientRect().height,font:getComputedStyle(e).fontSize}));
  const field=page.locator(`.${stage}-layout .configuration-field .ant-input-number`).first();await expect(field).toBeVisible();const current=await field.evaluate(e=>({height:e.getBoundingClientRect().height,font:getComputedStyle(e).fontSize}));expect(Math.abs(expected.height-current.height)).toBeLessThanOrEqual(1);expect(current.font).toBe(expected.font);
  const expectedLayout=await frame.locator(`.${stage}-layout`).evaluate(e=>({width:e.getBoundingClientRect().width,gap:getComputedStyle(e).gap,columns:getComputedStyle(e).gridTemplateColumns}));const actualLayout=await page.locator(`.${stage}-layout`).evaluate(e=>({width:e.getBoundingClientRect().width,gap:getComputedStyle(e).gap,columns:getComputedStyle(e).gridTemplateColumns}));expect(Math.abs(actualLayout.width-expectedLayout.width)).toBeLessThanOrEqual(1);expect(actualLayout.gap).toBe(expectedLayout.gap);expect(actualLayout.columns).toBe(expectedLayout.columns);
  await info.attach('component-prototype-measurement',{body:JSON.stringify({width,stage,expected,current,expectedLayout,actualLayout}),contentType:'application/json'});await page.screenshot({path:info.outputPath(`${stage}-${width}.png`),fullPage:true});await reference.close();
 });
}

/** 真实服务创建与首页入口点击；几何来自页面，绝不拦截业务接口。 */
test('真实任务1440/1920整页外壳、原始处理、模型训练和三维对照',async({page,browser,request},info)=>{
 test.setTimeout(180000);
 const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
 const made=await request.post(api+'/projects',{data:{name:'整页一致性验收 '+Date.now()}});expect(made.ok()).toBeTruthy();const project=await made.json();
 const created=await request.post(`${api}/projects/${project.id}/tasks`,{data:{name:'整页实际任务',case_id:'shapenet_car_transolver3_surface',data_root:'data0'}});expect(created.ok()).toBeTruthy();const task=await created.json();
 const reference=await browser.newPage();const records:any[]=[];
 const evidence=path.resolve('../../.context/mvp/web-integrated-results/ui-consistency');const fs=await import('node:fs');fs.mkdirSync(evidence,{recursive:true});
 try{
  await page.goto('/projects');await page.getByRole('textbox',{name:'搜索项目',exact:true}).fill(project.name);await page.locator('.taskcard').filter({hasText:project.name}).getByRole('link',{name:'进入项目',exact:true}).click();await page.getByRole('link',{name:'进入工作台',exact:true}).click();await expect(page).toHaveURL(new RegExp(`/tasks/${task.id}/1$`));
  for(const width of [1440,1920])for(const step of [1,3,4,6]){
   await page.setViewportSize({width,height:1000});await reference.setViewportSize({width,height:1000});
   const selector=({1:'.workbench-grid',3:'.model-layout',4:'.training-layout',6:'.post-visualization-layout'}as Record<number,string>)[step];
   await page.locator(`.workbench-steps a[href$="/${step}"]`).click();await expect(page.locator(selector)).toBeVisible();await reference.goto('file://'+path.resolve('../../docs/prototypes/dojo-web-integrated.html')+'#workbench/'+step);await expect(reference.locator('iframe:visible')).toHaveCount(1);await expect(reference.frameLocator('iframe:visible').locator(({1:'.layout',3:'.model-layout',4:'.training-layout',6:'.post-body'}as Record<number,string>)[step])).toBeVisible();
   const measured=await page.evaluate(selector=>{const rect=(s:string)=>document.querySelector(s)!.getBoundingClientRect().toJSON();const grid=document.querySelector(selector)!;return{heading:rect('.taskheading'),steps:rect('.topsteps'),footer:rect('.stage-foot'),grid:rect(selector),panels:[...grid.children].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.getBoundingClientRect().toJSON())}},selector);
   const expected=await reference.evaluate(step=>{const rect=(e:Element)=>e.getBoundingClientRect().toJSON();const frame=[...document.querySelectorAll('iframe')].find(f=>f.getBoundingClientRect().width>0)!;const offset=rect(frame);const local=(e:Element)=>{const r=rect(e);return{...r,x:r.x+offset.x,y:r.y+offset.y}};const grid=frame.contentDocument!.querySelector(({1:'.layout',3:'.model-layout',4:'.training-layout',6:'.post-body'}as Record<number,string>)[step])!;return{heading:rect(document.querySelector('.taskheading')!),steps:rect(document.querySelector('.topsteps')!),footer:rect(document.querySelector('.integrated-footer')!),grid:local(grid),panels:[...grid.children].filter(e=>e.getBoundingClientRect().width>0).map(local)}},step);
   records.push({width,step,project:project.id,task:task.id,expected,measured,exceptions:step===3&&width===1440?['单列模型参数内容数量来自真实案例，首面板及整个内容高度不与示例固定参数数目比较；阶段窗口仍按820px独立滚动。']:[]});
   fs.writeFileSync(path.join(evidence,'whole-page-measurements.json'),JSON.stringify(records,null,2));
   for(const area of ['heading','steps','footer','grid']as const)for(const axis of ['x','y','width','height']as const){if(area==='grid'&&axis==='height'&&step===3&&width===1440)continue;expect(Math.abs(measured[area][axis]-expected[area][axis]),`${width} step${step} ${area}.${axis}`).toBeLessThanOrEqual(1)}
   if(step===1||step===6){expect(measured.panels).toHaveLength(expected.panels.length);for(let i=0;i<expected.panels.length;i++)for(const axis of ['x','y','width','height']as const)expect(Math.abs(measured.panels[i][axis]-expected.panels[i][axis]),`${width} step${step} panel${i}.${axis}`).toBeLessThanOrEqual(1)}
   if(step===3||step===4){const input=page.locator(selector+' .configuration-field .ant-input-number').first();const refinput=reference.frameLocator('iframe:visible').locator(step===3?'.model-section input':'.train-field input').first();expect(Math.abs((await input.boundingBox())!.height-(await refinput.boundingBox())!.height)).toBeLessThanOrEqual(1)}
   await page.screenshot({path:path.join(evidence,`actual-${width}-${step}.png`),fullPage:true});await reference.screenshot({path:path.join(evidence,`prototype-${width}-${step}.png`),fullPage:true});
  }
  await info.attach('whole-page-measurements',{body:JSON.stringify(records,null,2),contentType:'application/json'});
 }finally{await reference.close();await request.patch(`${api}/projects/${project.id}`,{data:{archived:true}})}
});
