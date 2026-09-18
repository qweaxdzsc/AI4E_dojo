import type {Page} from '@playwright/test';
/** HTTP契约夹具，不代表真实CFD计算；用于布局、选择与会话请求断言。 */
export async function postFixture(page:Page,{sameSampleAcrossSplits=false,empty=false,genericBatch=false,trainEmpty=false,processed=false}={}){
 const state={creates:0,closes:0,appends:0,fileViews:0,fileQueries:[] as string[],submitted:[] as any[],visible:[] as boolean[]};
 const field={id:'surface:pressure:scalar',domain:'surface',field:'pressure',component:'scalar',association:'point',label:'surface / pressure',default:true};
 const items=['batch1','batch2'].flatMap(batch_id=>['a','b'].map(sample=>({id:batch_id+sample,revision:'r1',batch_id,run_id:batch_id+'run',sample:sameSampleAcrossSplits?'same-car':sample,split:sameSampleAcrossSplits?(sample==='a'?'train':'test'):undefined,checkpoint:{name:'last.pt',epoch:2},fields:[field],evaluable:true,status:'succeeded'})));
 const files=items.flatMap(i=>['pressure.vtp','values.json'].map(name=>({id:i.id+name,name,tree_path:`${i.batch_id}/last.pt/${i.sample}/${name}`,size:512,modified_at:'2026-09-15T08:00:00Z',batch_id:i.batch_id,sample:i.sample,result_id:i.id,run_id:i.run_id,visualizable:name.endsWith('.vtp'),ref:{project_id:'p',task_id:'t',asset_id:i.id+name,revision:'r1'}})));
 await page.route('**/api/v1/**',async route=>{const req=route.request(),u=new URL(req.url()),path=u.pathname;let json:any={};
  if(path==='/api/v1/projects')json=[{id:'p',name:'项目'}];else if(path.endsWith('/tasks/t'))json={id:'t',name:'任务',case_id:'shapenet_car_abupt',stage_summary:{infer:{status:'succeeded'}}};else if(path.endsWith('/tasks'))json=[{id:'t',name:'任务'}];else if(path.endsWith('/datasets'))json=processed?[{name:'shapenet_car2',status:'available',origin_task:'t'}]:[];else if(path.endsWith('/runs'))json=trainEmpty?[{id:'train1abcd',status:'succeeded',stages:['train'],created_at:'2026-09-17T10:00:00+00:00'}]:[];
  else if(path.endsWith('/post/results')){
   const view=u.searchParams.get('view')||'catalog',q=u.searchParams.get('query')||'',directory=u.searchParams.get('directory')||'',sample=u.searchParams.get('sample')||'',batch=u.searchParams.get('batch')||'';
   if(view==='catalog')json={items:empty||trainEmpty||processed?[]:items,files:[],batches:empty||trainEmpty?[]:processed?[{id:'dataset:shapenet_car2',name:'平台数据集 · shapenet_car2',status:'succeeded'}]:genericBatch?[{id:'batch1',name:'批量推理',created_at:'2026-09-15T08:00:00Z'},{id:'batch2',name:'批次二'}]:[{id:'batch1',name:'批次一'},{id:'batch2',name:'批次二'}],errors:[],total:0};
   else {
    state.fileViews++;
    state.fileQueries.push(u.search);
    if(processed){
     const prefix='平台数据集 · shapenet_car2';
     const sample='param1/1dc757e77f3cfad0253c03b7df20edd5';
     const sampleDir=prefix+'/param1／1dc757e77f3cfad0253c03b7df20edd5';
     const listed=!directory?[{id:'dir:'+prefix,name:prefix,tree_path:prefix,directory:true,batch_id:'dataset:shapenet_car2',kind:'dataset',status:'succeeded'}]:directory===prefix?[{id:'dir:'+sampleDir,name:sample,tree_path:sampleDir,directory:true,sample}]:[];
     json={items:[],files:listed,batches:[],errors:[],total:listed.length};
    }else if(trainEmpty){
     const prefix='训练运行 · train1ab';
     const note=prefix+'/没有写出预测或网格';
     const listed=!directory?[{id:'dir:'+prefix,name:prefix,tree_path:prefix,directory:true,batch_id:'train:train1abcd',run_id:'train1abcd',status:'succeeded',kind:'train',modified_at:'2026-09-17T10:00:00+00:00'}]:directory===prefix?[{id:'dir:'+note,name:'没有写出预测或网格',tree_path:note,directory:true,empty:true,run_id:'train1abcd'}]:[];
     json={items:[],files:listed,batches:[],errors:[],total:listed.length};
    }else{
    const picked=empty?[]:files.filter(f=>(!batch||f.batch_id===batch)&&(!sample||f.sample===sample)&&(!q||f.tree_path.toLowerCase().includes(q.toLowerCase()))&&(!directory||f.tree_path===directory||f.tree_path.startsWith(directory+'/'))).map(f=>{
     if(q||directory||sample)return {...f,ref:undefined,root:'project',path:f.tree_path,source_path:f.tree_path};
     const first=f.tree_path.split('/')[0];
     return {id:'dir:'+first,name:first,tree_path:first,directory:true,batch_id:f.batch_id};
    });
    const unique=q||directory||sample?picked:[...new Map(picked.map(f=>[f.id,f])).values()];
    json={items:[],files:unique,batches:[],errors:[],total:unique.length};
    }
   }
  }
  else if(path.endsWith('/assets')&&req.method()==='POST')json={project_id:'p',asset_id:'reg',revision:'r1',task_id:'t'};
  else if(path.endsWith('/metrics/catalog'))json={metrics:[{id:'relative_l2',label:'相对 L2'},{id:'rmse',label:'RMSE'},{id:'mse',label:'MSE'},{id:'mae',label:'MAE'},{id:'r2',label:'R²'}]};
  else if(path.endsWith('/metric-jobs')&&req.method()==='POST'){const body=req.postDataJSON();state.submitted.push(body);json={id:'job',status:'succeeded',created_at:'2026-09-15T08:00:00Z',completed:2,total:2,failed:0,request:{...body,fields:[field]},rows:items.slice(0,2).map(i=>({...i,id:i.id+field.id,field_id:field.id,field:field.field,domain:field.domain,component:'scalar',values:{mse:.5,mae:.5,rmse:.707,relative_l2:.1},status:'succeeded'}))};}
  else if(path.endsWith('/metric-jobs'))json={items:[]};else if(path.endsWith('/visualizations'))json={items:[]};
  else if(path.endsWith('/sessions')&&req.method()==='POST'){state.creates++;json={session_id:'session',embed_url:'/post-test-frame',status:'ready'};}
  else if(path.endsWith('/sessions/session')&&req.method()==='DELETE'){state.closes++;json={status:'closed'};}
  else if(path.endsWith('/sessions/session/sources')){state.appends++;json={added:req.postDataJSON().sources.length};}
  else if(path.endsWith('/previews/operations'))json={operation_id:'op',status:'succeeded',result:req.postDataJSON().options?{kind:'text',lines:['真实接口夹具'],fields:[]}:{}};
  await route.fulfill({json});
 });
 await page.route('**/post-test-frame',route=>route.fulfill({contentType:'text/html',body:'<html><body><h1>物理场测试视口</h1><input aria-label="相机状态" value="初始"/><script>window.addEventListener("message",e=>{if(e.data.type==="ai4e-vis:visibility")document.body.dataset.visible=e.data.visible;});window.parent.postMessage({type:"ai4e-vis:ready"},location.origin);</script></body></html>'}));
 return state;
}
