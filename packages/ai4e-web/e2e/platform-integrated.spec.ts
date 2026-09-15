import {test,expect} from '@playwright/test';
import fs from 'node:fs';
import path from 'node:path';
/** 消费总链路真实产物，验证宿主选择、固定输入、能力约束和布局。 */
test('真实汽车案例页面配置与正式产物交接',async({page,request},info)=>{
 const evidence=JSON.parse(fs.readFileSync(path.resolve('../../.context/mvp/web-integrated-results/shapenet_car_transolver3_surface.json'),'utf8'));
 const p=evidence.project,t=evidence.task,api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.setViewportSize({width:1440,height:1000});
 const measurements:any[]=[];
 for(const [step,selector]of [[2,'.preparation-layout'],[3,'.model-layout'],[4,'.training-layout'],[5,'.training-monitor'],[6,'.post-config']] as const){
  await page.goto(`/projects/${p}/tasks/${t}/${step}`);await expect(page.getByRole('button',{name:'保存配置',exact:true})).toBeVisible();
  await expect(page.locator('.workbench-steps .topstep')).toHaveCount(8);
  const layout=await page.evaluate(()=>({sidebar:document.querySelector('.ant-layout-sider')?.getBoundingClientRect().toJSON(),header:document.querySelector('.ant-layout-header')?.getBoundingClientRect().toJSON(),steps:document.querySelector('.workbench-steps')?.getBoundingClientRect().toJSON()}));
  expect(layout.sidebar.width).toBe(235);expect(layout.header.height).toBe(61);expect(layout.steps.x).toBeGreaterThanOrEqual(234);measurements.push({step,...layout});
  if(step===2||step===3){const input=page.getByRole('combobox',{name:'train.manifest',exact:true});await input.click();await page.locator('.ant-select-item-option').first().click();await expect(input.locator('..')).not.toContainText('选择正式运行产物');}
  if(step===2||step===4)await expect(page.locator('.execution-log')).not.toContainText('[post/阶段/开始]');
  if(step===3){await expect(page.locator('.execution-log')).toHaveCount(0);await expect(page.getByText(/固定等权 MSE/)).toBeVisible();await expect(page.getByText('隐藏层宽度',{exact:true})).toBeVisible();}
  if(step===4){const batch=page.locator('.configuration-field').filter({has:page.locator('label',{hasText:'批次大小'})}).getByRole('spinbutton');await expect(batch).toBeDisabled();const epochs=page.locator('.configuration-field').filter({has:page.locator('label',{hasText:'训练轮数'})}).getByRole('spinbutton');const old=await epochs.inputValue();await epochs.fill(old);await epochs.press('ArrowUp');await page.getByRole('button',{name:'保存配置',exact:true}).click();await expect(page.getByText('配置已保存，未创建新版本')).toBeVisible();await epochs.fill(old);await page.getByRole('button',{name:'保存配置',exact:true}).click();}
  if(step===6){await expect(page.locator('.post-shell')).toBeVisible();await expect(page.locator('.post-tabs [role=tab]')).toHaveCount(3);await expect(page.getByText('结果文件',{exact:true})).toBeVisible();await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'后处理运行',exact:true})}).click();await page.locator('.ant-select-item-option').filter({hasText:evidence.stages.post.id.slice(0,8)}).click();const response=await request.get(`${api}/projects/${p}/runs/${evidence.stages.post.id}/metrics`);expect(response.ok()).toBeTruthy();const metrics=await response.json();expect(metrics.evaluation).toBeTruthy();await page.getByRole('tab',{name:'指标数据',exact:true}).click();await expect(page.getByText('surface.pressure / mse',{exact:true})).toBeVisible();await page.getByRole('tab',{name:'图表',exact:true}).click();await expect(page.locator('.post-chart-grid>.ant-card')).toHaveCount(4);await expect(page.getByRole('img',{name:'mse 真实评价',exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'暂无记录',exact:true})).toHaveCount(2);}
  await page.screenshot({path:info.outputPath(`stage-${step}.png`),fullPage:true});
 }
 await info.attach('layout-measurements',{body:JSON.stringify(measurements,null,2),contentType:'application/json'});expect(errors).toEqual([]);
});

