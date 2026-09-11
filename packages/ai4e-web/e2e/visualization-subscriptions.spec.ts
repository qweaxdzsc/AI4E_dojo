import {test,expect} from '@playwright/test';
/** 传输协议夹具验证前端取消正文；服务共享进程隔离由后端真实用例覆盖。 */
test('查看器仅释放自己的转换订阅',async({page})=>{
 let posts=0,complete=false;const cancellations:any[]=[];let releaseFirst!:()=>void;const firstResponse=new Promise<void>(resolve=>{releaseFirst=resolve;});
 await page.route('**/api/v1/projects/subscription-fixture/**',async route=>{
  const request=route.request(),url=request.url();
  if(url.endsWith('/visualization/operations')){posts++;const index=posts;if(index===1)await firstResponse;return route.fulfill({json:{operation_id:'shared',status:'running',subscription_id:'subscriber-'+index}});}
  if(url.endsWith('/cancel')){cancellations.push(request.postDataJSON());return route.fulfill({json:{operation_id:'shared',status:'running'}});}
  if(url.endsWith('/operations/shared'))return route.fulfill({json:complete?{operation_id:'shared',status:'succeeded',result:{geometry_buffers:[],fields:[]},result_refs:[{project_id:'subscription-fixture',asset_id:'display',revision:'fixed'}]}:{operation_id:'shared',status:'running'}});
  return route.continue();
 });
 await page.goto('/projects');await page.evaluate(async()=>{const {transform}=await import('/src/modules/visualization/api.ts' as any);const source={project_id:'subscription-fixture',asset_id:'source',revision:'source-fixed'};const a=new AbortController(),b=new AbortController();(window as any).__subscriberA=a;(window as any).__subscriberB=b;(window as any).__subscriptionResults=[];(window as any).__promiseA=transform(source,[],a.signal).then(()=>{(window as any).__subscriptionResults.push('A success');}).catch((e:Error)=>{(window as any).__subscriptionResults.push('A '+e.name);});(window as any).__startSubscriberB=()=>{(window as any).__promiseB=transform(source,[],b.signal).then(()=>{(window as any).__subscriptionResults.push('B success');});};});
 await expect.poll(()=>posts).toBe(1);await page.evaluate(()=>(window as any).__startSubscriberB());await expect.poll(()=>posts).toBe(2);await page.evaluate(()=>(window as any).__subscriberA.abort());releaseFirst();await expect.poll(()=>cancellations).toEqual([{subscription_id:'subscriber-1'}]);await expect.poll(()=>page.evaluate(()=>(window as any).__subscriptionResults)).toEqual(['A AbortError']);
 complete=true;await page.evaluate(()=>(window as any).__promiseB);expect(await page.evaluate(()=>(window as any).__subscriptionResults)).toEqual(['A AbortError','B success']);expect(cancellations).toEqual([{subscription_id:'subscriber-1'}]);
});

test('旧服务没有订阅字段时保留无正文取消',async({page})=>{
 let submitted=false,canceled=false,cancelBody:string|null='not-called';
 await page.route('**/api/v1/projects/legacy-fixture/**',async route=>{const request=route.request();if(request.url().endsWith('/cancel')){canceled=true;cancelBody=request.postData();return route.fulfill({json:{status:'canceled'}});}submitted=true;return route.fulfill({json:{operation_id:'legacy',status:'running'}});});
 await page.goto('/projects');await page.evaluate(async()=>{const {transform}=await import('/src/modules/visualization/api.ts' as any);const controller=new AbortController();(window as any).__legacyAbort=controller;(window as any).__legacyPending=transform({project_id:'legacy-fixture',asset_id:'source',revision:'fixed'},[],controller.signal).catch(()=>{});});
 await expect.poll(()=>submitted).toBe(true);await page.waitForTimeout(50);await page.evaluate(()=>(window as any).__legacyAbort.abort());await expect.poll(()=>canceled).toBe(true);expect(cancelBody).toBeNull();
});

test('提交前已取消不会创建转换订阅',async({page})=>{
 let posts=0;await page.route('**/api/v1/projects/preaborted-fixture/**',async route=>{posts++;await route.fulfill({json:{operation_id:'unexpected',status:'running'}});});await page.goto('/projects');const result=await page.evaluate(async()=>{const {transform}=await import('/src/modules/visualization/api.ts' as any);const controller=new AbortController();controller.abort();try{await transform({project_id:'preaborted-fixture',asset_id:'source',revision:'fixed'},[],controller.signal);return 'unexpected';}catch(e){return (e as Error).name;}});expect(result).toBe('AbortError');expect(posts).toBe(0);
});
