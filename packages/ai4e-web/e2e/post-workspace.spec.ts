import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';
for(const width of [1440,1920])test(`三个Tab与指标布局 ${width}`,async({page})=>{
 await page.setViewportSize({width,height:1000});const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post');
 const tabs=page.getByRole('tablist',{name:'后处理视图'});await expect(tabs.getByRole('tab')).toHaveText(['指标','结果文件','三维物理场可视化']);
 await expect(page.getByRole('button',{name:'计算指标',exact:true})).toBeEnabled();await page.getByRole('button',{name:'计算指标',exact:true}).click();
 await expect(page.getByRole('cell',{name:'0.500000'}).first()).toBeVisible();expect(state.submitted).toHaveLength(1);expect(state.creates).toBe(0);
 await expect(page.getByRole('combobox',{name:'指标推理批次',includeHidden:true})).toBeVisible();await tabs.getByRole('tab',{name:'结果文件',exact:true}).click();await expect(page.getByRole('combobox',{name:'指标推理批次',includeHidden:true})).toBeHidden();await expect(page.getByRole('button',{name:'批量加入三维物理场',exact:true})).toBeVisible();
 const tree=await page.locator('.post-result-tree').boundingBox(),preview=await page.locator('.post-file-preview').boundingBox();expect(tree!.x+tree!.width).toBeLessThan(preview!.x);expect(tree!.width/preview!.width).toBeCloseTo(2/3,1);
});


test('同名样本按分片独立选择',async({page})=>{
 const state=await postFixture(page,{sameSampleAcrossSplits:true});
 await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('combobox',{name:'指标样本',exact:true}).click();
 await expect(page.getByRole('option',{name:'训练集 · same-car',exact:true})).toHaveCount(1);
 await expect(page.getByRole('option',{name:'测试集 · same-car',exact:true})).toHaveCount(1);
 await page.locator('.ant-select-item-option').filter({hasText:'测试集 · same-car'}).click();
 await page.getByRole('combobox',{name:'指标样本',exact:true}).press('Escape');
 await page.getByRole('button',{name:'计算指标',exact:true}).click();
 await expect.poll(()=>state.submitted.length).toBe(1);
 expect(state.submitted[0].results.map((r:any)=>r.id)).toEqual(['batch1a']);
});