test('整合原型主面板几何逐项回归',async({browser},info)=>{
 const prototype=await browser.newPage({viewport:{width:1440,height:1000}}),actual=await browser.newPage({viewport:{width:1440,height:1000}});
 const evidence=JSON.parse(fs.readFileSync(path.resolve('../../.context/mvp/web-integrated-results/shapenet_car_transolver3_surface.json'),'utf8'));
 const rows:any[]=[];
 const pairs=[['.layout','.workbench-grid'],['.prep-layout','.prepare-layout'],['.model-layout','.model-layout'],['.training-layout','.training-layout'],['.run-grid','.monitor-grid'],['.post-chart-grid','.post-chart-grid']];
 for(const step of [1,2,3,4,5,6]){
  await prototype.goto('file://'+path.resolve('../../docs/prototypes/dojo-web-integrated.html')+'#workbench/'+step);await expect(prototype.locator('iframe:visible')).toHaveCount(1);
  await actual.goto((process.env.DOJO_WEB_URL||'http://127.0.0.1:5174')+`/projects/${evidence.project}/tasks/${evidence.task}/${step}`);await expect(actual.locator('.workbench-steps')).toBeVisible();if(step>1)await expect(actual.getByRole('button',{name:'保存配置',exact:true})).toBeVisible();
  if(step===6){await prototype.frameLocator('iframe:visible').getByRole('tab',{name:'图表',exact:true}).click();await actual.getByRole('tab',{name:'图表',exact:true}).click()}
  const reference=await prototype.evaluate(selector=>{const f=[...document.querySelectorAll('iframe')].find(f=>f.getBoundingClientRect().width>0)!;const d=f.contentDocument!,container=d.querySelector(selector)!;return{panels:[...container.children].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.getBoundingClientRect().toJSON()),gap:getComputedStyle(container).gap,headings:[...d.querySelectorAll('h2,h3')].map(e=>e.textContent)}},pairs[step-1][0]);
  const current=await actual.evaluate(selector=>{const container=document.querySelector(selector)!;return{panels:[...container.children].filter(e=>e.getBoundingClientRect().width>0).map(e=>e.getBoundingClientRect().toJSON()),gap:getComputedStyle(container).gap}},pairs[step-1][1]);
  rows.push({step,reference,current});fs.writeFileSync('/private/tmp/dojo-platform-layout-comparison.json',JSON.stringify(rows,null,2));
  const expected=[3,3,2,2,2,4][step-1];expect(reference.panels.length).toBe(expected);expect(current.panels.length).toBe(expected);
  if(step===2){expect(current.gap).toBe('9px');for(let i=0;i<current.panels.length;i++){expect(Math.abs(current.panels[i].height-640),`step ${step} panel ${i} height`).toBeLessThanOrEqual(1);expect(Math.abs(current.panels[i].width-reference.panels[i].width),`step ${step} panel ${i} width`).toBeLessThanOrEqual(24)}}
  else{for(let i=0;i<current.panels.length;i++){expect(Math.abs(current.panels[i].width-reference.panels[i].width),`step ${step} panel ${i} width`).toBeLessThanOrEqual(2);expect(Math.abs(current.panels[i].height-reference.panels[i].height),`step ${step} panel ${i} height`).toBeLessThanOrEqual(2)}expect(current.gap).toBe(reference.gap)}
 }
 await info.attach('prototype-layout-comparison',{body:JSON.stringify(rows,null,2),contentType:'application/json'});await prototype.close();await actual.close();
});

