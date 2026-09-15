/** 真实PVD时间轴、四视口和相机联动；点击UI后通过公开快照核验结果。 */
const {chromium, expect}=require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs=require('node:fs');const path=require('node:path');
(async()=>{
 const base=process.env.VIS_BROWSER_URL||'http://127.0.0.1:18092';
 const context=process.env.VIS_CONTEXT, root=process.env.VIS_EVIDENCE_ROOT;
 if(!context||!root)throw new Error('需要显式上下文与证据根');
 const browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1600,height:1100}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));let session;
 try{
  await page.goto(base+'/workspace/#/phys?embed=1&context='+context);
  const creating=page.waitForResponse(r=>r.url().endsWith('/api/phys/sessions')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'新建工作区'}).click();session=await (await creating).json();
  const frame=page.frameLocator('iframe');await frame.getByText('Apply 显示',{exact:true}).waitFor({timeout:60000});
  const snapshot=async()=>{
   const r=await page.request.post(base+'/api/phys/sessions/'+session.session_id+'/commands',{data:{context_id:context,command:{operation:'snapshot'}}});
   if(!r.ok())throw new Error(await r.text());return r.json();
  };
  await frame.getByText('后一帧',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.time.value).toBe(1);
  await frame.getByText('前一帧',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.time.value).toBe(0);
  await frame.getByText('播放 ▶',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.time.value,{timeout:15000}).toBe(11);
  await frame.getByText('◀ 播放',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.time.value,{timeout:15000}).toBe(0);
  await frame.getByText('暂停',{exact:true}).click();
  await frame.getByLabel('窗口数',{exact:true}).click();
  await frame.getByRole('option',{name:'4',exact:true}).click();
  await frame.getByText('分窗',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.views.length).toBe(4);
  await frame.getByText('相机联动',{exact:true}).click();
  await expect.poll(async()=>(await snapshot()).spec.link_groups.length).toBe(1);
  await page.screenshot({path:path.join(root,'timeline-four-views.png')});
  if(errors.length)throw new Error(errors.join('\n'));
  fs.writeFileSync(path.join(root,'timeline-results.json'),JSON.stringify({status:'passed',checks:['actual PVD times','step forward/back','play forward/reverse','pause','four viewports','explicit camera linking'],snapshot:await snapshot()},null,2));
  console.log('TIMELINE PASS');
 }catch(e){await page.screenshot({path:path.join(root,'failure.png')});throw e;}
 finally{await page.goto('about:blank');if(session?.session_id)await page.request.delete(base+'/api/phys/sessions/'+session.session_id+'?context_id='+context);await browser.close();}
})().catch(e=>{console.error(e);process.exit(1)});
