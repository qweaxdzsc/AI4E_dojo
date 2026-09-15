import {test,expect} from '@playwright/test';
import {inferenceFixture} from './inference-fixture';
test('2000样本分页、筛选全选及跨分片保留选择',async({page})=>{
 const state=await inferenceFixture(page,{completed:false});await page.goto('/projects/p/tasks/t/infer');await page.getByRole('checkbox',{name:'选择检查点 BEST · train0',exact:true}).check();const panel=page.locator('[data-region="samples"]');await panel.getByRole('tab',{name:/验证集/}).click();const start=Date.now();await panel.getByRole('checkbox',{name:/全选当前页/}).check();await expect(panel).toContainText('已选择 50 / 2002 个');expect(Date.now()-start).toBeLessThan(1000);
 await panel.getByRole('tab',{name:/训练集/}).click();await panel.getByRole('checkbox',{name:'选择样本 train_sample'}).check();await panel.getByRole('tab',{name:/测试集/}).click();await panel.getByRole('checkbox',{name:'选择样本 test_sample'}).check();await panel.getByRole('tab',{name:/验证集/}).click();await expect(panel.getByRole('checkbox',{name:'选择样本 sample_0001',exact:true})).toBeChecked();await panel.getByRole('textbox',{name:'搜索推理样本'}).fill('sample_00');await panel.getByRole('checkbox',{name:/全部筛选范围/}).check();await page.getByRole('button',{name:'开始计算',exact:true}).click();await expect.poll(()=>state.submitted.length).toBe(1);expect(state.submitted[0].sample_selection).toHaveLength(101);expect(new Set(state.submitted[0].sample_selection.map((s:any)=>s.split)).size).toBe(3);
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
