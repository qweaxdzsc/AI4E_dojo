import {test,expect} from '@playwright/test';

function snapshot(status:string,done:number,total:number){
 return {id:'run-1',status,text:`[datapre/批量前处理/进度] 完成=${done}；总数=${total}；失败=0；未执行=${Math.max(total-done,0)}`};
}

/** 原始处理夹具：公开数据集绑定取消、结果树、正式执行进度条。 */
test('公开数据集绑定取消、结果树预览下载与正式进度',async({page})=>{
 page.setDefaultTimeout(15000);const saves:any[]=[];let revision='r1';let processedName='';
 const files=[{name:'field.pt',path:'train/sample/field.pt',root:'project',source_path:'physical/train/sample/field.pt',size:12,modified_at:'2026-09-14T02:30:00Z',ref:{project_id:'fixture',asset_id:'field',revision:'v1'}}];
 let current=snapshot('running',1,2);let runs:any[]=[];
 await page.route('**/api/v1/**',async route=>{
  const req=route.request(),url=new URL(req.url());
  let value:any=[];
  if(url.pathname.endsWith('/capabilities'))value={output_formats:['pt','zarr'],additional_outputs:['vtkhdf']};
  else if(url.pathname==='/api/v1/datasets')value=[];
  else if(url.pathname.endsWith('/datasets'))value={revision,current_dataset_id:'shapenet_car',model_id:'abupt',datasets:[{dataset_id:'shapenet_car',label:'ShapeNet-Car',description:'按 ShapeNet-Car 声明读取样本目录',binding_mode:'directory',compatible:true,instances:[{id:'copy-a',label:'data0 / cars',sources:{root:{root:'data0',path:'cars'}}}]}]};
  else if(url.pathname.endsWith('/dataset')){if(req.method()==='PUT'){saves.push(req.postDataJSON());revision='r3';}value={revision,dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};}
  else if(url.pathname.endsWith('/rawprep')){if(req.method()==='PUT'){const body=req.postDataJSON();saves.push(body);revision='r2';if(body.processed_name)processedName=body.processed_name;}const body=req.method()==='PUT'?req.postDataJSON():{};const formats=body.rawprep?.formats||(body.rawprep?.format?[body.rawprep.format]:['zarr']);const vtkhdf=body.rawprep?.vtkhdf!==undefined?body.rawprep.vtkhdf:true;value={revision,processed_name:processedName,profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{format:'zarr',geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:true}},rawprep:{format:formats[0],formats,geometry:{},filters:{},statistics:{mode:'none'},vtkhdf,sources:[]}};}
  else if(url.pathname.endsWith('/preflight'))value={sample_count:1,file_count:1};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'a'}],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/rawprep/execute')){runs=[{id:'run-1',stages:['rawprep'],operation_mode:'execute',status:'running'}];value={id:'run-1',status:'running'};}
  else if(url.pathname.endsWith('/rawprep/trial')){runs=[{id:'trial-1',stages:['rawprep'],operation_mode:'trial',status:'running'}];value={id:'trial-1',status:'running'};}
  else if(url.pathname.endsWith('/runs'))value=runs;
  else if(url.pathname.endsWith('/runs/run-1'))value=current;
  else if(url.pathname.endsWith('/runs/run-1/log'))value={text:current.text};
  else if(url.pathname.endsWith('/runs/trial-1'))value={id:'trial-1',status:'running',text:'[INFO] 试跑已开始'};
  else if(url.pathname.endsWith('/runs/trial-1/log'))value={text:'[INFO] 试跑已开始'};
  else if(url.pathname.includes('/stage-files')){const path=url.searchParams.get('path')||'';value=path==='train'?[{name:'sample',path:'train/sample',root:'project',source_path:'physical/train/sample',directory:true}]:path==='train/sample'?[{name:'field.pt',path:'train/sample/field.pt',root:'project',source_path:'physical/train/sample/field.pt',directory:false,size:12,modified_at:'2026-09-14T02:30:00Z'}]:[{name:'train',path:'train',root:'project',source_path:'physical/train',directory:true}];}
  else if(url.pathname.endsWith('/files'))value=url.searchParams.get('path')==='cars'?[{name:'surface.vtk',path:'cars/surface.vtk',directory:false,size:123,modified_at:'2026-09-14T01:02:00Z'}]:[{name:'cars',path:'cars',directory:true}];
  await route.fulfill({json:value});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-1/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify(current)+'\n\n'});
 });
 await page.route('**/api/v1/projects/fixture/runs/trial-1/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify({id:'trial-1',status:'running',text:'[INFO] 试跑已开始'})+'\n\n'});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByRole('searchbox',{name:'搜索绑定文件',exact:true})).toBeVisible();
 await expect(page.getByLabel('处理进度')).toHaveCount(0);
 await expect(page.getByText('处理中',{exact:true})).toHaveCount(0);
 await expect(page.getByRole('checkbox',{name:'VTKHDF · 网格与场关联'})).toBeChecked();
 await expect(page.getByRole('spinbutton',{name:'并行线程'})).toHaveValue('1');
 await page.getByRole('spinbutton',{name:'并行线程'}).fill('4');
 await expect(page.getByRole('spinbutton',{name:'并行线程'})).toHaveValue('4');
 await page.getByRole('combobox',{name:'执行范围',exact:true}).press('ArrowDown');
 await expect(page.locator('.ant-select-item-option').filter({hasText:'全部声明样本'})).toBeVisible();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'指定样本'})).toBeVisible();
 await expect(page.locator('.ant-select-item-option').filter({hasText:'选择分片'})).toHaveCount(0);
 await page.keyboard.press('Escape');
 await expect(page.getByRole('button',{name:'配置数据来源',exact:true})).toBeVisible();
 await page.getByRole('button',{name:'配置数据来源'}).click();
 const dialog=page.getByRole('dialog',{name:'选择公开数据集'});
 await expect(dialog.getByRole('button',{name:/ShapeNet-Car/})).toBeVisible();
 await dialog.getByRole('button',{name:/取\s*消/}).click();
 expect(saves.filter((item:any)=>item.dataset_id||item.instance_id)).toHaveLength(0);
 await page.getByRole('tab',{name:'处理结果',exact:true}).click();
 await expect(page.getByRole('combobox',{name:'平台数据集',exact:true})).toBeVisible();
 await expect(page.getByText('请选择固定输入或运行',{exact:true})).toBeVisible();
 await page.getByRole('tab',{name:'原始数据处理',exact:true}).click();
 await page.getByRole('button',{name:'校验输入与配置'}).click();
 await expect(page.getByLabel('处理进度')).toContainText(/校验中|校验通过/);
 await expect(page.getByLabel('运行日志内容')).toContainText('校验');
 await expect(page.getByText('校验通过：1 个完整样本，1 个依赖文件',{exact:true})).toBeVisible();
 await expect(page.getByLabel('处理进度')).toContainText('校验通过');
 await page.getByRole('button',{name:'刷新样本与字段'}).click();
 await expect(page.getByLabel('处理进度')).toContainText(/刷新中|已刷新/);
 await expect(page.getByLabel('运行日志内容')).toContainText('刷新');
 await page.getByRole('button',{name:'按所选范围试跑'}).click();
 await expect(page.getByLabel('处理进度')).toContainText(/试跑中|试跑完成/);
 await expect(page.getByLabel('运行日志内容')).toContainText('试跑');
 await page.getByRole('button',{name:'执行',exact:true}).click();
 expect(saves.some((item:any)=>item.processed_name==='shapenet_car')).toBeTruthy();
 await expect(page.getByLabel('处理进度')).toBeVisible();
 await expect(page.getByLabel('处理进度')).toContainText('处理中 1/2');
 await expect(page.getByLabel('运行日志内容')).toContainText('已提交运行');
 await expect(page.getByLabel('运行日志内容')).not.toContainText('—— 操作 ——');
 await page.getByRole('tab',{name:'处理结果',exact:true}).click();
 await expect(page.getByRole('button',{name:'train',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'预览 field.pt'})).toHaveCount(0);
 await page.getByRole('button',{name:'train',exact:true}).click();
 await expect(page.locator('.folderrow.selected')).toHaveCount(0);
 await page.getByRole('button',{name:'sample',exact:true}).click();
 await expect(page.locator('.folderrow.selected')).toHaveCount(0);
 await expect(page.getByRole('button',{name:'预览 field.pt'})).toBeVisible();
 await expect(page.getByRole('link',{name:'下载'})).toHaveAttribute('href','/api/v1/projects/fixture/files/download?root=project&path=physical%2Ftrain%2Fsample%2Ffield.pt&task_id=task');
});

