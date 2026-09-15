import {test,expect} from '@playwright/test';
import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
const root='/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance';
const output=process.env.DOJO_INFER_UI_OUTPUT||root+'/real-browser';
mkdirSync(output,{recursive:true});
/** 实际浏览器、实际后端、真实CFD；不拦截任何请求。 */
test('从首页完成两权重三分片推理、导出及固定结果交接',async({page,request},info)=>{
 test.skip(process.env.DOJO_INFER_UI_REAL!=='1','显式启用真实 CFD 专项');test.setTimeout(1200000);page.setDefaultTimeout(30000);
 const context=JSON.parse(readFileSync(root+'/real-cfd/context.json','utf8'));const {project,task}=context,base=`/api/v1/projects/${project}/tasks/${task}/inference`;
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));let submissions=0;page.on('request',r=>{if(r.url().endsWith('/inference/batches')&&r.method()==='POST')submissions++;});
 await page.setViewportSize({width:1672,height:941});await page.goto('/projects');const card=page.locator('.projectgrid .taskcard').filter({hasText:'真实 CFD 推理验收'});await card.getByRole('link',{name:'进入项目',exact:true}).click();await page.getByRole('link',{name:'进入工作台',exact:true}).click();await page.locator('.workbench-steps').getByRole('link',{name:/^推理 ·/}).click();
 const response=await request.get(base+'/checkpoints');expect(response.ok()).toBeTruthy();const catalog=await response.json();
 for(const id of context.checkpoint_ids){const cp=catalog.items.find((c:any)=>c.id===id);expect(cp).toBeTruthy();await page.getByRole('checkbox',{name:`选择检查点 ${cp.name} · ${cp.run_id}`,exact:true}).check();}
 const samplePanel=page.locator('[data-region="samples"]');for(const ref of context.sample_selection){const title={train:'训练集',eval:'验证集',validation:'验证集',test:'测试集'}[ref.split as string];await samplePanel.getByRole('tab',{name:new RegExp(title!)}).click();await samplePanel.getByRole('checkbox',{name:'选择样本 '+ref.sample,exact:true}).check();}
 await expect(samplePanel).toContainText('已选择 3 / 3 个');await page.locator('[data-region="settings"] .ant-select').click();await page.locator('.ant-select-item-option').filter({hasText:'CPU'}).click();await page.getByRole('spinbutton',{name:'推理查询块大小'}).fill('1024');
 const checkResponse=page.waitForResponse(r=>r.url().endsWith('/inference/check'));await page.getByRole('button',{name:'检查推理配置',exact:true}).click();const checked=await checkResponse;expect(checked.ok(),await checked.text()).toBeTruthy();await expect(page.getByText('检查通过；尚未提交推理')).toBeVisible({timeout:60000});
 const submission=page.waitForResponse(r=>r.url().endsWith('/inference/batches')&&r.request().method()==='POST');await page.getByRole('button',{name:'开始计算',exact:true}).click();const sent=await submission;expect(sent.ok(),await sent.text()).toBeTruthy();const batchId=(await sent.json()).id;
 const submitted=sent.request().postDataJSON();expect(submitted.sample_selection).toHaveLength(3);expect(submitted.checkpoints).toHaveLength(2);expect(submitted.options.query_chunk_size).toBe(1024);
 await page.reload();let batch:any;
 await expect.poll(async()=>{const r=await request.get(base+'/batches/'+batchId);batch=await r.json();return ['succeeded','failed','partial','canceled','interrupted'].includes(batch.status)?batch.status:'running';},{timeout:900000,intervals:[1500,3000,5000]}).toBe('succeeded');
 expect(batch.children).toHaveLength(6);expect(new Set(batch.children.map((c:any)=>c.split)).size).toBe(3);
 const resultResponse=await request.get(base+'/batches/'+batchId+'/results');expect(resultResponse.ok(),await resultResponse.text()).toBeTruthy();const results=await resultResponse.json();expect(results.items).toHaveLength(6);expect(results.statistics.length).toBeGreaterThanOrEqual(30);
 mkdirSync(output+'',{recursive:true});writeFileSync(output+'/results.json',JSON.stringify({submitted,batch,results},null,2));
 await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(2,{timeout:30000});await page.screenshot({path:output+'/completed.png'});
 const initialSubmissions=submissions;for(const name of ['散点图','柱状图','折线图'])await page.getByRole('button',{name,exact:true}).click();await page.locator('[data-region="chart"]').getByRole('button',{name:'配置',exact:true}).click();await page.getByRole('button',{name:'应用',exact:true}).click();expect(submissions).toBe(initialSubmissions);
 for(const [label,ext] of [['导出 CSV','csv'],['导出 Excel','xlsx']]){const pending=page.waitForEvent('download');await page.getByRole('button',{name:label,exact:true}).click();const download=await pending;await download.saveAs(`${output}/results.${ext}`);expect(await download.failure()).toBeNull();}
 if(!await page.locator('.infer-details').first().evaluate(e=>(e as HTMLDetailsElement).open))await page.locator('.infer-details').first().locator('summary').click();await page.getByRole('button',{name:'查看日志',exact:true}).first().click();await expect(page.locator('.infer-details').first()).toContainText('infer',{timeout:30000});
 await page.locator('#stage-handoff summary').click();const prediction=page.getByRole('link',{name:'下载',exact:true}).first();const file=await request.get((await prediction.getAttribute('href'))!);expect(file.ok()).toBeTruthy();writeFileSync(output+'/prediction-manifest.json',await file.body());
 await page.getByRole('button',{name:'在后处理中打开',exact:true}).first().click();await expect(page).toHaveURL(/\/post\?batch=/);await expect(page.locator('.post-file-location')).toContainText('固定来源');await expect(page.locator('.post-result-files')).toBeVisible();
 await page.screenshot({path:output+'/post-fixed.png',fullPage:true});
 const meshRow=page.locator('.post-result-files .filerow').filter({has:page.getByRole('button',{name:'surface.vtp',exact:true})});
 await expect(meshRow).toHaveCount(1);await meshRow.getByRole('button',{name:'可视化',exact:true}).click();
 const outer=page.frameLocator('iframe[title="独立可视化应用"]');
 const inner=outer.frameLocator('iframe[title="三维物理场 Trame 工作台"]');
 await expect(inner.locator('.phys-tree').getByText('基础显示',{exact:true})).toBeVisible({timeout:120000});
 await inner.getByLabel('着色物理量',{exact:true}).click();
 await inner.getByRole('option',{name:'surface.pressure.prediction (point)',exact:true}).click();
 await inner.getByRole('button',{name:'轴测',exact:true}).click();
 await expect(inner.locator('canvas').first()).toBeVisible();
 await inner.getByRole('button',{name:'适窗',exact:true}).click();
 await expect(inner.getByRole('option',{name:'surface.pressure.prediction (point)',exact:true})).not.toBeVisible();
 // Trame服务回传相机与字段后，本地VTK画布在后续帧绘制。
 await page.waitForTimeout(1500);
 await page.screenshot({path:output+'/trame-fixed.png',fullPage:true});
 await page.getByRole('menuitem',{name:'项目管理',exact:true}).click();
 expect(errors).toEqual([]);writeFileSync(output+'/browser-evidence.json',JSON.stringify({batch_id:batchId,submissions,errors,downloads:['results.csv','results.xlsx'],status:'passed-through-real-trame'},null,2));
 await info.attach('batch',{body:JSON.stringify(batch),contentType:'application/json'});
});

