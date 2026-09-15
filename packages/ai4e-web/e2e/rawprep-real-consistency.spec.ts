import {test,expect} from '@playwright/test';
const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
/** 真实受控文件与现有案例，不拦截 API，不生成示例科研产物。 */
for(const scenario of [{case:'shapenet_car_abupt',format:'pt'},{case:'nasa_crm_transolver3',format:'zarr'}])test(`真实页面配置执行与固定产物预览 ${scenario.case} ${scenario.format}`,async({page,request},info)=>{
 test.setTimeout(240000);page.setDefaultTimeout(20000);
 const name='一致性真实交接 '+scenario.case+' '+Date.now();const p=(await(await request.post(api+'/projects',{data:{name}})).json()).id;
 try{
 const created=await request.post(`${api}/projects/${p}/tasks`,{data:{name:scenario.case,case_id:scenario.case}});expect(created.ok()).toBeTruthy();const t=(await created.json()).id;const base=`${api}/projects/${p}/tasks/${t}`;
 const binding=await(await request.get(base+'/dataset')).json();const nasa=scenario.case.startsWith('nasa');
 const sources=nasa?{train_h5:{root:'data3',path:'Case 4 - NASA CRM 2/trainingData_NASA-CRM.h5'},test_h5:{root:'data3',path:'Case 4 - NASA CRM/testData_NASA-CRM.h5'},connectivity_h5:{root:'data3',path:'Case 4 - NASA CRM/connectivity_NASA-CRM.h5'}}:{root:{root:'data0',path:''}};
 const bound=await request.put(base+'/dataset',{data:{expected_revision:binding.revision,sources}});expect(bound.ok()).toBeTruthy();
 await page.goto('/projects');await page.getByRole('textbox',{name:'搜索项目',exact:true}).fill(name);await page.locator('.taskcard').filter({hasText:name}).getByRole('link',{name:'进入项目',exact:true}).click();await page.getByRole('link',{name:'进入工作台',exact:true}).click();
 await expect(page.getByRole('searchbox',{name:'搜索绑定文件',exact:true})).toBeVisible();
 if(nasa){for(const box of await page.locator('.bound-dataset-files').getByRole('checkbox').all())await box.check();}
 else{await page.getByRole('button',{name:'param1',exact:true}).click();await page.getByRole('button',{name:'1dc58be25e1b6e5675cad724c63e222e',exact:true}).click();await page.getByRole('checkbox',{name:'选择 quadpress_smpl.vtk',exact:true}).check();await page.getByRole('checkbox',{name:'选择 hexvelo_smpl.vtk',exact:true}).check();}
 await page.getByRole('button',{name:'读取真实样本目录'}).click();await expect(page.getByRole('combobox',{name:'执行样本'})).toBeVisible();
 if(nasa){await page.getByRole('button',{name:'清空样本选择'}).click();await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'执行样本'})}).click();await page.getByRole('combobox',{name:'执行样本'}).fill('train / Sample002');await page.locator('.ant-select-item-option').filter({hasText:'train / Sample002'}).click();await page.keyboard.press('Escape');}
 await page.getByLabel('平台数据集名称').fill(scenario.case.startsWith('nasa')?'NASA_CRM':'shapenet_car');
 const other=scenario.format==='pt'?'ZARR':'PT';
 if(await page.getByRole('checkbox',{name:other,exact:true}).isChecked())await page.getByRole('checkbox',{name:other,exact:true}).uncheck();
 await page.getByRole('checkbox',{name:scenario.format.toUpperCase(),exact:true}).check();
 const submitted=page.waitForResponse(r=>r.url().endsWith('/rawprep/execute')&&r.request().method()==='POST');await page.getByRole('button',{name:'执行',exact:true}).click();const response=await submitted;expect(response.ok(),await response.text()).toBeTruthy();const run=await response.json();
 await expect.poll(async()=>{const r=await(await request.get(`${api}/projects/${p}/runs/${run.id}`)).json();return r.status},{timeout:120000}).toBe('succeeded');
 const config=await(await request.get(base+'/rawprep')).json();expect(config.rawprep.formats||[config.rawprep.format||'pt']).toEqual([scenario.format]);await page.reload();await page.locator('.bound-dataset-files').getByRole('tab',{name:'处理结果',exact:true}).click();const filename=(nasa?'surface_cp.':'surface_pressure.')+scenario.format;await page.getByRole('button',{name:'预览 '+filename,exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.getByRole('dialog').locator('table tbody tr').first()).toBeVisible({timeout:30000});await page.screenshot({path:info.outputPath(scenario.case+'-'+scenario.format+'.png'),fullPage:true});await info.attach('real-run',{body:JSON.stringify({project:p,task:t,run:run.id,format:scenario.format}),contentType:'application/json'});
 }finally{await request.patch(`${api}/projects/${p}`,{data:{archived:true}})}
});
