import type { Page } from '@playwright/test';
/** 仅用于界面密度与传输协议验收，不作为真实计算证据。 */
export async function inferenceFixture(page:Page,{completed=true,samples=2000,empty=false,longNames=false,status="succeeded",legacy=false}={}) {
 const state={submitted:[] as any[],exports:[] as any[],checks:[] as any[],queries:0};
 const cps=Array.from({length:12},(_,i)=>({id:`cp${i}`,run_id:`train${i}`,name:longNames?"很长的检查点名称_".repeat(10)+i:i===0?'BEST':`ckpt_${128000-i*1000}`,revision:`sha${i}`,epoch:i+1,updates:128000-i*1000,size:2048,status:'succeeded',created_at:`2026-09-15T08:${String(20-i).padStart(2,'0')}:00Z`,compatibility:{status:'compatible'},preparation:{digest:'prepared'},evaluation:{value:.000122+i*.00001,metric:'loss',split:'validation',direction:'min',protocol:'same'}}));
 const fields=['Pressure','Velocity-U','Velocity-V','Velocity-W'].map((label,i)=>({id:i?`volume:velocity:${i-1}`:'surface:pressure:scalar',label,domain:i?'volume':'surface',field:i?'velocity':'pressure',component:i?String(i-1):'scalar',category:'流体',unit:null,available:true,evaluable:true,default:true}));
 const metrics=['relative_l2','mae','rmse','max_abs_error','r2','mse','relative_mae','mean_relative_error','mape','prediction_seconds','throughput'].map((id,i)=>({id,label:['L2 Error','MAE','RMSE','Max Error','R²','MSE','相对 MAE','平均逐点相对误差','MAPE','预测耗时','预测吞吐量'][i],category:i>8?'性能指标':i===4?'统计指标':'误差指标',formula:'由后台提供的指标公式',default:i<5,scope:i>8?'sample':'field',unit_rule:'field'}));
 const partitions={train:['train_sample'],validation:Array.from({length:samples},(_,i)=>(longNames?"很长的中文样本路径/".repeat(12):"")+`sample_${String(i+1).padStart(4,'0')}`),test:['test_sample']};
 const statistics=cps.slice(0,5).map((c,i)=>({checkpoint_id:c.id,checkpoint:c.name,split:'validation',field_id:fields[0].id,field:'Pressure',metric:'relative_l2',unit:'1',mean:(3.21+i)*.0001,median:(2.12+i)*.0001,p90:(6.12+i)*.0001,max:.00123+i*.0001,valid:samples,expected:samples,undefined:0,complete:true,prediction_seconds:18.4+i/10,throughput:100}));
 let batch:any=completed?{id:'batch',name:'已完成的验证批次',status,total:10,completed:status==='succeeded'?10:3,children:[]}:undefined;
 await page.addInitScript(({completed})=>{if(completed)sessionStorage.setItem('dojo.infer.p.t','batch');},{completed});
 await page.route('**/api/v1/**',async route=>{const req=route.request(),path=new URL(req.url()).pathname;let json:any={};
 if(path==='/api/v1/projects')json=[{id:'p',name:'abc'}];else if(path.endsWith('/tasks/t'))json={id:'t',name:'as',case_id:'shapenet_car_abupt',created_by:'zonghui',version_id:'53d3cdel4',stage_summary:{rawprep:{status:'succeeded'}}};else if(path.endsWith('/tasks'))json=[{id:'t',name:'as'}];else if(path.endsWith('/runs'))json=[];
 else if(path.endsWith('/inference/checkpoints'))json={items:empty?[]:cps,device_options:[{id:'mps',label:'MPS',busy:false},{id:'cpu',label:'CPU',busy:false}],revision:'config'};
 else if(path.endsWith('/inference/samples'))json={partitions,fields,metrics,selection_supported:!legacy,preparation:{digest:'prepared'}};
 else if(path.endsWith('/inference/check')){state.checks.push(req.postDataJSON());json={valid:true};}
 else if(path.endsWith('/batches')&&req.method()==='POST'){state.submitted.push(req.postDataJSON());batch={id:'batch',name:'推理',status:'succeeded',total:10,completed:10,children:[]};json=batch;}
 else if(path.endsWith('/batches'))json={items:batch?[batch]:[]};else if(path.endsWith('/results')){state.queries++;json={items:[],statistics:batch?statistics:[],records:[],comparison:{status:'comparable'}};}
 else if(path.endsWith('/batches/batch'))json=batch;
 else if(path.endsWith('/exports')){state.exports.push(req.postDataJSON());json={name:'results.'+req.postDataJSON().format,ref:{asset_id:'export',revision:'r1'}};}
 else if(path.includes('/assets/export/content')){await route.fulfill({contentType:'text/csv',headers:{'Content-Disposition':'attachment; filename=results.csv'},body:'checkpoint,mean\nBEST,.000321'});return;}
 await route.fulfill({json});});return state;
}