/** 真实进程故障只作用于本次隔离批次，不改输入、权重和已提交数据。 */
test('真实CFD只评价、进程中断恢复、取消与任务隔离',async({page,request},info)=>{
 test.skip(process.env.DOJO_INFER_UI_REAL!=='1','显式启用真实 CFD 专项');test.setTimeout(1200000);page.setDefaultTimeout(30000);
 const c=JSON.parse(readFileSync(root+'/real-cfd/context.json','utf8'));
 const base=`/api/v1/projects/${c.project}/tasks/${c.task}/inference`,url=`/projects/${c.project}/tasks/${c.task}/infer`;
 const before=await (await request.get(`/api/v1/projects/${c.project}/tasks/${c.task}/configuration`)).json();
 await page.goto(url);const catalog=await (await request.get(base+'/checkpoints')).json();
 for(const id of c.checkpoint_ids){const cp=catalog.items.find((v:any)=>v.id===id);await page.getByRole('checkbox',{name:`选择检查点 ${cp.name} · ${cp.run_id}`,exact:true}).check();}
 for(const ref of c.sample_selection){await page.locator('[data-region="samples"]').getByRole('tab',{name:new RegExp(({train:'训练集',eval:'验证集',test:'测试集'} as any)[ref.split])}).click();await page.getByRole('checkbox',{name:'选择样本 '+ref.sample,exact:true}).check();}
 await page.getByRole('checkbox',{name:'保存数据',exact:true}).uncheck();await expect(page.getByRole('checkbox',{name:'导出网格',exact:true})).not.toBeChecked();await expect(page.getByRole('checkbox',{name:'导出网格',exact:true})).toBeDisabled();
 await page.locator('[data-region="settings"] .ant-select').click();await page.locator('.ant-select-item-option').filter({hasText:'CPU'}).click();
 async function submit(){const p=page.waitForResponse(r=>r.url().endsWith('/inference/batches')&&r.request().method()==='POST');await page.getByRole('button',{name:'开始计算',exact:true}).click();const r=await p;expect(r.ok(),await r.text()).toBeTruthy();return (await r.json()).id as string;}
 async function state(id:string){return (await request.get(base+'/batches/'+id)).json();}
 const id=await submit();const folder=`${c.project_directory}/tasks/${c.task}/.dojo/inference_batches/${id}`;
 let coordinator:any;await expect.poll(()=>{try{coordinator=JSON.parse(readFileSync(folder+'/coordinator.json','utf8'));return coordinator.batch_id;}catch{return ''; }},{timeout:30000}).toBe(id);
 process.kill(coordinator.pid,'SIGTERM'); // 协调进程真实失联；已有子进程不被重新提交。
 await expect.poll(async()=>(await state(id)).status,{timeout:60000,intervals:[500]}).toBe('interrupted');
 await page.reload();await page.locator('.infer-details').first().locator('summary').click();await expect(page.getByRole('button',{name:'恢复中断批次',exact:true})).toBeEnabled();await page.getByRole('button',{name:'恢复中断批次',exact:true}).click();
 await expect.poll(async()=>(await state(id)).status,{timeout:300000,intervals:[1000]}).toBe('succeeded');
 const batch=await state(id),results=await (await request.get(base+'/batches/'+id+'/results')).json();
 expect(batch.children).toHaveLength(6);expect(results.items).toHaveLength(6);expect(results.items.every((r:any)=>r.files.length===0)).toBeTruthy();expect(results.statistics.length).toBeGreaterThan(0);
 await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(2,{timeout:30000});
 const downloading=page.waitForEvent('download');await page.getByRole('button',{name:'导出 Excel',exact:true}).click();await (await downloading).saveAs(output+'/evaluation-only.xlsx');
 await page.screenshot({path:output+'/evaluation-only.png',animations:'disabled'});
 // 关闭重开后仍恢复同一结果；切换到独立新任务不继承选择或批次。
 await page.goto('/projects');await page.goto(url);await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(2);await expect(page.locator('[data-region="checkpoints"] input:checked')).toHaveCount(0);
 const invalid=await request.post(base+'/check',{data:{expected_revision:'stale',checkpoints:catalog.items.slice(0,1).map((v:any)=>({id:v.id,revision:v.revision})),sample_selection:c.sample_selection,device:'cpu'}});expect(invalid.status()).toBe(409);
 const isolated=await request.post(`/api/v1/projects/${c.project}/tasks`,{data:{name:'推理任务隔离验收',case_id:'shapenet_car_transolver3_surface'}});expect(isolated.ok()).toBeTruthy();const other=await isolated.json();
 try{await page.goto(`/projects/${c.project}/tasks/${other.id}/infer`);await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(0);await expect(page.getByRole('button',{name:'开始计算',exact:true})).toBeDisabled();}finally{await request.patch(`/api/v1/projects/${c.project}/tasks/${other.id}`,{data:{archived:true}});}
 // 取消使用API提交与浏览器控制，保持所取消的固定意图可追溯。
 await page.goto(url);const cancelRequest={expected_revision:catalog.revision,checkpoints:c.checkpoint_ids.map((id:string)=>{const cp=catalog.items.find((v:any)=>v.id===id);return {id,revision:cp.revision};}),sample_selection:c.sample_selection,device:'cpu',options:{evaluate:true,save_predictions:false,export_vtk:false},idempotency_key:crypto.randomUUID()};
 const pending=await request.post(base+'/batches',{data:cancelRequest});expect(pending.ok(),await pending.text()).toBeTruthy();const cancelId=(await pending.json()).id;
 await page.evaluate(({key,id})=>sessionStorage.setItem(key,id),{key:`dojo.infer.${c.project}.${c.task}`,id:cancelId});await page.reload();await expect(page.getByRole('button',{name:'取消批次',exact:true})).toBeEnabled();await page.getByRole('button',{name:'取消批次',exact:true}).click();await expect.poll(async()=>(await state(cancelId)).status,{timeout:60000,intervals:[500]}).toBe('canceled');
 const after=await (await request.get(`/api/v1/projects/${c.project}/tasks/${c.task}/configuration`)).json();expect(after).toEqual(before);
 writeFileSync(output+'/resilience.json',JSON.stringify({evaluation_only:id,recovered_pid:coordinator.pid,batch,results,canceled:cancelId,stale_revision:invalid.status(),configuration_unchanged:true},null,2));
 await info.attach('resilience',{body:JSON.stringify({id,cancelId}),contentType:'application/json'});
});

