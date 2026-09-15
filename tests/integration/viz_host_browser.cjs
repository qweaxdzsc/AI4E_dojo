/** 三个宿主调用模式共用公开入口的真实嵌入链路；不使用模拟 Vis 服务。 */
const {chromium, expect}=require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const root=process.env.VIS_EVIDENCE_ROOT;if(!root)throw new Error('必须显式指定证据目录');fs.mkdirSync(root,{recursive:true});
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1600,height:1100}});const api='http://127.0.0.1:18080/api/v1';
 const project=(await (await page.request.post(api+'/projects',{data:{name:'三入口可视化验收 '+Date.now()}})).json()).id;
 const task=(await (await page.request.post(`${api}/projects/${project}/tasks`,{data:{name:'物理场配置目标'}})).json()).id;
 const source=await (await page.request.post(`${api}/projects/${project}/assets`,{data:{root:'data0',path:'frame0.vti',task_id:task}})).json();
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 try{
  for(const mode of ['preview','post','comparison']){
   await page.goto('http://127.0.0.1:18173/projects');
   await page.evaluate(async({source,project,task,mode})=>{
    const React=await import('/node_modules/.vite/deps/react.js');const DOM=await import('/node_modules/.vite/deps/react-dom_client.js');const {VisualizationWorkspace}=await import('/src/modules/visualization/index.ts');
    const host=document.createElement('div');document.body.replaceChildren(host);window.__physHostRoot=(DOM.createRoot||DOM.default.createRoot)(host);window.__physHostRoot.render((React.createElement||React.default.createElement)(VisualizationWorkspace,{sources:[source],scope:{project_id:project,task_id:task},mode}));
   },{source,project,task,mode});
   const outer=page.frameLocator('iframe[title="独立可视化应用"]');
   const inner=outer.frameLocator('iframe[title="三维物理场 Trame 工作台"]');
   await inner.locator('.phys-tree').waitFor({timeout:60000});
   await expect(inner.locator('canvas').first()).toBeVisible();
   await inner.getByRole('button',{name:'文件',exact:true}).click();await inner.getByText('保存配置',{exact:true}).click();
   await outer.getByLabel('可视化名称').fill(mode+' 来源配置');
   await outer.getByRole('button',{name:'确 定'}).click();
   await expect(outer.getByRole('dialog')).toHaveCount(0,{timeout:20000});
   await inner.getByRole('button',{name:'文件',exact:true}).click();await inner.getByText('导入结果',{exact:true}).click();
   await outer.getByRole('dialog').waitFor();await outer.getByRole('combobox',{name:'结果资产'}).press('ArrowDown');await outer.locator('.ant-select-item-option').first().click();await outer.getByRole('button',{name:'确 定',exact:true}).click();
   await expect(outer.getByRole('dialog')).toHaveCount(0);await expect(inner.locator('.phys-tree').getByText('基础显示',{exact:true})).toHaveCount(2);
   await inner.getByRole('button',{name:'文件',exact:true}).click();await inner.getByText('保存配置',{exact:true}).click();await outer.getByRole('button',{name:'确 定'}).click();await expect(outer.getByRole('dialog')).toHaveCount(0);
   await inner.getByRole('button',{name:'文件',exact:true}).click();await inner.getByText('打开已保存配置',{exact:true}).click();await outer.getByRole('combobox',{name:'打开配置资产'}).press('ArrowDown');await outer.getByText(mode+' 来源配置 · r2',{exact:true}).click();
   await inner.locator('.phys-tree').waitFor({timeout:60000});await expect(inner.locator('.phys-tree').getByText('基础显示',{exact:true})).toHaveCount(2,{timeout:30000});
   await page.screenshot({path:path.join(root,mode+'-embedded.png')});
   await page.evaluate(()=>window.__physHostRoot.unmount());
  }
  // 真正从项目文件页面进入，验证目录浏览、任务选择和嵌入组合。
  await page.goto('http://127.0.0.1:18173/projects/'+project+'/files');
  await page.getByRole('combobox',{name:'文件范围',exact:true}).press('ArrowDown');
  await page.locator('.ant-select-item-option-content').filter({hasText:'data0 ·'}).click();
  await page.getByRole('button',{name:'frame0.vti',exact:true}).click();
  await page.getByRole('combobox',{name:'可视化目标任务'}).press('ArrowDown');
  await page.locator('.ant-select-item-option-content').filter({hasText:'物理场配置目标'}).click();
  const routeFrame=page.frameLocator('iframe[title="独立可视化应用"]');
  await routeFrame.frameLocator('iframe').locator('.phys-tree').waitFor({timeout:60000});
  await page.screenshot({path:path.join(root,'project-files-entry.png')});
  await page.getByRole('dialog').getByRole('button',{name:'Close',exact:true}).click();
  const assets=await (await page.request.get(`${api}/projects/${project}/tasks/${task}/visualizations`)).json();
  if(assets.items.length!==3)throw new Error(JSON.stringify(assets));
  const lineage=await (await page.request.get(`${api}/projects/${project}/lineage`)).json();if(lineage.length!==1)throw new Error('保存增加了研究任务版本');
  if(errors.length)throw new Error(errors.join('\n'));
  fs.writeFileSync(path.join(root,'host-browser-results.json'),JSON.stringify({status:'passed',project,task,modes:['preview','post','comparison'],assets:assets.items.map(x=>x.visualization_id),lineage:lineage.length,real_routes:['project files to Trame'],scope:'三个调用模式通过公开微领域组件测试真实双层 iframe、HTTP/WS 与保存；不宣称科研阶段计算验收'},null,2));console.log('HOST PASS',project);
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
