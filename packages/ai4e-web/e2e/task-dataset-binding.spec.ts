import {test,expect} from '@playwright/test';
const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
const caseLabel=(c:{dataset_id:string;model_id:string})=>`数据集 ${c.dataset_id==='nasa_crm'?'NASA CRM':'ShapeNet-Car'} · 模型 ${c.model_id==='abupt'?'AB-UPT':'Transolver-3'}`;
async function enterProject(page:any,name:string,id:string){
  await page.goto('/projects');
  await page.getByRole('textbox',{name:'搜索项目',exact:true}).fill(name);
  await page.locator('.taskcard').filter({hasText:name}).getByRole('link',{name:'进入项目',exact:true}).click();
  await expect(page).toHaveURL(new RegExp(`/projects/${id}/tasks$`));
}
async function openTaskList(page:any,project:string){
  if(!new RegExp(`/projects/${project}/tasks$`).test(page.url()))await page.getByRole('link',{name:'返回任务管理',exact:true}).click();
  await expect(page).toHaveURL(new RegExp(`/projects/${project}/tasks$`));
}

/** 创建只表达案例；绑定在原始处理经真实受控浏览完成，结束后归档确切项目。 */
test('四案例简洁创建、工作台绑定与派生继承',async({page,request})=>{
 test.setTimeout(180000);page.setDefaultTimeout(15000);
 const name='四案例绑定验收 '+Date.now();
 const made=await request.post(api+'/projects',{data:{name}});expect(made.ok()).toBeTruthy();const p=(await made.json()).id;
 try{
  const cases=await(await request.get(`${api}/projects/${p}/tasks/cases`)).json();expect(cases).toHaveLength(4);
  const ids:string[]=[];
  await enterProject(page,name,p);
  for(const c of cases){
   await openTaskList(page,p);await page.getByRole('button',{name:'新建任务',exact:true}).click();const dialog=page.getByRole('dialog',{name:'新建任务',exact:true});
   await dialog.getByLabel('任务名称',{exact:true}).fill(c.name);await dialog.getByRole('button',{name:'创建并进入原始处理',exact:true}).click();await expect(dialog.getByText('请选择科研案例',{exact:true})).toBeVisible();
   await dialog.getByRole('combobox',{name:'科研案例',exact:true}).click();await expect(page.getByRole('option')).toHaveCount(4);await page.getByRole('option',{name:caseLabel(c),exact:true}).click();
   await expect(dialog.getByText('数据源',{exact:true})).toHaveCount(0);await expect(dialog.getByRole('textbox')).toHaveCount(2);
   const submitted=page.waitForResponse(r=>r.url().endsWith(`/projects/${p}/tasks`)&&r.request().method()==='POST');await dialog.getByRole('button',{name:'创建并进入原始处理',exact:true}).click();const response=await submitted;expect(response.ok()).toBeTruthy();expect(response.request().postDataJSON()).toEqual({name:c.name,description:'',case_id:c.id});const t=(await response.json()).id;ids.push(t);
   await expect(page).toHaveURL(new RegExp(`/projects/${p}/tasks/${t}/1$`));await expect(page.getByText('尚未绑定数据',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'开始处理',exact:true})).toBeDisabled();
   await page.getByRole('button',{name:'配置数据来源',exact:true}).click();const binding=page.getByRole('dialog',{name:'配置数据来源',exact:true});
   const pick=async(label:string,root:string,directory:string|undefined,file?:string)=>{await binding.getByRole('button',{name:'浏览'+label,exact:true}).click();const picker=page.getByRole('dialog',{name:'选择'+label,exact:true});await expect(picker.locator('.binding-picker-list')).toBeVisible();if(!(await picker.locator('.ant-select-selection-item').textContent())?.startsWith(root+' · ')){await picker.locator('.ant-select-selector').click();await page.getByRole('option').filter({hasText:root+' · '}).click({force:true});}if(directory)await picker.getByRole('button',{name:'▸ '+directory,exact:true}).click();await picker.getByRole('button',{name:file?'选择文件 '+file:'使用当前目录',exact:true}).click()};
   if(c.dataset_id==='shapenet_car'){await expect(binding.getByText('NASA 训练文件')).toHaveCount(0);await pick('ShapeNet 数据目录','data0',undefined)}
   else{expect(c.dataset_id).toBe('nasa_crm');await expect(binding.getByText('ShapeNet 数据目录')).toHaveCount(0);await pick('NASA 训练文件','data3','Case 4 - NASA CRM 2','trainingData_NASA-CRM.h5');await pick('NASA 测试文件','data3','Case 4 - NASA CRM','testData_NASA-CRM.h5');await pick('NASA 拓扑文件','data3','Case 4 - NASA CRM','connectivity_NASA-CRM.h5')}
   const saved=page.waitForResponse(r=>r.url().endsWith(`/tasks/${t}/dataset`)&&r.request().method()==='PUT');await binding.getByRole('button',{name:'保存数据绑定',exact:true}).click();const saveResponse=await saved;expect(saveResponse.ok()).toBeTruthy();const before=await saveResponse.json();expect(before.status).toBe('valid');
   await expect(page.getByText('数据绑定已保存，请重新选择处理文件',{exact:true})).toBeVisible();await expect(page.getByRole('button',{name:'开始处理',exact:true})).toBeDisabled();await page.reload();await expect(page.getByText('数据来源已绑定',{exact:true})).toBeVisible();const after=await(await request.get(`${api}/projects/${p}/tasks/${t}/dataset`)).json();expect(after.sources).toEqual(before.sources);
   if(c.dataset_id==='nasa_crm'){expect(Object.keys(after.sources)).toHaveLength(3);await expect(page.locator('.bound-dataset-files').getByRole('checkbox')).toHaveCount(3);await expect(page.locator('.bound-dataset-files').getByRole('checkbox').first()).not.toBeChecked()}
   await page.locator('.bound-dataset-files').getByRole('tab',{name:'处理结果',exact:true}).click();await expect(page.getByRole('combobox',{name:'文件范围',exact:true})).toBeVisible();
  }
  const source=ids[0],before=await(await request.get(`${api}/projects/${p}/tasks/${source}/configuration`)).json();await openTaskList(page,p);const row=page.locator('.tasktable tbody tr').filter({has:page.locator(`a.enter-workbench[href="/projects/${p}/tasks/${source}/1"]`)});await row.getByRole('button',{name:/更多操作$/}).click();await page.getByRole('menuitem',{name:'派生任务',exact:true}).click();const dialog=page.getByRole('dialog',{name:'派生任务',exact:true});await expect(dialog.getByRole('combobox')).toHaveCount(0);await dialog.getByLabel('任务名称',{exact:true}).fill('继承绑定案例');const forked=page.waitForResponse(r=>r.url().endsWith(`/tasks/${source}/fork`)&&r.request().method()==='POST');await dialog.getByRole('button',{name:'派生并进入原始处理',exact:true}).click();const child=await(await forked).json();await expect(page).toHaveURL(new RegExp(`/tasks/${child.id}/1$`));const inherited=await(await request.get(`${api}/projects/${p}/tasks/${child.id}/configuration`)).json();expect(inherited.config.components).toEqual(before.config.components);expect(inherited.config.dataset).toEqual(before.config.dataset);
 }finally{await request.patch(`${api}/projects/${p}`,{data:{archived:true}})}
});