test('真实CFD首个子进程失败、最后成功与只重试失败部分',async({page,request})=>{
 test.skip(process.env.DOJO_INFER_UI_REAL!=='1','显式启用真实 CFD 专项');test.setTimeout(600000);
 const c=JSON.parse(readFileSync(root+'/real-cfd/context.json','utf8')),base=`/api/v1/projects/${c.project}/tasks/${c.task}/inference`;
 const catalog=await (await request.get(base+'/checkpoints')).json();
 const body={expected_revision:catalog.revision,checkpoints:c.checkpoint_ids.map((id:string)=>{const cp=catalog.items.find((v:any)=>v.id===id);return {id,revision:cp.revision};}),sample_selection:c.sample_selection,device:'cpu',options:{evaluate:true,save_predictions:false,export_vtk:false},idempotency_key:crypto.randomUUID()};
 const submitted=await request.post(base+'/batches',{data:body});expect(submitted.ok(),await submitted.text()).toBeTruthy();const id=(await submitted.json()).id;
 const stateFile=`${c.project_directory}/tasks/${c.task}/.dojo/inference_batches/${id}/state.json`;
 let first:any,receipt:any;await expect.poll(()=>{try{const b=JSON.parse(readFileSync(stateFile,'utf8'));first=b.children[0];receipt=JSON.parse(readFileSync(`${c.project_directory}/tasks/${c.task}/.dojo/executions/${first.run_id}/started.json`,'utf8'));return receipt.run_id===first.run_id;}catch{return false;}},{timeout:60000,intervals:[50]}).toBe(true);
 process.kill(receipt.pid,'SIGTERM'); // 本次隔离推理子进程真实异常，保留输入与其他子运行。
 const state=async(batch:string)=>(await request.get(base+'/batches/'+batch)).json();
 await expect.poll(async()=>(await state(id)).status,{timeout:300000,intervals:[500]}).toBe('partial');
 const failed=await state(id);expect(failed.children.at(-1).status).toBe('succeeded');expect(failed.children[0].status).not.toBe('succeeded');
 await page.goto(`/projects/${c.project}/tasks/${c.task}/infer`);await page.evaluate(({key,id})=>sessionStorage.setItem(key,id),{key:`dojo.infer.${c.project}.${c.task}`,id});await page.reload();
 await page.locator('.infer-details').first().locator('summary').click();await expect(page.locator('.infer-details').first()).toContainText('部分失败');
 const task=await (await request.get(`/api/v1/projects/${c.project}/tasks/${c.task}`)).json();expect(task.stage_summary.infer.status).toBe('partial');
 const p=page.waitForResponse(r=>r.url().endsWith('/retry'));await page.getByRole('button',{name:'重试失败子运行',exact:true}).click();const retried=await p;expect(retried.ok(),await retried.text()).toBeTruthy();const retry=(await retried.json()).id;
 await expect.poll(async()=>(await state(retry)).status,{timeout:300000,intervals:[500]}).toBe('succeeded');const done=await state(retry);
 expect(done.children).toHaveLength(1);expect(done.inherited_children).toHaveLength(5);expect(done.inherited_children.map((v:any)=>v.run_id)).toEqual(failed.children.slice(1).map((v:any)=>v.run_id));
 const results=await (await request.get(base+'/batches/'+retry+'/results')).json();expect(results.items).toHaveLength(6);expect(results.comparison.status).toBe('comparable');
 await expect(page.locator('.infer-details').first()).toContainText('保留原批次 5 个成功子运行',{timeout:30000});await page.screenshot({path:output+'/retry-inherited.png',animations:'disabled'});
 writeFileSync(output+'/partial-retry.json',JSON.stringify({terminated_pid:receipt.pid,failed,retried:done,results},null,2));
});

