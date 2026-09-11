/* 验证整合原型的阶段隔离、导航与配置保留；不代表后端功能验收。 */
const {chromium}=require('/Users/zonghui/work/new_code_project/AI4E_Vis/frontend/node_modules/@playwright/test');
const assert=require('node:assert/strict');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 const page=await browser.newPage({viewport:{width:1672,height:1050}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 const file=path.resolve(__dirname,'../../docs/prototypes/dojo-web-integrated.html');
 await page.goto('file://'+file+'#projects');
 assert(await page.locator('#app').innerText());
 for(let step=1;step<=6;step++){
  await page.evaluate(n=>{location.hash='workbench/'+n},step);
  await page.waitForSelector(`#stage-bank iframe[data-step="${step}"][data-ready="true"]:not([hidden])`);
  const frame=await page.locator('#stage-bank iframe:not([hidden])').contentFrame();
  assert.equal(await frame.locator('#steps').isVisible(),false);
  assert.equal(await page.locator('.topsteps button').count(),8);
  assert.equal(await page.locator('#sidenav .navitem').count(),2);
  assert((await frame.locator('body').innerText()).length>150);
 }
 await page.evaluate(()=>{location.hash='workbench/2'});
 const frame=page.frameLocator('#stage-bank iframe[data-step="2"]:not([hidden])');
 const input=frame.locator('input:not([type="checkbox"]):not([type="file"]):visible').first();
 await input.fill('集成保留检查');
 await page.evaluate(()=>{location.hash='workbench/3'});
 await page.waitForSelector('iframe[data-step="3"]:not([hidden])');
 await page.evaluate(()=>{location.hash='workbench/2'});
 await page.waitForSelector('iframe[data-step="2"]:not([hidden])');
 assert.equal(await input.inputValue(),'集成保留检查');
 await page.getByRole('button',{name:'收起菜单',exact:true}).click();
 assert.equal(await input.inputValue(),'集成保留检查');
 await page.getByRole('button',{name:'展开菜单',exact:true}).click();
 for(const step of [0,7]){
  await page.evaluate(n=>{location.hash='workbench/'+n},step);
  await page.waitForFunction(()=>document.getElementById('stage-bank').hidden);
  assert((await page.locator('#app').innerText()).length>150);
 }
 await page.evaluate(()=>{location.hash='workbench/1'});
 await page.waitForSelector('iframe[data-step="1"]:not([hidden])');
 await page.screenshot({path:'/private/tmp/dojo-integrated-rawprep.png',fullPage:true});
 // 隐藏的独立页面旧链接也应由整合导航接管，不加载第二层平台。
 await page.frameLocator('iframe[data-step="1"]:not([hidden])').locator('a[href="dojo-web-wireframe.html#project/0"]').first().evaluate(a=>a.click());
 await page.waitForURL(/#project\/0$/);
 assert.equal(await page.locator('#stage-bank').isVisible(),false);
 await page.evaluate(()=>{location.hash='workbench/6'});
 await page.waitForSelector('iframe[data-step="6"]:not([hidden])');
 await page.screenshot({path:'/private/tmp/dojo-integrated-post.png',fullPage:true});
 const post=page.frameLocator('iframe[data-step="6"]:not([hidden])');
 await post.getByRole('tab',{name:'指标数据',exact:true}).click();
 assert.equal(await post.locator('#postMetricRows tr').count(),11);
 await post.getByRole('tab',{name:'图表',exact:true}).click();
 assert.equal(await post.locator('.post-chart-card img').count(),4);
 await post.getByLabel('放大 相对L2误差随迭代变化',{exact:true}).click();
 assert(await post.locator('#info img').isVisible());
 await post.getByRole('button',{name:'关闭',exact:true}).click();
 await post.getByRole('tab',{name:'结果可视化',exact:true}).click();
 assert.deepEqual(errors,[]);
 await browser.close();console.log('Integrated prototype: six embedded stages, retained state, shell and navigation PASS');
})().catch(e=>{console.error(e);process.exit(1)});