test('提取卡片草稿取消不会保存',async({page})=>{
 let saved=0;
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/rawprep')&&route.request().method()==='PUT')saved+=1;
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{dataset_id:'shapenet_car',source_files:{surface:'quadpress_smpl.vtk',volume:'hexvelo_smpl.vtk'},outputs:[{name:'surface_pressure',label:'表面压力',domain:'surface',association:'point',components:1,filename:'quadpress_smpl.vtk',raw_field:'surface/point/point_scalars'}],geometry:[],filters:[],formats:['pt'],vtkhdf:false,statistics_modes:['none'],defaults:{save_fields:['surface_pressure']}},rawprep:{format:'pt',save_fields:['surface_pressure'],geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:['surface']}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'train/a'}],fields:[{field_id:'surface/point/point_scalars',name:'point_scalars',association:'point',shape:[10,1],components:1,semantic_key:'surface'}],sources:[{source_id:'train/a/surface',relative_path:'data0::train/a/quadpress_smpl.vtk',exists:true},{source_id:'train/a/volume',relative_path:'data0::train/a/hexvelo_smpl.vtk',exists:true}],inspection:{checked_samples:['train::a']},errors:[]};
  else if(url.pathname.endsWith('/runs'))value=[];
  else if(url.pathname.includes('/stage-files'))value=[];
  else if(url.pathname.endsWith('/files'))value=[{name:'quadpress_smpl.vtk',path:'train/a/quadpress_smpl.vtk',directory:false},{name:'hexvelo_smpl.vtk',path:'train/a/hexvelo_smpl.vtk',directory:false},{name:'press.npy',path:'train/a/press.npy',directory:false},{name:'notes.txt',path:'train/a/notes.txt',directory:false}];
  else if(url.pathname.includes('/preview'))value={kind:'mesh',fields:[{field_id:'surface/point/point_scalars',name:'point_scalars',association:'point',shape:[10,1],components:1},{field_id:'surface/geometry/points',name:'points',association:'geometry',shape:[10,3],components:3}]};
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await page.getByRole('button',{name:'＋ 添加字段提取',exact:true}).click();
 const dialog=page.getByRole('dialog');
 await expect(dialog.getByText('勾选一个字段')).toBeVisible();
 await expect(dialog.getByText('输出格式',{exact:true})).toHaveCount(0);
 await expect(dialog.getByRole('button',{name:'添加输出',exact:true})).toHaveCount(0);
 await expect(dialog.locator('.ant-select-selection-item')).toHaveText(/quadpress_smpl\.vtk|hexvelo_smpl\.vtk|press\.npy/);
 await dialog.locator('.ant-select-selector').click();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'quadpress_smpl.vtk'})).toBeVisible();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'hexvelo_smpl.vtk'})).toBeVisible();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'press.npy'})).toBeVisible();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'notes.txt'})).toHaveCount(0);
 await dialog.getByRole('button',{name:/取\s*消/}).click();
 await expect(dialog).toHaveCount(0);
 expect(saved).toBe(0);
});

