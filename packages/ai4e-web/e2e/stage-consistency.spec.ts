import {test,expect} from '@playwright/test';
/** 传输故障使用明确契约夹具；真实服务/算法链由集成验收另行覆盖。 */
test('阶段检查先保存，冲突不提交，响应丢失重用请求键',async({page})=>{
 let revision='r1',values={max_epochs:2},conflict=true,posts:any[]=[],saves:any[]=[];let failResponse=true;
 await page.route('**/api/v1/**',async route=>{
  const req=route.request(),url=new URL(req.url());
  if(url.pathname.endsWith('/configuration')){
   if(req.method()==='PUT'){saves.push(req.postDataJSON());if(conflict)return route.fulfill({status:409,json:{detail:'configuration_revision_conflict'}});values=req.postDataJSON().values;revision='r2';return route.fulfill({json:{revision,config:{train:values}}})}
   return route.fulfill({json:{revision,stage:'train',values,capabilities:{}}});
  }
  if(url.pathname.endsWith('/stages/train/operations')){posts.push(req.postDataJSON());if(failResponse){failResponse=false;return route.abort('failed')}return route.fulfill({json:{operation_id:'checked',status:'succeeded',result:{valid:true}}})}
  return route.fulfill({json:[]});
 });
 await page.goto('/');await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(StageWorkbench,{project:'fixture',task:'fixture',stage:'train'}))});
 const epochs=page.locator('.configuration-field').filter({has:page.locator('label',{hasText:'训练轮数'})}).getByRole('spinbutton');await epochs.fill('3');await page.getByRole('button',{name:'预检',exact:true}).click();await expect(page.getByText('configuration_revision_conflict',{exact:false})).toBeVisible();expect(posts).toHaveLength(0);await expect(epochs).toHaveValue('3');
 conflict=false;await page.getByRole('button',{name:'预检',exact:true}).evaluate((button:HTMLButtonElement)=>{button.click();button.click()});await expect(page.getByText(/配置已保存；后续操作失败/)).toBeVisible();expect(posts).toHaveLength(1);expect(posts[0].expected_revision).toBe('r2');expect(saves).toHaveLength(2);
 await page.getByRole('button',{name:'预检',exact:true}).click();await expect(page.getByText('配置与交接检查通过',{exact:true})).toBeVisible();expect(posts).toHaveLength(2);expect(posts[0].idempotency_key).toBe(posts[1].idempotency_key);expect(saves).toHaveLength(2);
});

test('浏览后处理不勾选前序步骤，已选输入按selected恢复',async({page})=>{
 const summary={rawprep:{status:'succeeded',run_id:'raw'},trainprep:{status:'not_run'},train:{status:'not_run'},post:{status:'not_run'},model:{status:'stale'},training:{status:'unchecked'}};
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname==='/api/v1/projects')return route.fulfill({json:[{id:'p',name:'测试项目'}]});
  if(url.pathname==='/api/v1/projects/p/tasks/t')return route.fulfill({json:{id:'t',name:'测试任务',stage_summary:summary}});
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:url.searchParams.get('stage')||'model',values:url.searchParams.get('stage')==='trainprep'?{domains:{},normalization:{fields:{}}}:{parameters:{dim:192}},config:{},capabilities:{field_matching:{model_roles:[],dataset_fields:[]}}}});
  if(url.pathname.endsWith('/model-options'))return route.fulfill({json:{current_model_id:'abupt',options:[{id:'abupt',name:'AB-UPT',structure_version:{id:'default',name:'案例默认'}}],presets:[],trace_available:true}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[{binding:'train.manifest',run_id:'older',name:'已绑定清单',selected:true,ref:{asset_id:'chosen',revision:'fixed'}},{binding:'train.manifest',run_id:'newer',name:'更新清单',selected:false,ref:{asset_id:'new',revision:'new'}}]});
  if(url.pathname.includes('/post/results'))return route.fulfill({json:{items:[],files:[],batches:[],errors:[],total:0}});
  if(url.pathname.includes('/metrics/catalog'))return route.fulfill({json:{metrics:[]}});
  if(url.pathname.includes('/metric-jobs'))return route.fulfill({json:{items:[]}});
  return route.fulfill({json:[]});
 });
 await page.goto('/projects/p/tasks/t/6');await expect(page.locator('.workbench-steps .topstep.done')).toHaveCount(1);await expect(page.locator('.taskheading .statuspill')).toHaveText('部分阶段完成');await page.getByRole('link',{name:'模型设置 · 检查失效',exact:true}).click();await expect(page.locator('.workbench-steps .topstep.done')).toHaveCount(1);await expect(page.getByRole('combobox',{name:'train.manifest'})).toHaveCount(0);await expect(page.locator('summary',{hasText:'权重加载'})).toHaveCount(0);await page.getByRole('link',{name:'数据准备 · 未运行',exact:true}).click();await expect(page.locator('.input-bindings .ant-select-selection-item').first()).toContainText('已绑定清单');await expect(page.locator('.input-bindings .ant-select-selection-item').first()).not.toContainText('更新清单');
});