/** 固定数组重新评价和真实Excel/张量下载，不允许触发新的推理批次。 */
test('真实固定结果重算指标、Excel及预测张量下载',async({page,request})=>{
 test.skip(process.env.DOJO_INFER_UI_REAL!=='1','显式启用真实 CFD 专项');test.setTimeout(180000);page.setDefaultTimeout(30000);
 const c=JSON.parse(readFileSync(root+'/real-cfd/context.json','utf8'));
 const previous=JSON.parse(readFileSync(output+'/results.json','utf8')),batch=previous.batch.id;
 const post=`/api/v1/projects/${c.project}/tasks/${c.task}/post`;
 let predictions=0;page.on('request',r=>{if(r.method()==='POST'&&r.url().endsWith('/inference/batches'))predictions++;});
 await page.goto(`/projects/${c.project}/tasks/${c.task}/post?batch=${batch}&tab=metrics`);
 await expect(page.getByRole('button',{name:'计算指标',exact:true})).toBeEnabled({timeout:90000});
 const submitted=page.waitForResponse(r=>r.url().endsWith('/post/metric-jobs')&&r.request().method()==='POST');
 await page.getByRole('button',{name:'计算指标',exact:true}).click();const response=await submitted;
 expect(response.ok(),await response.text()).toBeTruthy();const job=(await response.json()).id;
 let value:any;await expect.poll(async()=>{value=await (await request.get(post+'/metric-jobs/'+job)).json();return value.status;},{timeout:90000,intervals:[500]}).toBe('succeeded');
 expect(value.rows).toHaveLength(6);expect(new Set(value.rows.map((r:any)=>r.split)).size).toBe(3);
 for(const row of value.rows){const original=previous.results.items.find((i:any)=>i.run_id===row.run_id&&i.sample===row.sample);
 // 评价run与预测run分别记录；用checkpoint修订、分片和样本定位原固定值。
 const source=original||previous.results.items.find((i:any)=>i.checkpoint.revision===row.checkpoint.revision&&i.split===row.split&&i.sample===row.sample);
 expect(source).toBeTruthy();const metric=source.metric_records.find((r:any)=>r.field_id===row.field_id);expect(row.values.mae).toBeCloseTo(metric.values.mae,12);}
 await expect(page.locator('.post-metric-status')).toContainText('计算完成');
 await page.getByRole('button',{name:'导出 ▾',exact:true}).click();const pending=page.waitForEvent('download');await page.getByRole('menuitem',{name:'导出 Excel',exact:true}).click();await (await pending).saveAs(output+'/post-recalculated.xlsx');
 await page.goto(`/projects/${c.project}/tasks/${c.task}/infer`);await page.evaluate(({key,batch})=>sessionStorage.setItem(key,batch),{key:`dojo.infer.${c.project}.${c.task}`,batch});await page.reload();
 await page.locator('#stage-handoff summary').click();const row=page.locator('#stage-handoff tbody tr').filter({hasText:'.prediction.pt'}).first();
 const download=page.waitForEvent('download');await row.getByRole('link',{name:'下载',exact:true}).click();const file=await download;await file.saveAs(output+'/prediction-array.pt');expect(await file.failure()).toBeNull();
 expect(predictions).toBe(0);writeFileSync(output+'/post-recalculated.json',JSON.stringify({job,value,predictions,download:file.suggestedFilename()},null,2));
});

