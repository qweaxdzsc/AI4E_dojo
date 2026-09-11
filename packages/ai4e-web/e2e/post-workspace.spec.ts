import {test,expect} from '@playwright/test';

/** 后处理页对照整合 HTML 的页签与三栏，只用真实运行入口。 */
test('后处理页签、配置条与三维栏可操作',async({page,request})=>{
 const api=process.env.DOJO_API_URL||'http://127.0.0.1:8002';
 const p=process.env.DOJO_POST_PROJECT||'ae6834dbf6cc44b58371b68d96f05a39';
 const t=process.env.DOJO_POST_TASK||'3092ee50ddaa46b282c373cd01ed38a0';
 const probe=await request.get(`${api}/api/v1/projects/${p}/tasks/${t}`);
 test.skip(!probe.ok(),'本机没有可用的后处理任务');
 await page.setViewportSize({width:1440,height:1000});
 await page.goto(`/projects/${p}/tasks/${t}/6`);
 await expect(page.getByRole('heading',{name:'后处理',exact:true})).toBeVisible();
 await expect(page.getByText('在管线浏览器中选择结果，设置显示与过滤器；同时查看指标和图表。')).toBeVisible();
 await expect(page.getByRole('button',{name:'检查配置与交接',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'保存配置',exact:true})).toBeVisible();
 await expect(page.getByRole('button',{name:'运行后处理',exact:true})).toBeVisible();
 await expect(page.locator('.post-shell')).toBeVisible();
 await expect(page.locator('.post-config')).toBeVisible();
 await expect(page.locator('.post-tabs [role=tab]')).toHaveCount(3);
 await expect(page.getByRole('combobox',{name:'后处理运行',exact:true})).toBeVisible();
 await expect(page.getByRole('combobox',{name:'train.preparation',exact:true})).toBeVisible();
 await expect(page.getByRole('combobox',{name:'post.checkpoint',exact:true})).toBeVisible();
 await expect(page.getByText('结果文件',{exact:true})).toBeVisible();
 await expect(page.getByText('三维可视化窗口',{exact:true}).or(page.getByText('可视化视图',{exact:true}))).toBeVisible();
 await page.getByRole('tab',{name:'指标数据',exact:true}).click();
 await expect(page.locator('.metric-data-table')).toBeVisible();
 await page.getByRole('tab',{name:'图表',exact:true}).click();
 await expect(page.locator('.post-chart-grid>.ant-card')).toHaveCount(4);
 await expect(page.getByRole('button',{name:'暂无记录',exact:true})).toHaveCount(2);
 await page.getByRole('tab',{name:'结果可视化',exact:true}).click();
 await expect(page.getByRole('button',{name:'将所选文件加入场景',exact:true})).toBeVisible();
});
