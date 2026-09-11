import {test,expect} from '@playwright/test';
/** 标为测试夹具的解析三角形，验证单元语义和预算隔离；不替代真实数据验收。 */
test('四窗口预算隔离及单元字段拾取',async({page})=>{
 const fixtures:Record<string,Float32Array|Uint32Array|BigInt64Array>={points:new Float32Array([-1,-1,0,1,-1,0,0,1,0]),polys:new Uint32Array([3,0,1,2]),pressure:new Float32Array([99]),ids:new BigInt64Array([9007199254740993n])};
 await page.route('**/__viz_fixture/*',async route=>{const key=route.request().url().split('/').at(-1)!;await route.fulfill({contentType:'application/octet-stream',body:Buffer.from(fixtures[key].buffer)});});
 const errors:string[]=[];page.on('pageerror',e=>errors.push(e.message));await page.goto('/projects');
 await page.evaluate(async()=>{
  const React=await import('/node_modules/.vite/deps/react.js' as any),ReactDOM=await import('/node_modules/.vite/deps/react-dom_client.js' as any),{VtkViewport}=await import('/src/infrastructure/rendering/vtk/Viewport.tsx' as any);const h=React.createElement||React.default.createElement;
  const d=(path:string,dtype:string,shape:number[],byte_length:number)=>({path,dtype,shape,byte_length,byte_order:'little'});
  const manifest={geometry_buffers:[d('points','float32',[3,3],36)],topology_buffers:[{...d('polys','uint32',[4],16),name:'polys'}],fields:[{field_id:'cell:pressure',name:'pressure',association:'cell',components:1,range:[99,99],buffer:d('pressure','float32',[1],4)}],entity_mapping:{generated_entities:false,cell:d('ids','int64',[1],8)}};
  const host=document.createElement('div');document.body.replaceChildren(host);host.style.cssText='display:grid;grid-template-columns:1fr 1fr;height:800px';(window as any).__pick=null;(window as any).__errors=[];
  function Window({index}:any){const [error,setError]=(React.useState||React.default.useState)('');return h('section',{},h('h3',{},'窗口 '+index),error?h('div',{role:'alert'},error):h(VtkViewport,{manifest:index===4?{...manifest,geometry_buffers:[{...manifest.geometry_buffers[0],byte_length:129*1024*1024}]}:manifest,url:(p:string)=>'/__viz_fixture/'+p,field:'cell:pressure',representation:'surface',opacity:1,onError:(e:Error)=>{(window as any).__errors.push(index);setError(e.message);},onPick:(p:any)=>{(window as any).__pick=p;}}));}
  (window as any).__safetyRoot=(ReactDOM.createRoot||ReactDOM.default.createRoot)(host);(window as any).__safetyRoot.render(h(React.Fragment||React.default.Fragment,{},...[1,2,3,4].map(index=>h(Window,{index,key:index}))));
 });
 await page.waitForTimeout(300);expect(errors).toEqual([]);await expect(page.getByRole('alert')).toHaveText('单窗口显示资产超过 128 MiB 预算');await expect(page.locator('.viz-canvas canvas')).toHaveCount(3);
 await page.waitForTimeout(300);const box=await page.locator('.viz-canvas').first().boundingBox();if(!box)throw new Error('missing canvas');await page.mouse.click(box.x+box.width/2,box.y+box.height/2);
 await expect.poll(()=>page.evaluate(()=>(window as any).__pick)).toMatchObject({association:'cell',display_id:0,original_id:'9007199254740993',values:['99'],generated:false});
 expect(await page.evaluate(()=>(window as any).__errors)).toEqual([4]);await expect(page.locator('.viz-canvas canvas')).toHaveCount(3);
 await page.evaluate(()=>(window as any).__safetyRoot.unmount());const cache=await page.evaluate(async()=>{const {bufferCacheStats}=await import('/src/infrastructure/assets/binary.ts' as any);return bufferCacheStats();});expect(cache.references).toBe(0);expect(cache.entries).toBe(0);
});
