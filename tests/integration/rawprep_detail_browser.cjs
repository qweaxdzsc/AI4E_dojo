/** 原始处理细节原型验收：只验证本地交互，不读取真实数据。 */
const {chromium,expect}=require(process.env.PLAYWRIGHT_MODULE||'@playwright/test');
const {pathToFileURL}=require('node:url');
const {resolve}=require('node:path');
(async()=>{const browser=await chromium.launch({headless:true});try{
const page=await browser.newPage({viewport:{width:1600,height:1050}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto(pathToFileURL(resolve(__dirname,'../../docs/prototypes/dojo-rawprep-detail.html')).href);
await expect(page.locator('.steps a')).toHaveCount(8);
await page.getByRole('button',{name:'配置字段提取',exact:true}).click();
await page.getByLabel('选择 surface_position',{exact:true}).check();await page.getByLabel('选择 surface_pressure',{exact:true}).check();
await page.getByLabel('提取源文件').selectOption('volume');await page.getByLabel('选择 volume_velocity',{exact:true}).check();
await expect(page.locator('#plannedTree')).toContainText('surface_pressure.pt');await expect(page.locator('#plannedTree')).toContainText('volume.vtkhdf');
await page.getByLabel('输出名称 volume_velocity',{exact:true}).fill('surface_pressure');await page.getByRole('button',{name:'应用字段方案',exact:true}).click();await expect(page.locator('#validation')).toContainText('唯一');
await page.getByLabel('输出名称 volume_velocity',{exact:true}).fill('volume_velocity');
await page.screenshot({path:'/private/tmp/dojo-rawprep-extraction.png',fullPage:true});
await page.getByRole('button',{name:'应用字段方案',exact:true}).click();await expect(page.locator('#planSummary')).toContainText('3 个字段');
await page.getByRole('button',{name:'配置字段提取',exact:true}).click();await page.getByLabel('选择 surface_pressure',{exact:true}).uncheck();await page.getByRole('button',{name:'取消',exact:true}).click();await expect(page.locator('#planSummary')).toContainText('3 个字段');
await page.getByLabel('搜索文件',{exact:true}).fill('press.npy');await page.locator('#tree button').filter({hasText:'press.npy'}).click();await expect(page.locator('#fileNote')).toContainText('不自带拓扑');await expect(page.getByRole('button',{name:'配置字段提取',exact:true})).toBeDisabled();await page.getByRole('button',{name:'⛶ 弹出预览',exact:true}).click();await expect(page.locator('#preview')).toBeVisible();await page.getByRole('button',{name:'关闭预览',exact:true}).click();
await page.getByLabel('搜索文件',{exact:true}).fill('');await page.getByLabel('文件类型',{exact:true}).selectOption('mesh');await page.locator('#tree button').filter({hasText:'geometry.vtkhdf'}).click();await expect(page.locator('#fileNote')).toContainText('非负');
await page.getByLabel('文件类型',{exact:true}).selectOption('all');await page.locator('#tree button').filter({hasText:'quadpress_smpl.vtk'}).click();
await page.screenshot({path:'/private/tmp/dojo-rawprep-detail.png',fullPage:true});
if(errors.length)throw Error(errors.join('\n'));console.log('Rawprep detail UI checks passed');
}finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