test('刷新后仍显示最近一次正式执行终态',async({page})=>{
 page.setDefaultTimeout(15000);
 const current=snapshot('succeeded',2,2);
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{}},rawprep:{format:'zarr',geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:[]}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/runs'))value=[{id:'run-1',stages:['rawprep'],operation_mode:'execute',status:'succeeded'}];
  else if(url.pathname.endsWith('/runs/run-1'))value=current;
  else if(url.pathname.endsWith('/runs/run-1/log'))value={text:current.text};
  else if(url.pathname.includes('/stage-files'))value=[];
  else if(url.pathname.endsWith('/files'))value=[];
  await route.fulfill({json:value});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-1/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify(current)+'\n\n'});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByLabel('处理进度')).toContainText('已完成');
 await expect(page.getByRole('progressbar')).toHaveAttribute('aria-valuenow','100');
});

test('再执行立刻清进度且日志叠加',async({page})=>{
 page.setDefaultTimeout(15000);
 let current=snapshot('succeeded',2,2);
 let release!:()=>void;const held=new Promise<void>(resolve=>release=resolve);
 let started=false;
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{}},rawprep:{format:'pt',geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:[]}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'a'}],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/rawprep/execute')){started=true;await held;value={id:'run-2',status:'running'};}
  else if(url.pathname.endsWith('/runs'))value=started?[{id:'run-2',stages:['rawprep'],operation_mode:'execute',status:'running'}]:[{id:'run-1',stages:['rawprep'],operation_mode:'execute',status:'succeeded'}];
  else if(url.pathname.endsWith('/runs/run-1'))value=current;
  else if(url.pathname.endsWith('/runs/run-1/log'))value={text:current.text};
  else if(url.pathname.endsWith('/runs/run-2'))value=snapshot('running',0,2);
  else if(url.pathname.endsWith('/runs/run-2/log'))value={text:snapshot('running',0,2).text};
  else if(url.pathname.includes('/stage-files'))value=[];
  else if(url.pathname.endsWith('/files'))value=[];
  await route.fulfill({json:value});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-1/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify(current)+'\n\n'});
 });
 await page.route('**/api/v1/projects/fixture/runs/run-2/events',async route=>{
  await route.fulfill({status:200,contentType:'text/event-stream',body:'id: 1\ndata: '+JSON.stringify(snapshot('running',0,2))+'\n\n'});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByLabel('处理进度')).toContainText('已完成');
 await expect(page.getByLabel('运行日志内容')).toContainText('完成=2');
 await page.getByRole('button',{name:'执行',exact:true}).click();
 await expect(page.getByLabel('处理进度')).toBeVisible();
 await expect(page.getByText('已完成',{exact:true})).toHaveCount(0);
 await expect(page.getByLabel('处理进度')).toContainText('处理中');
 await expect(page.getByLabel('运行日志内容')).toContainText('完成=2');
 release();
 await expect(page.getByLabel('处理进度')).toBeVisible();
 await expect(page.getByLabel('处理进度')).not.toContainText('已完成');
 await expect(page.getByLabel('运行日志内容')).toContainText('下一次运行');
 await expect(page.getByLabel('运行日志内容')).toContainText('完成=2');
});

