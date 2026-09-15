import {test,expect} from '@playwright/test';
import {postFixture} from './post-fixture';
test('搜索保留祖先、预览独立、批量追加',async({page})=>{const state=await postFixture(page);await page.goto('/projects/p/tasks/t/post?batch=batch1&sample=a');
 await expect(page.locator('.artifact-file-table')).toBeVisible();await page.getByLabel('搜索结果文件').fill('values.json');await expect(page.locator('.folderrow').first()).toBeVisible();
 await page.getByRole('button',{name:'预览 values.json',exact:true}).first().click();await expect(page.getByRole('region',{name:'文件预览'})).toContainText('values.json');expect(state.creates).toBe(0);
 await page.getByLabel('搜索结果文件').fill('');await page.getByRole('checkbox',{name:'选择 pressure.vtp',exact:true}).first().check();await page.getByRole('button',{name:/批量加入三维物理场/}).click();await expect(page.locator('.phys-host iframe')).toBeVisible();expect(state.creates).toBe(1);expect(state.appends).toBe(1);
});
