import {test,expect} from '@playwright/test';
import {inferenceFixture} from './inference-fixture';
import {mkdirSync,writeFileSync} from 'node:fs';
const evidence='/Users/zonghui/work/project_simulation/dojo_train/inference-ui-acceptance/result-views';
test('独立表格和坐标配置、聚合多选、样本身份及导出一致',async({page})=>{
 const state=await inferenceFixture(page);await page.setViewportSize({width:1672,height:941});await page.goto('/projects/p/tasks/t/infer');
 const table=page.locator('[data-region="table"]'),chart=page.locator('[data-region="chart"]');
 await expect(table.locator('tbody tr')).toHaveCount(5);
 await table.getByRole('button',{name:'配置',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('表格字段配置');
 for(const name of ['Max','Median']){const box=page.getByRole('checkbox',{name,exact:true});await box.click();await expect(box).not.toBeChecked();}
 await expect(page.getByRole('dialog')).toHaveCSS('transform','none');mkdirSync(evidence,{recursive:true});await page.waitForTimeout(350);await page.screenshot({animations:"disabled",path:evidence+'/table-checkpoint.png'});
 await page.getByRole('button',{name:'应用',exact:true}).click();await expect(table.locator('th')).toHaveCount(4);await expect(table).not.toContainText('Median');
 await chart.getByRole('button',{name:'配置',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('图表坐标配置');await expect(page.getByRole('combobox',{name:'图表 X 轴'})).toBeDisabled();await expect(page.getByRole('dialog')).not.toContainText('聚合方式');
 await expect(page.getByRole('dialog')).toHaveCSS('transform','none');await page.waitForTimeout(350);await page.screenshot({animations:"disabled",path:evidence+'/chart-checkpoint.png'});await page.getByRole('button',{name:'应用',exact:true}).click();
 await table.getByRole('button',{name:'配置',exact:true}).click();await page.getByRole('radio',{name:'样本对比',exact:true}).check();await expect(page.getByRole('dialog')).not.toContainText('聚合方式');await expect(page.getByRole('dialog')).toHaveCSS('transform','none');await page.waitForTimeout(350);await page.screenshot({animations:"disabled",path:evidence+'/table-sample.png'});await page.getByRole('button',{name:'应用',exact:true}).click();
 await expect(table.locator('tbody tr')).toHaveCount(4);await expect(table.locator('th')).toHaveCount(3);await expect(table).toContainText('训练集');await expect(table).toContainText('验证集');await expect(table).toContainText('same_sample');
 await chart.getByRole('button',{name:'配置',exact:true}).click();await expect(page.getByRole('dialog')).toContainText('样本');await expect(page.getByRole('dialog')).toHaveCSS('transform','none');await page.waitForTimeout(350);await page.screenshot({animations:"disabled",path:evidence+'/chart-sample.png'});await page.getByRole('button',{name:'取消',exact:true}).click();
 for(const name of ['散点图','柱状图','折线图'])await page.getByRole('button',{name,exact:true}).click();
 const download=page.waitForEvent('download');await page.getByRole('button',{name:'导出 CSV',exact:true}).click();await download;
 expect(state.submitted).toHaveLength(0);expect(state.exports[0].selection.view).toEqual({mode:'sample',checkpoint_id:'cp0',pairs:[{field_id:'surface:pressure:scalar',metric:'relative_l2'}],aggregations:['mean','p90']});
 await page.waitForTimeout(350);await page.screenshot({animations:"disabled",path:evidence+'/sample-view.png'});
});
test('无结果时也可打开两个配置弹窗并明确禁用应用',async({page})=>{
 await inferenceFixture(page,{empty:true,completed:false});await page.goto('/projects/p/tasks/t/infer');
 for(const region of ['table','chart']){await page.locator(`[data-region="${region}"]`).getByRole('button',{name:'配置',exact:true}).click();await expect(page.getByRole('button',{name:'应用',exact:true})).toBeDisabled();await page.getByRole('button',{name:'取消',exact:true}).click();}
 await page.locator('[data-region="chart"]').getByRole('button',{name:'配置',exact:true}).click();
 await expect(page.getByRole('switch',{name:'刻度'})).toBeVisible();
 await expect(page.getByRole('switch',{name:'网格线'})).toBeVisible();
 await expect(page.getByRole('switch',{name:'点数值'})).toBeVisible();
 await expect(page.getByRole('radiogroup',{name:'刻度疏密'})).toBeVisible();
 await page.getByRole('button',{name:'取消',exact:true}).click();
});

test('多个物理量指标成对选列、坐标多选及取消草稿',async({page})=>{
 const state=await inferenceFixture(page,{multiplePairs:true});await page.goto('/projects/p/tasks/t/infer');
 const table=page.locator('[data-region="table"]'),chart=page.locator('[data-region="chart"]');
 await expect(table.locator('tbody tr')).toHaveCount(5);await table.getByRole('button',{name:'配置',exact:true}).click();
 for(const name of ['Median','Max']){const box=page.getByRole('checkbox',{name,exact:true});await box.click();await expect(box).not.toBeChecked();}
 for(const name of ['mae','rmse']){const box=page.getByRole('dialog').getByRole('checkbox',{name,exact:true});await box.click();await expect(box).toBeChecked();}
 await page.getByRole('button',{name:'应用',exact:true}).click();await expect(table.locator('th')).toHaveCount(8);
 await expect(table).toContainText('Velocity-U · rmse · P90 (m/s)');
 await chart.getByRole('button',{name:'配置',exact:true}).click();await page.getByRole('combobox',{name:'图表 Y 轴字段'}).click();
 await page.locator('.ant-select-dropdown:visible .ant-select-item-option-content').getByText('Velocity-U · rmse · P90 (m/s)',{exact:true}).click();
 await page.getByRole('dialog').getByText('图表坐标配置',{exact:true}).click();await page.getByRole('button',{name:'应用',exact:true}).click();
 await expect(chart.locator('.infer-chart-legend')).toContainText('Velocity-U · rmse · P90 (m/s)');
 const headers=await table.locator('th').allTextContents();await table.getByRole('button',{name:'配置',exact:true}).click();await page.getByRole('radio',{name:'样本对比',exact:true}).click();await page.getByRole('button',{name:'取消',exact:true}).click();expect(await table.locator('th').allTextContents()).toEqual(headers);
 await table.getByRole('button',{name:'配置',exact:true}).click();for(const name of ['Mean','P90']){await page.getByRole('checkbox',{name,exact:true}).click();}await expect(page.getByRole('button',{name:'应用',exact:true})).toBeDisabled();await page.getByRole('button',{name:'取消',exact:true}).click();
 const bounds:any[]=[];
 for(const [width,height] of [[1672,941],[1440,900],[1920,1080]]){await page.setViewportSize({width,height});for(const region of ['table','chart']){await page.locator(`[data-region="${region}"]`).getByRole('button',{name:'配置',exact:true}).click();await page.waitForTimeout(350);await expect(page.getByRole('dialog')).toHaveCSS('transform','none');const box=await page.getByRole('dialog').boundingBox();bounds.push({viewport:{width,height},region,...box});expect(box!.x).toBeGreaterThanOrEqual(0);expect(box!.y+box!.height).toBeLessThan(height);await page.screenshot({animations:"disabled",path:`${evidence}/${region}-${width}.png`});await page.getByRole('button',{name:'取消',exact:true}).click();expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth)).toBeTruthy();}}writeFileSync(evidence+'/dialog-bounds.json',JSON.stringify(bounds,null,2));
 expect(state.submitted).toHaveLength(0);
});

const PREV_TABLE_HEIGHT=218,PREV_CHART_HEIGHT=194,PREV_SVG_HEIGHT=154;
test('指标表和折线图高度至少为原值两倍，图表显示选项可保存',async({page})=>{
 await inferenceFixture(page);await page.setViewportSize({width:1672,height:941});await page.goto('/projects/p/tasks/t/infer');
 const table=page.locator('[data-region="table"]'),chart=page.locator('[data-region="chart"]');
 await expect(table.locator('tbody tr')).toHaveCount(5);
 const tableBox=await table.boundingBox(),chartBox=await chart.boundingBox();
 expect(tableBox!.height).toBeGreaterThanOrEqual(PREV_TABLE_HEIGHT*2);
 expect(chartBox!.height).toBeGreaterThanOrEqual(PREV_CHART_HEIGHT*2);
 const svg=chart.locator('svg');
 const svgBox=await svg.boundingBox();
 expect(svgBox!.height).toBeGreaterThanOrEqual(PREV_SVG_HEIGHT*2);
 await expect(svg).toHaveAttribute('data-ticks','on');
 await expect(svg).toHaveAttribute('data-grid','on');
 await expect(svg).toHaveAttribute('data-point-labels','off');
 await chart.getByRole('button',{name:'配置',exact:true}).click();
 await expect(page.getByRole('switch',{name:'刻度'})).toBeVisible();
 await expect(page.getByRole('switch',{name:'网格线'})).toBeVisible();
 await expect(page.getByRole('switch',{name:'点数值'})).toBeVisible();
 await page.getByRole('switch',{name:'点数值'}).click();
 await page.getByRole('switch',{name:'网格线'}).click();
 await page.getByRole('radio',{name:'密',exact:true}).check();
 await page.getByRole('button',{name:'取消',exact:true}).click();
 await expect(svg).toHaveAttribute('data-point-labels','off');
 await expect(svg).toHaveAttribute('data-grid','on');
 await chart.getByRole('button',{name:'配置',exact:true}).click();
 await page.getByRole('switch',{name:'点数值'}).click();
 await page.getByRole('switch',{name:'网格线'}).click();
 await page.getByRole('radio',{name:'密',exact:true}).check();
 await page.getByRole('button',{name:'应用',exact:true}).click();
 await expect(svg).toHaveAttribute('data-point-labels','on');
 await expect(svg).toHaveAttribute('data-grid','off');
 await expect(svg).toHaveAttribute('data-tick-density','dense');
 await expect(svg.locator('.infer-point-label').first()).toBeVisible();
 await page.reload();
 await expect(page.locator('[data-region="table"] tbody tr')).toHaveCount(5);
 const restored=page.locator('[data-region="chart"] svg');
 await expect(restored).toHaveAttribute('data-point-labels','on');
 await expect(restored).toHaveAttribute('data-grid','off');
 await expect(restored).toHaveAttribute('data-tick-density','dense');
 await page.locator('[data-region="chart"]').getByRole('button',{name:'配置',exact:true}).click();
 await expect(page.getByRole('switch',{name:'点数值'})).toBeChecked();
 await expect(page.getByRole('switch',{name:'网格线'})).not.toBeChecked();
});