test('处理结果可选择已登记平台数据集且不自动勾最新',async({page})=>{
 page.setDefaultTimeout(15000);
 const files=[{name:'field.pt',path:'train/sample/field.pt',root:'project',source_path:'physical/train/sample/field.pt',directory:false,size:12,modified_at:'2026-09-14T02:30:00Z'}];
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',processed_name:'shapenet_car',profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{}},rawprep:{format:'pt',geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:false,sources:[]}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/stage-inputs'))value=[
   {binding:'inputs.trainprep.dataset',origin:'platform',processed_name:'shapenet_car2',name:'shapenet_car2',created_at:'2026-09-15T08:00:00Z',ref:{asset_id:'ds-2',revision:'v2'},compatibility:{status:'unchecked'}},
   {binding:'inputs.trainprep.dataset',origin:'platform',processed_name:'shapenet_car',name:'shapenet_car',created_at:'2026-09-15T07:00:00Z',ref:{asset_id:'ds-1',revision:'v1'},compatibility:{status:'unchecked'}},
  ];
  else if(url.pathname.includes('/stage-files'))value=url.searchParams.get('asset_id')==='ds-2'?[{name:'train',path:'train',root:'project',source_path:'physical/train',directory:true}]:url.searchParams.get('path')==='train'?files:url.searchParams.get('asset_id')==='ds-1'?[]:[];
  else if(url.pathname.endsWith('/runs'))value=[];
  else if(url.pathname.endsWith('/files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await page.getByRole('tab',{name:'处理结果',exact:true}).click();
 await expect(page.getByRole('combobox',{name:'平台数据集',exact:true})).toBeVisible();
 await expect(page.locator('.ant-empty-description')).toHaveText('有 2 个平台数据集，请选择');
 await expect(page.getByRole('button',{name:'train',exact:true})).toHaveCount(0);
 await page.getByRole('combobox',{name:'平台数据集',exact:true}).click();
 await page.locator('.ant-select-item-option').filter({hasText:'shapenet_car2'}).click({force:true});
 await expect(page.getByRole('button',{name:'train',exact:true})).toBeVisible();
});