test('平台数据集同一清单只选一条，不与历史项联动',async({page})=>{
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:'trainprep',values:{domains:{},normalization:{fields:{}}},capabilities:{field_matching:{model_roles:[],dataset_fields:[]}}}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[
   {binding:'train.manifest',origin:'platform',processed_name:'shapenet_car',name:'shapenet_car',created_at:'2026-01-01T00:00:00+00:00',selected:false,ref:{asset_id:'same',revision:'v1'}},
   {binding:'train.manifest',origin:'platform',processed_name:'shapenet_car2',name:'shapenet_car2',created_at:'2026-09-15T00:00:00+00:00',selected:false,ref:{asset_id:'other',revision:'v1'}},
   {binding:'train.manifest',origin:'run',run_id:'b8517271xxxx',name:'manifest.json',selected:false,ref:{asset_id:'same',revision:'v1'}},
  ]});
  return route.fulfill({json:[]});
 });
 await page.goto('/');await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(StageWorkbench,{project:'fixture',task:'fixture',stage:'trainprep'}))});
 await page.getByRole('combobox',{name:'train.manifest'}).click();
 const dropdown=page.locator('.ant-select-dropdown:not(.ant-select-dropdown-hidden)');
 await expect(dropdown.getByText('shapenet_car',{exact:true})).toBeVisible();
 await expect(dropdown.getByText('shapenet_car2',{exact:true})).toBeVisible();
 await expect(dropdown.getByText(/b8517271/)).toHaveCount(0);
 await expect(dropdown.locator('.ant-select-item-option')).toHaveCount(2);
 await expect(dropdown.locator('.ant-select-item-option-content')).toHaveText(['shapenet_car2','shapenet_car']);
 await dropdown.getByText('shapenet_car',{exact:true}).click();
 await expect(page.locator('.input-bindings .ant-select-selection-item')).toHaveText('shapenet_car');
 await expect(page.locator('.input-bindings .ant-select-selection-item')).not.toContainText('manifest.json');
 await expect(page.getByLabel('平台数据集名称')).toHaveValue('shapenet_car');
});

