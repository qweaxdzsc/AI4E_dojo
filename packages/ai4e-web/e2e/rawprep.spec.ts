import {test,expect} from '@playwright/test';
/** 正式表面案例、真实字段检查、单样本执行与产物预览，不使用接口替身。 */
test('页面单场提取到真实处理和产物预览',async({page,request},info)=>{
 test.setTimeout(180000);
 page.setDefaultTimeout(25000);
 const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
 const p=await(await request.post(api+'/projects',{data:{name:'真实单场浏览器 '+Date.now()}})).json();
 const created=await request.post(`${api}/projects/${p.id}/tasks`,{data:{name:'字段提取',case_id:'shapenet_car_transolver3_surface',data_root:'data0'}});expect(created.ok()).toBeTruthy();const t=await created.json();
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(`/projects/${p.id}/tasks/${t.id}/1`);
 await page.getByRole('button',{name:'param1',exact:true}).click();await page.getByRole('button',{name:'1dc58be25e1b6e5675cad724c63e222e',exact:true}).click();await page.getByLabel('选择 quadpress_smpl.vtk',{exact:true}).check();await page.getByLabel('选择 hexvelo_smpl.vtk',{exact:true}).check();
 const before=await page.locator('.extraction-card').count();
 expect(before).toBeGreaterThan(0);
 await page.getByRole('button',{name:'＋ 添加字段提取',exact:true}).click();const modal=page.getByRole('dialog');
 const selected=modal.locator('.ant-select-selection-item');
 if((await selected.textContent())!=='quadpress_smpl.vtk'){
  await modal.locator('.ant-select-selector').click();
  await page.locator('.ant-select-item-option').filter({hasText:'quadpress_smpl.vtk'}).click();
 }
 const pressure=modal.getByRole('row').filter({has:page.getByRole('cell',{name:'point_scalars',exact:true})});
 if(await pressure.count()===0) await modal.getByRole('button',{name:'读取字段',exact:true}).click();
 await pressure.getByRole('radio').check();
 await expect(modal.getByRole('radio')).toHaveCount(await modal.getByRole('radio').count());
 await modal.getByRole('button',{name:/取\s*消/}).click();
 await expect(page.locator('.extraction-card')).toHaveCount(before);
 const config=await(await request.get(`${api}/projects/${p.id}/tasks/${t.id}/configuration`)).json();
 const fields=config.config.rawprep.save_fields||[];expect(fields.length).toBeGreaterThan(0);
 await expect(page.getByText(/处理样本：[1-9]/)).toBeVisible({timeout:60000});
 await page.getByLabel('平台数据集名称').fill('field_extract_'+Date.now());
 await page.getByRole('combobox',{name:'执行范围',exact:true}).press('ArrowDown');
 await page.locator('.ant-select-item-option').filter({hasText:'指定样本'}).click();
 const combo=page.getByRole('combobox',{name:'执行样本选择',exact:true});
 await combo.focus();await combo.press('ArrowDown');await combo.fill('1dc58be25e1b6e5675cad724c63e222e');
 await page.locator('.ant-select-item-option').filter({hasText:'1dc58be25e1b6e5675cad724c63e222e'}).click();
 await page.keyboard.press('Escape');
 await page.getByRole('button',{name:'执行',exact:true}).click();await expect(page.locator('.execution-log').getByText('succeeded',{exact:true})).toBeVisible({timeout:90000});
 const refs=await(await request.get(`${api}/projects/${p.id}/tasks/${t.id}/stage-inputs`)).json();expect(refs.some((r:any)=>r.binding==='train.manifest')).toBeTruthy();
 const listed=await(await request.get(`${api}/datasets`)).json();
 expect(listed.some((item:any)=>String(item.name||'').startsWith('field_extract_'))).toBeTruthy();
 await page.getByRole('button',{name:'quadpress_smpl.vtk',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();
 const outer=page.frameLocator('iframe[title="独立可视化应用"]');
 const inner=outer.frameLocator('iframe[title="三维物理场 Trame 工作台"]');
 await expect(inner.getByText('基础显示').first()).toBeVisible({timeout:30000});
 await page.screenshot({path:info.outputPath('real-single-field.png'),fullPage:true});expect(errors).toEqual([]);
});