test('编辑字段提取回填默认源文件和字段',async({page})=>{
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',status:'valid',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{source_files:{surface:'quadpress_smpl.vtk'},outputs:[{name:'surface_pressure',label:'表面压力',domain:'surface',association:'point',components:1,filename:'quadpress_smpl.vtk',raw_field:'surface/point/point_scalars'}],geometry:[],filters:[],formats:['pt'],vtkhdf:false,statistics_modes:['none'],defaults:{}},rawprep:{format:'pt',save_fields:['surface_pressure'],geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:['surface']}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'train/a'}],fields:[{field_id:'surface/point/point_scalars',name:'point_scalars',association:'point',shape:[3682,1],components:1,semantic_key:'surface'}],sources:[{source_id:'train/a/surface',relative_path:'data0::train/a/quadpress_smpl.vtk',exists:true},{source_id:'train/a/volume',relative_path:'data0::train/a/hexvelo_smpl.vtk',exists:true}],inspection:{checked_samples:['train::a']},errors:[]};
  else if(url.pathname.endsWith('/files'))value=[{name:'quadpress_smpl.vtk',path:'train/a/quadpress_smpl.vtk',directory:false},{name:'hexvelo_smpl.vtk',path:'train/a/hexvelo_smpl.vtk',directory:false}];
  else if(url.pathname.includes('/preview'))value={kind:'mesh',fields:[{field_id:'surface/point/point_scalars',name:'point_scalars',association:'point',shape:[3682,1],components:1},{field_id:'surface/geometry/points',name:'points',association:'geometry',shape:[3682,3],components:3}]};
  else if(url.pathname.endsWith('/runs')||url.pathname.includes('/stage-files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await page.getByRole('button',{name:'编辑 surface_pressure',exact:true}).click();
 const dialog=page.getByRole('dialog');
 await expect(dialog.locator('.ant-select-selection-item')).toHaveText('quadpress_smpl.vtk');
 await expect(dialog.getByRole('radio')).toHaveCount(2);
 await expect(dialog.getByRole('row').filter({hasText:'point_scalars'}).getByRole('radio')).toBeChecked();
 await expect(dialog.getByText('将保存为')).toContainText('surface_pressure.pt');
});

test('几何派生场不进提取列表并在右侧显示命名',async({page})=>{
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',status:'valid',sources:{root:{root:'data0',path:''}},errors:[],binding_schema:{mode:'directory',root_key:'root',slots:[{key:'root',label:'目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{outputs:[
   {name:'surface_pressure',label:'表面压力',domain:'surface',association:'point',components:1,requires:[]},
   {name:'surface_position',label:'表面坐标',domain:'surface',association:'geometry',components:3,required:true,requires:[]},
   {name:'surface_normals',label:'表面法向',domain:'surface',association:'point',components:3,requires:['surface_normals']},
   {name:'volume_sdf',label:'最近距离',domain:'volume',association:'point',components:1,requires:['nearest_vertex']},
   {name:'volume_normals',label:'体积法向',domain:'volume',association:'point',components:3,requires:['volume_normals']},
   {name:'volume_surface_distance',label:'点到表面有符号距离',domain:'volume',association:'point',components:1,requires:['mesh_signed_distance']},
   {name:'volume_closest_surface',label:'表面最近点',domain:'volume',association:'point',components:3,requires:['mesh_signed_distance']},
   {name:'volume_surface_direction',label:'表面最近方向',domain:'volume',association:'point',components:3,requires:['mesh_signed_distance']},
  ],geometry:[
   {id:'nearest_vertex',label:'最近顶点距离',output:'volume_sdf',domains:['surface','volume'],parameters:{epsilon:{label:'数值稳定阈值',default:1e-8}},conflicts:[]},
   {id:'volume_normals',label:'体积法向',output:'volume_normals',domains:['surface','volume'],parameters:{epsilon:{label:'数值稳定阈值',default:1e-8}},conflicts:[]},
   {id:'mesh_signed_distance',label:'点到网格表面距离',output:['volume_surface_distance','volume_closest_surface','volume_surface_direction'],domains:['surface','volume'],parameters:{epsilon:{label:'数值稳定阈值',default:1e-8}},conflicts:[]},
   {id:'surface_normals',label:'表面法向',output:'surface_normals',domains:['surface'],parameters:{epsilon:{label:'数值稳定阈值',default:1e-8}}},
  ],filters:[],formats:['pt'],vtkhdf:false,statistics_modes:['none'],defaults:{}},rawprep:{format:'pt',save_fields:['surface_pressure','surface_position','surface_normals','volume_sdf','volume_normals'],geometry:{nearest_vertex:{},volume_normals:{},surface_normals:{}},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:['surface','volume']}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[],fields:[],sources:[],inspection:{checked_samples:[]},errors:[]};
  else if(url.pathname.endsWith('/runs')||url.pathname.includes('/stage-files')||url.pathname.endsWith('/files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByRole('button',{name:'编辑 surface_pressure',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'编辑 surface_normals',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'编辑 volume_sdf',exact:true})).toHaveCount(0);
 await expect(page.locator('.extraction-card')).toHaveCount(2);
 await expect(page.getByText('数值稳定阈值',{exact:true})).toHaveCount(0);
 await expect(page.getByRole('textbox',{name:'命名 表面法向',exact:true})).toHaveValue('surface_normals');
 await expect(page.getByRole('textbox',{name:'命名 最近距离',exact:true})).toHaveValue('volume_sdf');
 await expect(page.getByRole('textbox',{name:'命名 体积法向',exact:true})).toHaveValue('volume_normals');
 await expect(page.getByRole('textbox',{name:'命名 最近方向',exact:true})).toHaveCount(0);
 await page.getByRole('checkbox',{name:'点到网格表面距离',exact:true}).check();
 await expect(page.getByRole('textbox',{name:'命名 点到表面有符号距离',exact:true})).toHaveValue('volume_surface_distance');
 await expect(page.getByRole('textbox',{name:'命名 表面最近点',exact:true})).toHaveValue('volume_closest_surface');
 await expect(page.getByRole('textbox',{name:'命名 表面最近方向',exact:true})).toHaveValue('volume_surface_direction');
 const stacked=page.locator('.geometry-row',{hasText:'点到网格表面距离'}).locator('.geometry-names input');
 await expect(stacked).toHaveCount(3);
 const first=await stacked.nth(0).boundingBox();
 const second=await stacked.nth(1).boundingBox();
 const third=await stacked.nth(2).boundingBox();
 expect(first&&second&&third&&second.y>first.y+first.height-1&&third.y>second.y+second.height-1).toBeTruthy();
 await page.getByRole('textbox',{name:'命名 最近距离',exact:true}).fill('custom_sdf');
 await expect(page.getByRole('button',{name:'编辑 custom_sdf',exact:true})).toHaveCount(0);
 await expect(page.getByRole('textbox',{name:'命名 最近距离',exact:true})).toHaveValue('custom_sdf');
});

/** 捕获真实保存响应：进行中禁用，快速完成后装饰图标不改变操作名称。 */
test('快速保存与进行中按钮状态不会滞留',async({page,request})=>{
 const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
 const project=await(await request.post(api+'/projects',{data:{name:'保存状态回归 '+Date.now()}})).json();
 const created=await request.post(`${api}/projects/${project.id}/tasks`,{data:{name:'保存状态',case_id:'shapenet_car_transolver3_surface',data_root:'data0'}});expect(created.ok()).toBeTruthy();const task=await created.json();
 await page.goto(`/projects/${project.id}/tasks/${task.id}/4`);
 const save=page.getByRole('button',{name:'保存配置',exact:true});const check=page.getByRole('button',{name:'检查配置与交接',exact:true});const epochs=page.locator('.configuration-field').filter({has:page.locator('label',{hasText:'训练轮数'})}).getByRole('spinbutton');
 await expect(save).toBeVisible();
 let release!:()=>void;const held=new Promise<void>(resolve=>release=resolve);let reached!:()=>void;const responseReady=new Promise<void>(resolve=>reached=resolve);
 await page.route('**/configuration',async route=>{if(route.request().method()!=='PUT')return route.continue();const response=await route.fetch();expect(response.ok()).toBeTruthy();reached();await held;await route.fulfill({response})},{times:1});
 await epochs.press('ArrowUp');await save.click();await responseReady;
 await expect(save).toBeDisabled();await expect(check).toBeDisabled();await expect(save).toHaveAttribute('aria-busy','true');await expect(save).toHaveAccessibleName('保存配置');release();
 await expect(save).toHaveAttribute('aria-busy','false');await expect(check).toBeEnabled();
 for(let i=0;i<3;i++){
  await epochs.press('ArrowUp');await expect(save).toBeEnabled();const response=page.waitForResponse(r=>r.request().method()==='PUT'&&r.url().endsWith('/configuration'));await save.click();expect((await response).ok()).toBeTruthy();
  await expect(save).toHaveAttribute('aria-busy','false');await expect(save).toBeDisabled();await expect(check).toBeEnabled();await expect(save.getByRole('img',{name:'loading'})).toHaveCount(0);await expect(save).not.toHaveClass(/ant-btn-loading/);
 }
});