test('新建弹窗校验、案例重试与约定尺寸',async({page,request})=>{
 const name='弹窗验收 '+Date.now();
 const made=await request.post(api+'/projects',{data:{name}});expect(made.ok()).toBeTruthy();const p=(await made.json()).id;
 let failCases=true;
 await page.route(`**/projects/${p}/tasks/cases`,async route=>{
  if(failCases){await route.fulfill({status:500,contentType:'application/json',body:JSON.stringify({detail:'案例列表不可用'})});return}
  await route.continue();
 });
 try{
  await enterProject(page,name,p);
  await page.getByRole('button',{name:'新建任务',exact:true}).click();
  const dialog=page.getByRole('dialog',{name:'新建任务',exact:true});
  await expect(dialog.getByText('案例列表不可用',{exact:true})).toBeVisible();
  await expect(dialog.getByRole('button',{name:'创建并进入原始处理',exact:true})).toBeDisabled();
  failCases=false;
  await dialog.getByRole('button',{name:'重试加载案例',exact:true}).click();
  await expect(dialog.getByRole('combobox',{name:'科研案例',exact:true})).toBeVisible();
  await dialog.getByRole('button',{name:'创建并进入原始处理',exact:true}).click();
  await expect(dialog.getByText('请填写任务名称',{exact:true})).toBeVisible();
  await dialog.getByLabel('任务名称',{exact:true}).fill('保留的草稿');
  await dialog.getByRole('button',{name:'创建并进入原始处理',exact:true}).click();
  await expect(dialog.getByText('请选择科研案例',{exact:true})).toBeVisible();
  await expect(dialog.getByLabel('任务名称',{exact:true})).toHaveValue('保留的草稿');
  const nameLabel=dialog.locator('label[for="task-name-input"]'),nameInput=dialog.locator('#task-name-input'),caseLabelEl=dialog.locator('label[for="task-case-select"]');
  const nameBox=await nameLabel.boundingBox(),inputBox=await nameInput.boundingBox(),caseBox=await caseLabelEl.boundingBox(),modalBox=await page.locator('.task-form-dialog .ant-modal').boundingBox();
  expect(nameBox&&inputBox&&caseBox&&modalBox).toBeTruthy();
  expect(Math.abs((inputBox!.y)-(nameBox!.y+nameBox!.height)-6)).toBeLessThanOrEqual(1);
  expect(Math.abs(caseBox!.y-(inputBox!.y+inputBox!.height)-16)).toBeLessThanOrEqual(1);
  expect(Math.abs(inputBox!.height-36)).toBeLessThanOrEqual(1);
  expect(Math.abs(modalBox!.width-520)).toBeLessThanOrEqual(1);
  await dialog.getByRole('button',{name:/取\s*消/}).click();
  await page.getByRole('button',{name:'新建任务',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'新建任务',exact:true}).getByLabel('任务名称',{exact:true})).toHaveValue('');
  await page.setViewportSize({width:400,height:800});
  const narrow=page.getByRole('dialog',{name:'新建任务',exact:true});
  const narrowModal=await page.locator('.task-form-dialog .ant-modal').boundingBox();
  expect(narrowModal).toBeTruthy();
  expect(Math.abs(narrowModal!.x-24)).toBeLessThanOrEqual(1);
  expect(Math.abs(400-narrowModal!.x-narrowModal!.width-24)).toBeLessThanOrEqual(1);
  expect(['auto','scroll']).toContain(await page.locator('.task-form-dialog .ant-modal-body').evaluate(el=>getComputedStyle(el).overflowY));
  await narrow.getByRole('button',{name:/取\s*消/}).click();
  await page.setViewportSize({width:1440,height:1000});
  await page.goto('/projects');
  await page.getByRole('button',{name:'新建项目',exact:true}).click();
  await expect(page.getByRole('dialog',{name:'新建项目',exact:true})).toBeVisible();
  await expect(page.locator('.task-form-dialog')).toHaveCount(0);
  await page.keyboard.press('Escape');
  await enterProject(page,name,p);
  await page.getByRole('button',{name:'新建任务',exact:true}).click();
  const again=page.getByRole('dialog',{name:'新建任务',exact:true});
  await again.getByLabel('任务名称',{exact:true}).fill('重复提交');
  await again.getByRole('combobox',{name:'科研案例',exact:true}).click();
  await page.getByRole('option').first().click();
  const posts:string[]=[];
  page.on('request',req=>{if(req.method()==='POST'&&req.url().endsWith(`/projects/${p}/tasks`))posts.push(req.url())});
  const submitted=page.waitForResponse(r=>r.url().endsWith(`/projects/${p}/tasks`)&&r.request().method()==='POST');
  const submit=again.getByRole('button',{name:'创建并进入原始处理',exact:true});
  await submit.click();await expect(submit).toBeDisabled();await submit.click({force:true});
  expect((await submitted).ok()).toBeTruthy();
  await expect(page).toHaveURL(new RegExp(`/projects/${p}/tasks/.+/1$`));
  expect(posts).toHaveLength(1);
 }finally{await request.patch(`${api}/projects/${p}`,{data:{archived:true}})}
});

