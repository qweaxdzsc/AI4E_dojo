import {test,expect} from '@playwright/test';
import {inferenceFixture} from './inference-fixture';
test('进页即加载目录；2000样本分页、筛选全选及跨分片保留选择',async({page})=>{
 const state=await inferenceFixture(page,{completed:false});await page.goto('/projects/p/tasks/t/infer');const panel=page.locator('[data-region="samples"]');await expect(panel.getByRole('tab',{name:/评价集/})).toBeVisible();await expect(page.getByRole('checkbox',{name:'选择物理量 Pressure'})).toBeVisible();await expect(page.getByRole('checkbox',{name:'选择指标 L2 Error'})).toBeVisible();await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();await panel.getByRole('tab',{name:/评价集/}).click();const start=Date.now();await panel.getByRole('checkbox',{name:/全选当前页/}).check();await expect(panel).toContainText('已选择 50 / 2002 个');expect(Date.now()-start).toBeLessThan(1000);
 await panel.getByRole('tab',{name:/训练集/}).click();await panel.getByRole('checkbox',{name:'选择样本 train_sample'}).check();await panel.getByRole('tab',{name:/测试集/}).click();await panel.getByRole('checkbox',{name:'选择样本 test_sample'}).check();await panel.getByRole('tab',{name:/评价集/}).click();await expect(panel.getByRole('checkbox',{name:'选择样本 sample_0001',exact:true})).toBeChecked();await panel.getByRole('textbox',{name:'搜索推理样本'}).fill('sample_00');await panel.getByRole('checkbox',{name:/全部筛选范围/}).check();await page.getByRole('button',{name:'开始计算',exact:true}).click();await expect.poll(()=>state.submitted.length).toBe(1);expect(state.submitted[0].sample_selection).toHaveLength(101);expect(new Set(state.submitted[0].sample_selection.map((s:any)=>s.split)).size).toBe(3);
});


test('检查点、物理量和指标提供全选',async({page})=>{
 await inferenceFixture(page,{completed:false});await page.goto('/projects/p/tasks/t/infer');
 await page.getByRole('button',{name:'全选检查点'}).click();
 await expect(page.locator('[data-region="checkpoints"]')).toContainText('已选择 12 / 12 个');
 await page.getByRole('checkbox',{name:'全选物理量'}).check();
 await expect(page.locator('[data-region="fields"]')).toContainText('已选择 4 / 4 个');
 await page.getByRole('checkbox',{name:'全选指标'}).check();
 await expect(page.locator('[data-region="metrics"]')).toContainText('已选择 11 / 11 个');
});

test('检查点按训练运行收成树，选父级等于该 run 下叶子',async({page})=>{
 await inferenceFixture(page,{completed:false});await page.goto('/projects/p/tasks/t/infer');
 const panel=page.locator('[data-region="checkpoints"]');
 await expect(panel.locator('[data-run-parent="train0"]')).toContainText('训练运行 · train0');
 await expect(panel.locator('[data-run-parent="train1"]')).toContainText('训练运行 · train1');
 await expect(panel.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true})).toBeVisible();
 await expect(panel.getByRole('checkbox',{name:'选择检查点 ckpt_127000 · train0',exact:true})).toBeVisible();
 await expect(panel.getByRole('checkbox',{name:'选择检查点 ckpt_122000 · train1',exact:true})).toBeVisible();
 await panel.getByRole('checkbox',{name:'选择训练运行 train0'}).check();
 await expect(panel).toContainText('已选择 6 / 12 个');
 await expect(panel.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true})).toBeChecked();
 await page.getByRole('button',{name:'全选检查点'}).click();
 await expect(panel).toContainText('已选择 12 / 12 个');
});

test('检查点目录不一致时提示并回退先选后加载',async({page})=>{
 await inferenceFixture(page,{completed:false,divergent:true});await page.goto('/projects/p/tasks/t/infer');
 await expect(page.getByText('各 Checkpoint 的样本、物理量或指标不一致')).toBeVisible();
 await expect(page.getByText('选择检查点后读取样本')).toBeVisible();
 await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();
 await expect(page.getByRole('checkbox',{name:'选择样本 test_sample'})).toBeVisible();
});

test('某一检查点目录失败时提示回退且不误报数据根',async({page})=>{
 await inferenceFixture(page,{completed:false,failSecond:true});await page.goto('/projects/p/tasks/t/infer');
 await expect(page.getByText('各 Checkpoint 的样本、物理量或指标不一致')).toBeVisible();
 await expect(page.getByText('文件不存在或数据根未配置')).toHaveCount(0);
 await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();
 await expect(page.getByRole('checkbox',{name:'选择样本 test_sample'})).toBeVisible();
});

test('过期批次记忆不误报数据根未配置',async({page})=>{
 await inferenceFixture(page,{completed:false,stale:true});await page.goto('/projects/p/tasks/t/infer');
 await expect(page.getByRole('checkbox',{name:'选择样本 test_sample'})).toBeVisible();
 await expect(page.getByText('文件不存在或数据根未配置')).toHaveCount(0);
});

test('旧模板明确关闭高级选择并保留原推理请求',async({page})=>{
 const state=await inferenceFixture(page,{completed:false,legacy:true});
 await page.goto('/projects/p/tasks/t/infer');
 await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();
 await expect(page.getByText('旧 post 模板按原字段和指标执行；自定义选择需要独立 infer 模板。历史结果仍可查看和下载。')).toBeVisible();
 await expect(page.locator('[data-region="fields"] input[type="checkbox"]').first()).toBeDisabled();
 await page.getByRole('checkbox',{name:'选择样本 test_sample',exact:true}).check();
 await page.getByRole('button',{name:'开始计算',exact:true}).click();
 await expect.poll(()=>state.submitted.length).toBe(1);
 expect(state.submitted[0]).not.toHaveProperty('fields');
 expect(state.submitted[0]).not.toHaveProperty('metrics');
});
