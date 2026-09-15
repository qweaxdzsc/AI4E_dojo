import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';

/** 参考图布局门禁：紧凑行高、独立勾选列、标题导入和浮层生命周期。 */
for(const width of [1440,1920])test(`参考图布局与浮层 ${width}`,async({page})=>{
 await page.setViewportSize({width,height:1000});await postFixture(page);await page.goto('/projects/p/tasks/t/post');
 await page.getByRole('button',{name:'计算指标',exact:true}).click();
 const row=page.locator('.post-metric-table .ant-table-tbody tr.ant-table-row').first();await expect(row).toBeVisible();
 expect((await row.boundingBox())!.height).toBeLessThanOrEqual(42);
 const table=await page.locator('.post-metric-table').boundingBox(),bar=await page.locator('.post-metric-config').boundingBox();expect(table!.y-bar!.y).toBeLessThan(190);
 await page.getByRole('button',{name:'导出 ▾',exact:true}).click();await expect(page.getByRole('menuitem',{name:'导出 CSV',exact:true})).toBeVisible();
 await page.getByRole('tab',{name:'结果文件',exact:true}).click();await expect(page.getByRole('menuitem',{name:'导出 CSV',exact:true})).not.toBeVisible();
 const header=page.locator('.post-result-tree>header');await expect(header.getByRole('button',{name:'批量加入三维物理场',exact:true})).toBeVisible();
 const tree=await page.locator('.post-result-tree').boundingBox(),preview=await page.locator('.post-file-preview').boundingBox();expect(tree!.width/preview!.width).toBeCloseTo(2/3,1);
 const checks=await page.locator('.artifact-file-table tbody .artifact-select').evaluateAll(nodes=>nodes.map(n=>Math.round(n.getBoundingClientRect().left)));expect(new Set(checks).size).toBe(1);
 const overflow=await page.locator('.artifact-tree-scroll').evaluate(n=>n.scrollWidth>n.clientWidth+1);expect(overflow).toBe(false);
 await page.getByRole('button',{name:'预览 values.json',exact:true}).first().click();await page.getByRole('button',{name:'放大文件预览',exact:true}).click();await expect(page.locator('.post-file-preview')).toHaveClass(/maximized/);
 await page.getByRole('button',{name:'关闭文件预览',exact:true}).click();await expect(page.locator('.post-file-preview')).not.toHaveClass(/maximized/);
});