test('同名已存在时询问覆盖并带标记提交',async({page})=>{
 page.setDefaultTimeout(15000);
 const executes:any[]=[];
 await page.route('**/api/v1/**',async route=>{
  const req=route.request(),url=new URL(req.url());
  let value:any=[];
  if(url.pathname.endsWith('/capabilities'))value={output_formats:['pt','zarr'],additional_outputs:['vtkhdf']};
  else if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r2',processed_name:'shapenet_car',processed_name_status:{status:'conflict',message:'已有登记 VTKHDF=关，当前配置 VTKHDF=开。确认后将覆盖原登记。'},profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{format:'zarr',geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:true}},rawprep:{format:'pt',formats:['pt'],geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:true,sources:[]}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'a'}],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/rawprep/execute')){executes.push(req.postDataJSON());value={id:'run-1',status:'running'};}
  else if(url.pathname.endsWith('/runs'))value=executes.length?[{id:'run-1',stages:['rawprep'],operation_mode:'execute',status:'running'}]:[];
  else if(url.pathname.endsWith('/runs/run-1'))value={id:'run-1',status:'running',text:'[INFO] 已提交运行 run-1'};
  else if(url.pathname.endsWith('/runs/run-1/log'))value={text:'[INFO] 已提交运行 run-1'};
  else if(url.pathname.endsWith('/files'))value=[];
  else if(url.pathname.includes('/stage-files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByText('确认后将覆盖原登记。')).toBeVisible();
 await page.getByRole('button',{name:'执行',exact:true}).click();
 const dialog=page.getByRole('dialog',{name:'覆盖已有共享数据集？'});
 await expect(dialog).toBeVisible();
 await dialog.getByRole('button',{name:'覆盖并执行'}).click();
 await expect.poll(()=>executes.length).toBe(1);
 expect(executes[0].overwrite_processed_name).toBe(true);
});

test('进页先出三栏与配置，慢的文件树和运行名单不挡住',async({page})=>{
 page.setDefaultTimeout(15000);
 let finishCfg!:(value:unknown)=>void,finishFiles!:(value:unknown)=>void,finishRuns!:(value:unknown)=>void,finishCatalog!:(value:unknown)=>void,finishInputs!:(value:unknown)=>void;
 const cfg=new Promise(resolve=>{finishCfg=resolve;});
 const files=new Promise(resolve=>{finishFiles=resolve;});
 const runs=new Promise(resolve=>{finishRuns=resolve;});
 const catalog=new Promise(resolve=>{finishCatalog=resolve;});
 const inputs=new Promise(resolve=>{finishInputs=resolve;});
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep')&&!url.pathname.includes('/catalog')){await cfg;value={revision:'r1',processed_name:'shapenet_car',profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{}},rawprep:{format:'zarr',formats:['zarr'],geometry:{},filters:{},statistics:{mode:'none'},vtkhdf:true,sources:[]}};}
  else if(url.pathname.endsWith('/rawprep/catalog')){await catalog;value={revision:'cat',samples:[{key:'train::a',partition:'train',sample_id:'a'}],fields:[],sources:[],errors:[]};}
  else if(url.pathname.endsWith('/runs')){await runs;value=[];}
  else if(url.pathname.endsWith('/files')){await files;value=[{name:'surface.vtk',path:'cars/surface.vtk',directory:false,size:123,modified_at:'2026-09-14T01:02:00Z'}];}
  else if(url.pathname.endsWith('/stage-inputs')){await inputs;value=[{binding:'inputs.trainprep.dataset',origin:'platform',processed_name:'shapenet_car2',name:'shapenet_car2',created_at:'2026-09-15T08:00:00Z',ref:{asset_id:'ds-2',revision:'v2'},compatibility:{status:'unchecked'}}];}
  else if(url.pathname.includes('/stage-files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.locator('.workbench-grid.layout')).toBeVisible({timeout:2000});
 await expect(page.getByText('处理设置',{exact:true})).toBeVisible();
 await expect(page.getByRole('heading',{name:'执行配置'})).toBeVisible();
 await expect(page.getByRole('tab',{name:'原始数据处理',exact:true})).toBeVisible();
 await expect(page.getByLabel('处理设置加载中')).toBeVisible();
 await expect(page.getByRole('checkbox',{name:'VTKHDF · 网格与场关联'})).toHaveCount(0);
 finishCfg(null);
 await expect(page.getByRole('checkbox',{name:'VTKHDF · 网格与场关联'})).toBeChecked();
 await expect(page.getByLabel('绑定文件加载中')).toBeVisible();
 await expect(page.getByRole('button',{name:'预览 surface.vtk'})).toHaveCount(0);
 finishFiles(null);
 await expect(page.getByRole('button',{name:'预览 surface.vtk'})).toBeVisible();
 await page.getByRole('tab',{name:'处理结果',exact:true}).click();
 await expect(page.getByRole('combobox',{name:'平台数据集',exact:true})).toBeVisible();
 await expect(page.getByLabel('处理结果加载中')).toBeVisible();
 finishInputs(null);
 await expect(page.locator('.ant-empty-description')).toHaveText('有 1 个平台数据集，请选择');
 finishCatalog(null);
 finishRuns(null);
});

test('已接入数据集缺 VTKHDF 键时默认勾选',async({page})=>{
 page.setDefaultTimeout(15000);
 await page.route('**/api/v1/**',async route=>{
  const url=new URL(route.request().url());
  let value:any=[];
  if(url.pathname.endsWith('/dataset'))value={revision:'r1',dataset_id:'shapenet_car',label:'ShapeNet-Car',status:'valid',location:'root：data0 / cars',sources:{root:{root:'data0',path:'cars'}},errors:[],binding_schema:{mode:'directory',root_key:'root',description:'按 ShapeNet-Car 声明读取样本目录',slots:[{key:'root',label:'ShapeNet 数据目录',kind:'directory'}]}};
  else if(url.pathname.endsWith('/rawprep'))value={revision:'r1',profile:{dataset_id:'shapenet_car',outputs:[],geometry:[],filters:[],formats:['pt','zarr'],vtkhdf:true,statistics_modes:['none'],defaults:{vtkhdf:true}},rawprep:{format:'pt',formats:['pt'],geometry:{},filters:{},statistics:{mode:'none'},sources:[]}};
  else if(url.pathname.endsWith('/rawprep/catalog'))value={revision:'cat',samples:[],fields:[],sources:[],errors:[]};
  else if(url.pathname.endsWith('/runs'))value=[];
  else if(url.pathname.includes('/stage-files')||url.pathname.endsWith('/files'))value=[];
  await route.fulfill({json:value});
 });
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {RawprepWorkbench}=await import('/src/modules/rawprep/RawprepWorkbench.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';createRoot(document.getElementById('fixture')).render(React.createElement(RawprepWorkbench,{project:'fixture',task:'task'}));});
 await expect(page.getByRole('checkbox',{name:'VTKHDF · 网格与场关联'})).toBeChecked();
});