test('数据准备字段按模型角色下拉匹配并标出张量形状不符',async({page})=>{
 const values={domains:{surface:{position:'surface_position',features:{},targets:{pressure:'surface_pressure'}}},normalization:{fields:{surface_pressure:{method:'zscore'}}}};
 const matching={source:'configuration',model_roles:[{id:'surface/position',domain:'surface',role:'position',name:'position',shape:['N',3],required:true},{id:'surface/targets/pressure',domain:'surface',role:'targets',name:'pressure',shape:['N',1],required:true}],dataset_fields:[{domain:'surface',name:'surface_position',shape:[3586,3]},{domain:'surface',name:'surface_pressure',shape:[3586,1]}]};
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:'trainprep',values,capabilities:{field_matching:matching}}});
  return route.fulfill({json:[]});
 });
 await page.goto('/');await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(StageWorkbench,{project:'fixture',task:'fixture',stage:'trainprep'}))});
 await expect(page.getByRole('combobox',{name:'surface/targets/pressure',exact:true})).toBeVisible();
 await expect(page.getByText('模型输入',{exact:true})).toBeVisible();
 await expect(page.getByText('数据集字段',{exact:true})).toBeVisible();
 await expect(page.getByText('(N, 3)',{exact:true})).toBeVisible();
 await expect(page.getByText('(N, 1)',{exact:true})).toBeVisible();
 await expect(page.getByText('1维',{exact:true})).toHaveCount(0);
 await expect(page.getByText('3维',{exact:true})).toHaveCount(0);
 await expect(page.locator('.prep-match-ok')).toHaveCount(2);
 await expect(page.getByRole('textbox',{name:'surface/targets/pressure',exact:true})).toHaveCount(0);
 await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'surface/targets/pressure',exact:true})}).click();
 await expect(page.locator('.ant-select-item-option-disabled').filter({hasText:'surface_position'})).toHaveCount(1);
});

test('数据准备分片显示原人数且数量之和须等于全部样本',async({page})=>{
 const values={domains:{surface:{position:'surface_position',features:{},targets:{}}},normalization:{fields:{}}};
 const matching={source:'manifest',model_roles:[],dataset_fields:[]};
 const split={total:3,defaults:{train:2,test:1,eval:0},methods:['original','random'],samples:[{id:'a',partition:'train'},{id:'b',partition:'train'},{id:'c',partition:'test'}]};
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:'trainprep',values,capabilities:{field_matching:matching,split}}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[{binding:'train.manifest',origin:'platform',processed_name:'shapenet_car',name:'shapenet_car',selected:true,ref:{asset_id:'m',revision:'v1'}}]});
  return route.fulfill({json:[]});
 });
 await page.goto('/');await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(StageWorkbench,{project:'fixture',task:'fixture',stage:'trainprep'}))});
 await expect(page.getByLabel('平台数据集名称')).toHaveValue('shapenet_car');
 await expect(page.getByRole('combobox',{name:'执行范围',exact:true})).toBeVisible();
 await expect(page.getByText(/处理样本：\s*3\s*个/)).toBeVisible();
 await expect(page.getByLabel('全部样本数')).toHaveValue('3');
 await expect(page.getByLabel('训练分片数量')).toHaveValue('2');
 await expect(page.getByLabel('测试分片数量')).toHaveValue('1');
 await expect(page.getByLabel('评价分片数量')).toHaveValue('0');
 await expect(page.getByRole('combobox',{name:'抽取方法'})).toBeVisible();
 await page.getByLabel('测试分片数量').fill('0');
 await expect(page.getByRole('alert')).toContainText('三个分片数量之和必须等于全部样本 3');
 await expect(page.getByRole('button',{name:'▶ 执行',exact:true})).toBeDisabled();
 await page.getByLabel('训练分片数量').fill('3');
 await expect(page.getByRole('alert')).toHaveCount(0);
 await expect(page.getByRole('button',{name:'▶ 执行',exact:true})).toBeEnabled();
 await expect(page.getByLabel('分片随机种子')).toBeVisible();
});

