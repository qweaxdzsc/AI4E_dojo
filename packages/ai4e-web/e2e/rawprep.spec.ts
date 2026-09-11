import {test,expect} from '@playwright/test';
/** 正式表面案例、真实字段检查、多输出保存与页面执行，不使用接口替身。 */
test('页面多输出配置到真实处理和产物预览',async({page,request},info)=>{
 const api=(process.env.DOJO_API_URL||'http://127.0.0.1:8002')+'/api/v1';
 const p=await(await request.post(api+'/projects',{data:{name:'真实多输出浏览器 '+Date.now()}})).json();
 const created=await request.post(`${api}/projects/${p.id}/tasks`,{data:{name:'字段组合',case_id:'shapenet_car_transolver3_surface',data_root:'data0'}});expect(created.ok()).toBeTruthy();const t=await created.json();
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(`/projects/${p.id}/tasks/${t.id}/1`);
 await page.getByRole('button',{name:'▸ param1',exact:true}).click();await page.getByRole('button',{name:'▸ 1dc58be25e1b6e5675cad724c63e222e',exact:true}).click();await page.getByLabel('选择 quadpress_smpl.vtk',{exact:true}).check();await page.getByLabel('选择 hexvelo_smpl.vtk',{exact:true}).check();
 await page.getByRole('button',{name:'＋ 添加字段提取',exact:true}).click();const modal=page.getByRole('dialog');await modal.getByRole('button',{name:'添加输出',exact:true}).click();await modal.getByLabel('输出名称',{exact:true}).fill('surface_bundle');await modal.getByRole('combobox',{name:'读取文件',exact:true}).click();await page.locator('.ant-select-item-option').filter({hasText:'quadpress_smpl.vtk'}).click();await modal.getByRole('button',{name:'读取字段',exact:true}).click();
 const pressure=modal.getByRole('row').filter({has:page.getByRole('cell',{name:'point_scalars',exact:true})});await pressure.getByRole('checkbox').check();const points=modal.getByRole('row').filter({has:page.getByRole('cell',{name:'points',exact:true})});await points.getByRole('checkbox').check();await modal.getByRole('button',{name:'添加输出',exact:true}).click();await modal.getByLabel('输出名称',{exact:true}).nth(1).fill('pressure_copy');await pressure.getByRole('checkbox').check();await modal.getByRole('button',{name:'保存提取条目',exact:true}).click();
 await page.getByRole('button',{name:'保存配置',exact:true}).click();await expect(page.getByText('配置已保存，未创建新版本')).toBeVisible();const config=await(await request.get(`${api}/projects/${p.id}/tasks/${t.id}/configuration`)).json();expect(config.config.rawprep.extraction.entries[0].outputs).toHaveLength(2);
 await page.getByRole('button',{name:'开始处理',exact:true}).click();await expect(page.locator('.execution-log').getByText('succeeded',{exact:true})).toBeVisible({timeout:90000});
 const refs=await(await request.get(`${api}/projects/${p.id}/tasks/${t.id}/stage-inputs`)).json();expect(refs.some((r:any)=>r.binding==='train.manifest')).toBeTruthy();
 await page.getByRole('button',{name:'quadpress_smpl.vtk',exact:true}).click();await expect(page.getByRole('dialog')).toBeVisible();await expect(page.locator('canvas').first()).toBeVisible({timeout:30000});await page.screenshot({path:info.outputPath('real-multi-output.png'),fullPage:true});expect(errors).toEqual([]);
});
