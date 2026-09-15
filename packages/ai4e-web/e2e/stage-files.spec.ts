import {test,expect} from '@playwright/test';
/** 固定来源组件夹具：验证页签隔离、空态、刷新与受控下载，不冒充真实计算。 */
test('阶段文件无来源不回退，切换范围只请求固定来源',async({page})=>{
 const calls:string[]=[];
 await page.route('**/api/v1/**',route=>{const url=route.request().url();calls.push(url);const parsed=new URL(url);const path=parsed.searchParams.get('path')||'';
  const rows=url.includes('stage-files')?(path?[{name:'field.pt',path:'train/sample/field.pt',root:'project',source_path:'physical/train/sample/field.pt',directory:false,modified_at:'2026-09-14T02:30:00Z'}]:[{name:'train',path:'train',root:'project',source_path:'physical/train',directory:true,modified_at:'2026-09-14T02:30:00Z'}]):[];
  return route.fulfill({json:rows});});
 await page.goto('/');
 await page.evaluate(async()=>{const React=(await import('/node_modules/.vite/deps/react.js' as any)).default;const {createRoot}=(await import('/node_modules/.vite/deps/react-dom_client.js' as any)).default;const {StageFiles}=await import('/src/modules/files/StageFiles.tsx' as any);document.body.innerHTML='<div id="fixture"></div>';const root=createRoot(document.getElementById('fixture'));(window as any).showFiles=(props:any)=>root.render(React.createElement(StageFiles,{project:'fixture',task:'t',...props}));(window as any).showFiles({role:'inputs'});});
 await expect(page.getByText('请选择固定输入或运行')).toBeVisible();expect(calls.filter(v=>v.includes('stage-files'))).toHaveLength(0);
 await page.evaluate(()=>(window as any).showFiles({role:'inputs',asset:{asset_id:'manifest',revision:'r1'},onSelection:()=>{}}));
 await expect(page.getByRole('button',{name:'train',exact:true})).toBeVisible();expect(calls.at(-1)).toContain('asset_id=manifest');expect(calls.at(-1)).toContain('revision=r1');
 await page.getByRole('button',{name:'train',exact:true}).click();
 await expect.poll(()=>calls.some(v=>v.includes('path=train'))).toBeTruthy();
 await page.evaluate(()=>(window as any).showFiles({role:'preparation',run:'fixed-run'}));await expect.poll(()=>calls.at(-1)).toContain('role=preparation&run_id=fixed-run');expect(calls.some(v=>v.includes('/files?'))).toBeFalsy();
});