test('已完成步骤为绿当前为蓝，失效清单用人话，准备日志完整',async({page})=>{
 const summary={rawprep:{status:'succeeded',run_id:'raw'},trainprep:{status:'not_run'},train:{status:'not_run'},post:{status:'not_run'},model:{status:'unchecked'},training:{status:'unchecked'}};
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname==='/api/v1/projects')return route.fulfill({json:[{id:'p',name:'测试项目'}]});
  if(url.pathname==='/api/v1/projects/p/tasks/t')return route.fulfill({json:{id:'t',name:'测试任务',stage_summary:summary}});
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:url.searchParams.get('stage')||'trainprep',values:{domains:{},normalization:{fields:{}}},capabilities:{field_matching:{model_roles:[],dataset_fields:[]}}}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[{binding:'train.manifest',name:'已绑定来源不可用',selected:false,ref:null,compatibility:{status:'invalid',reason:'path_outside_root'}}]});
  return route.fulfill({json:[]});
 });
 await page.goto('/projects/p/tasks/t/trainprep');
 const done=page.locator('.workbench-steps .topstep.done').first().locator('span');
 const active=page.locator('.workbench-steps .topstep.active span');
 await expect(done).toHaveCSS('background-color','rgb(7, 156, 100)');
 await expect(active).toHaveCSS('background-color','rgb(8, 115, 255)');
 await expect(page.getByText('平台数据集：已绑定来源不可用',{exact:true})).toBeVisible();
 await expect(page.getByText('所选文件不在可访问范围内。',{exact:true})).toBeVisible();
 await expect(page.getByText('train.manifest：已绑定来源不可用',{exact:true})).toHaveCount(0);
 await expect(page.getByText('path_outside_root',{exact:true})).toHaveCount(0);
 await expect(page.getByLabel('搜索日志',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'下载日志',exact:true})).toBeVisible();
 const box=await page.locator('.execution-log').boundingBox();
 expect(box?.height||0).toBeGreaterThan(90);
 await page.getByRole('link',{name:'原始处理 · 运行成功',exact:true}).click();
 await expect(page.locator('.workbench-steps .topstep.active.done span')).toHaveCSS('background-color','rgb(8, 115, 255)');
});

test('数据准备有正式清单时提示先选，不自动勾最新',async({page})=>{
 const summary={rawprep:{status:'succeeded',run_id:'raw'},trainprep:{status:'not_run'},train:{status:'not_run'},post:{status:'not_run'},model:{status:'unchecked'},training:{status:'unchecked'}};
 await page.route('**/api/v1/**',route=>{
  const url=new URL(route.request().url());
  if(url.pathname==='/api/v1/projects')return route.fulfill({json:[{id:'p',name:'测试项目'}]});
  if(url.pathname==='/api/v1/projects/p/tasks/t')return route.fulfill({json:{id:'t',name:'测试任务',stage_summary:summary}});
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:'trainprep',values:{domains:{},normalization:{fields:{}}},capabilities:{field_matching:{model_roles:[],dataset_fields:[]}}}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[{binding:'train.manifest',run_id:'older',name:'manifest.json',selected:false,ref:{asset_id:'a',revision:'r'}},{binding:'train.manifest',run_id:'newer',name:'manifest.json',selected:false,ref:{asset_id:'b',revision:'r'}}]});
  return route.fulfill({json:[]});
 });
 await page.goto('/projects/p/tasks/t/trainprep');
 await expect(page.getByText('有 2 个平台数据集，请选择',{exact:true})).toBeVisible();
 await expect(page.getByText('请从上方选择平台数据集',{exact:true})).toBeVisible();
 await expect(page.getByText('请先选择平台数据集再执行。',{exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'▶ 执行',exact:true})).toBeDisabled();
 await expect(page.getByText('请选择固定输入或运行',{exact:true})).toHaveCount(0);
 await expect(page.getByText('平台数据集：已绑定来源不可用',{exact:true})).toHaveCount(0);
 await expect(page.locator('.input-bindings .ant-select-selection-item')).toHaveCount(0);
 await expect(page.getByLabel('平台数据集名称')).toBeVisible();
 await expect(page.getByRole('combobox',{name:'执行范围',exact:true})).toBeVisible();
 await expect(page.getByText('执行数量',{exact:true})).toHaveCount(0);
 await expect(page.getByText('执行全部',{exact:true})).toHaveCount(0);
 await page.getByRole('tab',{name:'处理结果',exact:true}).click();
 await expect(page.getByText('准备运行完成后在此查看产物',{exact:true})).toBeVisible();
});

