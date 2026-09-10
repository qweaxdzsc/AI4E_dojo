/** 线框交互验收：只操作本地示意页面，不连接后端或真实训练资源。 */
const {chromium,expect}=require(process.env.PLAYWRIGHT_MODULE || '@playwright/test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {resolve}=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true});
 try{
 const page=await browser.newPage({viewport:{width:1600,height:1100}});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto(pathToFileURL(resolve(__dirname,'../../docs/prototypes/dojo-web-wireframe.html')).href);
 const click=async name=>page.getByRole('button',{name,exact:true}).click();
 await click('收起菜单');assert(await page.locator('body').evaluate(el=>el.classList.contains('collapsed')));await click('展开菜单');
 await page.getByLabel('搜索项目',{exact:true}).fill('机翼');await expect(page.locator('.taskcard')).toHaveCount(1);
 await page.getByLabel('搜索项目',{exact:true}).fill('');await click('已归档');await expect(page.locator('.taskcard')).toHaveCount(1);
 await click('全部项目');await page.getByLabel('筛选研究领域',{exact:true}).selectOption('流体力学');await expect(page.locator('.taskcard')).toHaveCount(2);await page.getByLabel('筛选研究领域',{exact:true}).selectOption('全部领域');await page.getByLabel('项目排序',{exact:true}).selectOption('创建时间 ↑');
 await page.screenshot({path:'/private/tmp/dojo-v2-projects.png',fullPage:true});
 await page.getByRole('button',{name:'进入项目',exact:true}).first().click();await expect(page.locator('.ministeps')).toHaveCount(5);await expect(page.locator('.ministeps').first().getByRole('button')).toHaveCount(8);
 await expect(page.locator('#sidenav .navitem')).toHaveCount(2);await expect(page.locator('.projecttabs button')).toHaveCount(6);
 await page.screenshot({path:'/private/tmp/dojo-v2-tasks.png',fullPage:true});
 await page.locator('.projecttabs').getByRole('button',{name:'版本树',exact:false}).click();await click('选择任务 B1');
 await page.getByLabel('血缘任务阶段',{exact:true}).selectOption('2');
 await page.getByLabel('选择 锚点数量',{exact:true}).check();await click('添加选中项到对比参数');
 await expect(page.locator('aside.panel select')).toHaveCount(1);
 await page.screenshot({path:'/private/tmp/dojo-v2-tree.png',fullPage:true});
 await page.getByRole('button',{name:'前往版本比较（1） →',exact:true}).click();assert.match(await page.locator('.comparemain table').innerText(),/锚点数量/);
 await page.locator('.viewrail button').filter({hasText:'趋势'}).click();await expect(page.locator('.chart')).toHaveCount(1);
 await page.locator('.viewrail button').filter({hasText:'三维可视化'}).click();await expect(page.locator('.pvview')).toHaveCount(0);
 await page.getByRole('button',{name:'＋ 添加视图',exact:true}).first().click();await click('＋ 添加视图');await expect(page.locator('.pvview')).toHaveCount(2);
 await page.getByLabel('过滤器',{exact:true}).selectOption('Slice');await click('Apply');assert.match(await page.locator('.pipelinechild').innerText(),/Slice/);
 await page.getByLabel('显示字段',{exact:true}).selectOption('速度 / m/s');assert.match(await page.locator('.pvview .viewtitle').first().innerText(),/速度/);
 await page.screenshot({path:'/private/tmp/dojo-v2-compare.png',fullPage:true});
 await click('加入项目报告');await expect(page.locator('.reportblock')).toHaveCount(3);
 await page.locator('.projecttabs').getByRole('button',{name:'文件管理',exact:false}).click();
 await page.getByLabel('筛选文件版本',{exact:true}).selectOption('B2');await expect(page.locator('#filerows tr')).toHaveCount(2);
 await page.getByLabel('搜索文件',{exact:true}).fill('metrics');await expect(page.locator('#filerows tr')).toHaveCount(1);await click('预览');await expect(page.locator('dialog[open]')).toHaveCount(1);await click('关闭');
 await page.getByLabel('搜索文件',{exact:true}).fill('');await page.getByLabel('筛选文件类型',{exact:true}).selectOption('图像');await expect(page.locator('#filerows tr')).toHaveCount(1);await page.getByLabel('文件排序',{exact:true}).selectOption('大小 ↓');
 await page.locator('.projecttabs').getByRole('button',{name:'任务管理',exact:false}).click();await page.getByRole('button',{name:'进入工作台',exact:true}).first().click();
 await expect(page.locator('.topsteps button')).toHaveCount(8);await expect(page.locator('.projecttabs')).toHaveCount(0);await expect(page.locator('#sidenav .navitem')).toHaveCount(2);
 await page.locator('.topsteps button').nth(1).click();await expect(page.locator('.rawcolumns > section')).toHaveCount(3);
 await page.getByLabel('匹配文件名',{exact:true}).fill('quadpress*');await click('扫描匹配');await expect(page.locator('.rawfiletable input:checked')).toHaveCount(2);
 await page.getByLabel('原数据输出格式',{exact:true}).selectOption('PT + VTKHDF');await click('预检（演示）');await expect(page.locator('.rawlogs')).toContainText('没有写入数据');await click('▶ 执行（演示）');await expect(page.locator('.outputs')).toContainText('entity_mapping.json');await expect(page.locator('.rawlogs')).toContainText('仅 UI 模拟');
 await page.screenshot({path:'/private/tmp/dojo-v3-rawprep.png',fullPage:true});
 await click('模板配置');await expect(page.locator('.configcode')).toContainText('warmup_cosine');await click('关闭');await click('执行范围');await expect(page.locator('.flowcards > div')).toHaveCount(4);await click('关闭');await click('输入输出交接');await expect(page.locator('dialog')).toContainText('preparation.json');await click('关闭');
 
 for(let i=2;i<=5;i++){
  await page.locator('.topsteps button').nth(i).click();await expect(page.locator('.formsection').nth(1)).toBeVisible();
  await click('表格查看');await expect(page.locator('dialog[open] table')).toHaveCount(1);await click('关闭');
 }
 await page.locator('.topsteps button').nth(2).click();await page.getByLabel('锚点数量',{exact:true}).fill('8192');await click('下一步 →');await click('← 上一步');assert.equal(await page.getByLabel('锚点数量',{exact:true}).inputValue(),'8192');
 await page.screenshot({path:'/private/tmp/dojo-v2-workbench.png',fullPage:true});
 await page.locator('.topsteps button').nth(6).click();await click('指标');await expect(page.locator('#app table')).toHaveCount(1);await click('图表');await expect(page.locator('.chart')).toHaveCount(1);await click('三维可视化');await click('＋ 添加视图');await expect(page.locator('.pvview')).toHaveCount(2);
 await click('三维查看');await page.locator('dialog').getByRole('button',{name:'＋ 添加视图',exact:true}).click();await expect(page.locator('dialog .pvview')).toHaveCount(2);await click('关闭');
 await page.screenshot({path:'/private/tmp/dojo-v2-post.png',fullPage:true});
 await click('返回任务管理');await page.locator('.projecttabs').getByRole('button',{name:'批量运行',exact:false}).click();await click('生成计划表');await click('运行计划（演示）');await click('运行计划（演示）');await expect(page.getByRole('button',{name:'A1-anchors-2048',exact:true})).toHaveCount(1);await click('A1-anchors-2048');await expect(page.locator('.topsteps button')).toHaveCount(8);
 assert.deepEqual(errors,[]);console.log('PASS: collapsible navigation; project search/filter/sort; task progress; stage parameter selection; comparison table/trend/viewer; file filters; 8-step workbench; popup previews; post metrics/charts; batch idempotency. No page errors.');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
