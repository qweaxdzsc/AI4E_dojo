import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';
test('空结果说明训练写出或推理来源',async({page})=>{
 await postFixture(page,{empty:true});await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('tab',{name:'结果文件',exact:true}).click();
 await expect(page.getByText('暂无训练运行、平台数据集或推理固定结果')).toBeVisible();
});

test('结果文件列出平台数据集文件夹',async({page})=>{
 await postFixture(page,{processed:true});await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('tab',{name:'结果文件',exact:true}).click();
 await expect(page.getByRole('button',{name:'平台数据集 · shapenet_car2'})).toBeVisible();
 await page.getByRole('button',{name:'平台数据集 · shapenet_car2'}).click();
 await expect(page.getByRole('button',{name:'param1/1dc757e77f3cfad0253c03b7df20edd5'})).toBeVisible();
});

test('无写出的训练运行仍显示 run 文件夹',async({page})=>{
 await postFixture(page,{trainEmpty:true});await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('tab',{name:'结果文件',exact:true}).click();
 await expect(page.getByRole('button',{name:'训练运行 · train1ab'})).toBeVisible();
 await page.getByRole('button',{name:'训练运行 · train1ab'}).click();
 await expect(page.getByRole('button',{name:'没有写出预测或网格'})).toBeVisible();
});

test('搜索保留祖先、预览独立、批量追加',async({page})=>{const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post?batch=batch1&sample=a');
 await expect(page.locator('.artifact-file-table')).toBeVisible();await page.getByLabel('搜索结果文件').fill('values.json');await expect(page.locator('.folderrow').first()).toBeVisible();
 await page.getByRole('button',{name:'预览 values.json',exact:true}).first().click();await expect(page.getByRole('region',{name:'文件预览'})).toContainText('values.json');expect(state.creates).toBe(0);
 await page.getByLabel('搜索结果文件').fill('');await page.getByRole('checkbox',{name:'选择 pressure.vtp',exact:true}).first().check();await page.getByRole('button',{name:/批量加入三维物理场/}).click();await expect(page.locator('.phys-host iframe')).toBeVisible();expect(state.creates).toBe(1);expect(state.appends).toBe(1);
});

test('未展开时搜索命中祖先，换批次只带筛选重取当前层',async({page})=>{
 const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post');
 await expect(page.getByRole('tab',{name:'结果文件',exact:true})).toHaveAttribute('aria-selected','true');
 await expect(page.getByRole('button',{name:'batch1',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'预览 values.json'})).toHaveCount(0);
 await page.getByLabel('搜索结果文件').fill('values.json');
 await expect(page.getByRole('button',{name:'预览 values.json'}).first()).toBeVisible();
 await expect(page.locator('.folderrow').first()).toBeVisible();
 await page.getByLabel('搜索结果文件').fill('');
 await page.locator('.post-file-filters .ant-select').first().click();
 await page.locator('.ant-select-item-option').filter({hasText:'批次一'}).click();
 await expect.poll(()=>state.fileQueries.some(q=>q.includes('batch=batch1'))).toBeTruthy();
});
