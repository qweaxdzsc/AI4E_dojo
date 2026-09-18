import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';
for(const width of [1440,1920])test(`两个Tab与结果文件默认布局 ${width}`,async({page})=>{
 await page.setViewportSize({width,height:1000});const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post');
 const tabs=page.getByRole('tablist',{name:'后处理视图'});await expect(tabs.getByRole('tab')).toHaveText(['结果文件','三维物理场可视化']);
 const filesTab=tabs.getByRole('tab',{name:'结果文件',exact:true});
 const visTab=tabs.getByRole('tab',{name:'三维物理场可视化',exact:true});
 await expect(filesTab).toHaveCSS('font-size','12px');
 await expect(visTab).toHaveCSS('font-size','12px');
 const filesBox=await filesTab.boundingBox(),visBox=await visTab.boundingBox();
 expect(filesBox!.height).toBeLessThanOrEqual(30);
 expect(visBox!.height).toBeLessThanOrEqual(30);
 await expect(page.getByRole('tab',{name:'指标',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'计算指标',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'批量加入三维物理场',exact:true})).toBeVisible();
 await expect(page.getByRole('combobox',{name:'结果文件批次',includeHidden:true})).toBeVisible();
 const tree=await page.locator('.post-result-tree').boundingBox(),preview=await page.locator('.post-file-preview').boundingBox();expect(tree!.x+tree!.width).toBeLessThan(preview!.x);expect(tree!.width/preview!.width).toBeCloseTo(2/3,1);
 expect(state.fileViews).toBeGreaterThan(0);expect(state.creates).toBe(0);
});

test('旧指标深链接落到结果文件',async({page})=>{
 await postFixture(page);
 await page.goto('/projects/p/tasks/t/post?tab=metrics&batch=batch1&sample=a');
 await expect(page.getByRole('tab',{name:'结果文件',exact:true})).toHaveAttribute('aria-selected','true');
 await expect(page.getByRole('tab',{name:'指标',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'计算指标',exact:true})).toHaveCount(0);
 await expect(page.getByRole('button',{name:'批量加入三维物理场',exact:true})).toBeVisible();
 await expect(page.locator('.artifact-file-table')).toBeVisible();
});

test('旧批量推理按创建时间展示 infer 身份',async({page})=>{
 await postFixture(page,{genericBatch:true});
 await page.goto('/projects/p/tasks/t/post');
 await page.locator('.post-file-filters .ant-select').first().click();
 const options=page.locator('.ant-select-dropdown:visible .ant-select-item-option');
 await expect(options.filter({hasText:/infer-\d{8}-\d{6}/})).toHaveCount(1);
 await expect(options.filter({hasText:'批次二'})).toHaveCount(1);
 await expect(options.filter({hasText:'批量推理'})).toHaveCount(0);
});