/** 真实目录上的编辑、过滤和预检只读核验。 */
test('真实目录搜索排序筛选与全选取消名单准确',async({page,request})=>{
 test.skip(process.env.DOJO_INFER_UI_REAL!=='1','显式启用真实 CFD 专项');test.setTimeout(120000);page.setDefaultTimeout(30000);
 const c=JSON.parse(readFileSync(root+'/real-cfd/context.json','utf8')),base=`/api/v1/projects/${c.project}/tasks/${c.task}/inference`;
 await page.goto(`/projects/${c.project}/tasks/${c.task}/infer`);
 const catalog=await (await request.get(base+'/checkpoints')).json();
 for(const id of c.checkpoint_ids){const cp=catalog.items.find((v:any)=>v.id===id);await page.getByRole('checkbox',{name:`选择检查点 ${cp.name} · ${cp.run_id}`,exact:true}).check();}
 const cpPanel=page.locator('[data-region="checkpoints"]');await cpPanel.getByRole('textbox',{name:'搜索检查点'}).fill(c.checkpoint_ids[0].split(':')[0]);await expect(cpPanel.locator('.infer-choice')).toHaveCount(catalog.items.filter((v:any)=>v.run_id===c.checkpoint_ids[0].split(':')[0]).length);await cpPanel.getByRole('textbox',{name:'搜索检查点'}).fill('');
 await cpPanel.getByRole('button',{name:/排序/}).click();await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'检查点排序方式'})}).click();await page.locator('.ant-select-item-option').filter({hasText:'名称'}).click();await cpPanel.getByRole('button',{name:/排序/}).click();
 const samples=page.locator('[data-region="samples"]');for(const ref of c.sample_selection){
  await samples.getByRole('tab',{name:new RegExp(({train:'训练集',eval:'验证集',test:'测试集'} as any)[ref.split])}).click();
  await samples.getByRole('textbox',{name:'搜索推理样本'}).fill(ref.sample);await samples.getByRole('button',{name:/排序/}).click();
  await samples.getByRole('checkbox',{name:/全选当前页/}).check();await samples.getByRole('checkbox',{name:/全选当前页/}).uncheck();await samples.getByRole('checkbox',{name:/全部筛选范围/}).check();await samples.getByRole('textbox',{name:'搜索推理样本'}).fill('');
 }
 await samples.getByRole('button',{name:/筛选/}).click();await page.locator('.ant-select').filter({has:page.getByRole('combobox',{name:'样本筛选范围'})}).click();await page.locator('.ant-select-item-option').filter({hasText:'已选择'}).click();await samples.getByRole('button',{name:/筛选/}).click();
 const response=page.waitForResponse(r=>r.url().endsWith('/inference/check'));await page.getByRole('button',{name:'检查推理配置',exact:true}).click();const checked=await response;expect(checked.ok(),await checked.text()).toBeTruthy();const body=checked.request().postDataJSON();expect(body.sample_selection).toEqual(c.sample_selection);expect(body.checkpoints).toHaveLength(2);
 writeFileSync(output+'/selection-check.json',JSON.stringify(body,null,2));
});
