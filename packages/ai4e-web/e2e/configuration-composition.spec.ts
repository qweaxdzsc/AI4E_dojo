import { test, expect } from '@playwright/test';

/** 明确的传输夹具验证编辑请求；真实Python保存与运行由集成用例覆盖。 */
test('四类配置差异保留空值、删除及包含点的字段名', async ({page}) => {
  await page.goto('/');
  const result = await page.evaluate(async () => {
    const {configurationEdits} = await import('/src/infrastructure/configuration/edits.ts' as any);
    return [
      configurationEdits({format:'pt',workers:1}, {formats:['pt','zarr'],workers:4}),
      configurationEdits({domains:{surface:{features:{'p.mean':'p'}}},normalization:{materialize:true}}, {domains:{surface:{features:{}}},normalization:{materialize:false}}),
      configurationEdits({sampling:{seed:1},parameters:{dim:192}}, {sampling:{seed:0},parameters:{dim:192}}),
      configurationEdits({ema_decay:0.9,max_epochs:2}, {ema_decay:null,max_epochs:3}),
    ];
  });
  expect(result[0]).toEqual({edited_paths:[['workers'],['formats']],removed_paths:[['format']]});
  expect(result[1].edited_paths).toEqual([['domains','surface','features'],['normalization','materialize']]);
  expect(result[2].edited_paths).toEqual([['sampling','seed']]);
  expect(result[3].edited_paths).toEqual([['ema_decay'],['max_epochs']]);
});

test('训练保存只提交编辑路径且后续检查使用新修订', async ({page}) => {
  let revision='r1', values:any={max_epochs:2,learning_rate:0.001,betas:[0.9,0.999]};
  const saves:any[]=[]; const operations:any[]=[];
  await page.route('**/api/v1/**', async route => {
    const req=route.request(), url=new URL(req.url());
    if(url.pathname.endsWith('/configuration')) {
      if(req.method()==='PUT') { const body=req.postDataJSON();saves.push(body); values=body.values;revision='r2';return route.fulfill({json:{revision,config:{train:values}}}); }
      return route.fulfill({json:{revision,stage:'train',values,capabilities:{}}});
    }
    if(url.pathname.endsWith('/stages/train/operations')) {operations.push(req.postDataJSON());return route.fulfill({json:{operation_id:'check',status:'succeeded',result:{valid:true}}});}
    return route.fulfill({json:[]});
  });
  await page.goto('/');
  await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageWorkbench}=await import('/src/modules/stages/StageWorkbench.tsx' as any);document.body.innerHTML='<div id="test-root"></div>';createRoot(document.getElementById('test-root')!).render(React.createElement(StageWorkbench,{project:'p',task:'t',stage:'train'}));});
  await page.locator('.configuration-field').filter({has:page.getByText('训练轮数',{exact:true})}).getByRole('spinbutton').fill('3');
  await page.getByRole('button',{name:'预检',exact:true}).click();
  await expect(page.getByText('配置与交接检查通过',{exact:true})).toBeVisible();
  expect(saves).toHaveLength(1);
  expect(saves[0].edited_paths).toEqual([['max_epochs']]);
  expect(saves[0].removed_paths).toEqual([]);
  expect(operations[0].expected_revision).toBe('r2');
});