test('数据准备树表列与再执行清进度日志叠加',async({page})=>{
 await page.setViewportSize({width:1440,height:900});
 let current={id:'run-1',status:'succeeded',text:'[datapre/批量前处理/进度] 完成=2；总数=2；失败=0；未执行=0'};
 let release!:()=>void;const held=new Promise<void>(resolve=>release=resolve);
 let started=false;
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  if(url.pathname.endsWith('/configuration'))return route.fulfill({json:{revision:'r1',stage:'trainprep',values:{domains:{},normalization:{fields:{surface_position:{method:'coordinate'}}}},capabilities:{field_matching:{model_roles:[],dataset_fields:[]}}}});
  if(url.pathname.endsWith('/stage-inputs'))return route.fulfill({json:[{binding:'train.manifest',origin:'platform',processed_name:'shapenet_car',name:'shapenet_car',selected:true,ref:{asset_id:'m',revision:'v1'}}]});
  if(url.pathname.includes('/stage-files'))return route.fulfill({json:[{name:'field.pt',path:'train/sample/field.pt',root:'project',source_path:'physical/train/sample/field.pt',size:12,modified_at:'2026-09-14T02:30:00Z',ref:{project_id:'fixture',asset_id:'field',revision:'v1'}}]});
  if(url.pathname.endsWith('/stages/trainprep/operations')){started=true;await held;return route.fulfill({json:{id:'run-2',status:'running'}});}
  if(url.pathname.endsWith('/runs'))return route.fulfill({json:started?[{id:'run-2',stages:['trainprep'],operation_mode:'execute',status:'running'}]:[{id:'run-1',stages:['trainprep'],operation_mode:'execute',status:'succeeded'}]});
  if(url.pathname.endsWith('/runs/run-1'))return route.fulfill({json:current});
  if(url.pathname.endsWith('/runs/run-1/log'))return route.fulfill({json:{text:current.text}});
  if(url.pathname.endsWith('/runs/run-2'))return route.fulfill({json:{id:'run-2',status:'running',text:'[datapre/批量前处理/进度] 完成=0；总数=2；失败=0；未执行=2'}});
  if(url.pathname.endsWith('/runs/run-2/log'))return route.fulfill({json:{text:'[datapre/批量前处理/进度] 完成=0；总数=2；失败=0；未执行=2'}});
  return route.fulfill({json:[]});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-1/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify(current)+'\n\n'});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-2/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify({id:'run-2',status:'running',text:'[datapre/批量前处理/进度] 完成=0；总数=2；失败=0；未执行=2'})+'\n\n'});
 });
 await page.goto('/');await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(StageWorkbench,{project:'fixture',task:'fixture',stage:'trainprep'}))});
 await expect(page.getByText('文件名',{exact:true})).toBeVisible();
 await expect(page.getByText('类型',{exact:true})).toBeVisible();
 await expect(page.locator('th.artifact-size')).toBeVisible();
 await expect(page.locator('th.artifact-modified')).toBeAttached();
 await expect(page.getByRole('button',{name:'预览 field.pt'})).toBeVisible();
 await expect(page.getByRole('checkbox',{name:'统一空间 surface_position'})).toBeChecked();
 await expect(page.locator('.ant-select').filter({has:page.getByLabel('归一化方法 surface_position')}).locator('.ant-select-selection-item')).toHaveText(/最小最大/);
 await expect(page.getByLabel('处理进度')).toContainText('已完成');
 await page.getByRole('button',{name:'▶ 执行',exact:true}).click();
 await expect(page.getByLabel('处理进度')).toHaveCount(0);
 await expect(page.getByLabel('运行日志内容')).toContainText('完成=2');
 release();
 await expect(page.getByLabel('处理进度')).toBeVisible();
 await expect(page.getByLabel('处理进度')).not.toContainText('已完成');
 await expect(page.getByLabel('运行日志内容')).toContainText('完成=2');
});