/** 同样五个真实任务，对照原型主表、表头、行、进度及工具栏，不靠截图判定。 */
test('任务表在1440和1920下与原型关键尺寸相差不超过1px',async({browser,request},info)=>{
 const p=(await(await request.post(api+'/projects',{data:{name:'任务表几何验收 '+Date.now()}})).json()).id;
 const actual=await browser.newPage(),reference=await browser.newPage();const records:any[]=[];
 try{
  const cases=await(await request.get(`${api}/projects/${p}/tasks/cases`)).json();
  for(let i=0;i<5;i++){const created=await request.post(`${api}/projects/${p}/tasks`,{data:{name:'表格实际任务 '+(i+1),case_id:cases[0].id}});expect(created.ok()).toBeTruthy()}
  for(const width of [1440,1920]){
   await actual.setViewportSize({width,height:1000});await reference.setViewportSize({width,height:1000});
   await reference.goto('file://'+process.cwd()+'/../../docs/prototypes/dojo-web-integrated.html#project/0');await expect(reference.locator('.tasktable')).toBeVisible();await actual.goto((process.env.DOJO_WEB_URL||'http://127.0.0.1:5174')+`/projects/${p}/tasks`);await expect(actual.locator('.ministeps')).toHaveCount(5);
   const measure=(page:typeof actual)=>page.evaluate(()=>Object.fromEntries(['.projecttabs','.tasktoolbar','.taskpanel','.tasktable','.tasktable thead tr','.tasktable tbody tr:first-child','.progresscell','.ministeps'].map(selector=>{const r=document.querySelector(selector)!.getBoundingClientRect();return[selector,{x:r.x,y:r.y,width:r.width,height:r.height}]})));
   const expected=await measure(reference),current=await measure(actual);records.push({width,expected:structuredClone(expected),current,approved_difference:"进度行左右12px，原型左侧100px；ministeps左移88px且增加88px宽度"});expected[".ministeps"].x-=88;expected[".ministeps"].width+=88;
   for(const key of Object.keys(expected))for(const axis of ['x','y','width','height']as const)expect(Math.abs(current[key][axis]-expected[key][axis]),`${width} ${key} ${axis}`).toBeLessThanOrEqual(1);
   await actual.screenshot({path:info.outputPath(`tasktable-${width}.png`),fullPage:true});
  }
  await info.attach('tasktable-geometry',{body:JSON.stringify(records,null,2),contentType:'application/json'});
 }finally{await actual.close();await reference.close();await request.patch(`${api}/projects/${p}`,{data:{archived:true}})}
});
