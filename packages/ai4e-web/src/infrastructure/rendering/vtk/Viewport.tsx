import {useEffect,useRef,useState} from 'react';
import vtkGenericRenderWindow from '@kitware/vtk.js/Rendering/Misc/GenericRenderWindow';
import vtkPolyData from '@kitware/vtk.js/Common/DataModel/PolyData';
import vtkDataArray from '@kitware/vtk.js/Common/Core/DataArray';
import vtkMapper from '@kitware/vtk.js/Rendering/Core/Mapper';
import vtkCellPicker from '@kitware/vtk.js/Rendering/Core/CellPicker';
import vtkPointPicker from '@kitware/vtk.js/Rendering/Core/PointPicker';
import vtkActor from '@kitware/vtk.js/Rendering/Core/Actor';
import vtkColorTransferFunction from '@kitware/vtk.js/Rendering/Core/ColorTransferFunction';
import '@kitware/vtk.js/Rendering/Profiles/Geometry';
import {decodeBuffer,acquireBuffer,releaseBuffer} from '../../assets/binary';
/** VTK 运行时与业务状态隔离，纯显示变化不重建几何。 */
export function VtkViewport({manifest,url,field,component='magnitude',range,representation,opacity,onCamera,camera,onError,command,onImage,onPick}:any){
 const [generation,setGeneration]=useState(0),[contextLost,setContextLost]=useState(false);
 const fieldRef=useRef(field);fieldRef.current=field;const latestCamera=useRef(camera);latestCamera.current=camera;
 const cameraCallback=useRef(onCamera),pickCallback=useRef(onPick);cameraCallback.current=onCamera;pickCallback.current=onPick;
 const host=useRef<HTMLDivElement>(null),runtime=useRef<any>(null),synchronizing=useRef(false),[ready,setReady]=useState(0);
 useEffect(()=>{
  if(!host.current)return;
  const descriptors=[...(manifest.geometry_buffers||[]),...(manifest.topology_buffers||[]),...(manifest.fields||[]).map((f:any)=>f.buffer)];if(descriptors.reduce((n:number,b:any)=>n+(b?.byte_length||0),0)>128*1024*1024){onError?.(new Error('单窗口显示资产超过 128 MiB 预算'));return;}
  let disposed=false;const held=new Map<string,Promise<ArrayBuffer>>();const load=(path:string)=>{const key=url(path);if(!held.has(key))held.set(key,acquireBuffer(key));return held.get(key)!;};const window=vtkGenericRenderWindow.newInstance({background:[237/255,247/255,1]});window.setContainer(host.current);
  const renderer=window.getRenderer(),render=window.getRenderWindow();const mesh=vtkPolyData.newInstance(),mapper=vtkMapper.newInstance(),actor=vtkActor.newInstance(),lut=vtkColorTransferFunction.newInstance();mapper.setInputData(mesh);actor.setMapper(mapper);renderer.addActor(actor);mapper.setLookupTable(lut);
  let visible=true,dirty=false;const paint=()=>{if(!visible||document.hidden){dirty=true;return;}dirty=false;render.render();};const visibility=new IntersectionObserver(entries=>{visible=!!entries[0]?.isIntersecting;if(visible&&dirty)paint();});visibility.observe(host.current);const resume=()=>{if(!document.hidden&&dirty)paint();};document.addEventListener('visibilitychange',resume);
  runtime.current={window,renderer,render:{render:paint},mesh,mapper,actor,lut,load};
  const observer=new ResizeObserver(()=>window.resize());observer.observe(host.current);
  const sub=renderer.getActiveCamera().onModified(()=>{const c=renderer.getActiveCamera();host.current?.setAttribute('data-camera-position',JSON.stringify(c.getPosition()));if(synchronizing.current)return;cameraCallback.current?.({position:[...c.getPosition()],focalPoint:[...c.getFocalPoint()],viewUp:[...c.getViewUp()],parallelScale:c.getParallelScale()});});
  const picker=vtkPointPicker.newInstance(),cellPicker=vtkCellPicker.newInstance();picker.setTolerance(.01);cellPicker.setTolerance(.001);
  const lost=(event:Event)=>{event.preventDefault();setContextLost(true);};const restored=()=>{if(disposed)return;setContextLost(false);setGeneration(g=>g+1);};const element=host.current;element.addEventListener('webglcontextlost',lost,true);element.addEventListener('webglcontextrestored',restored,true);
  const pickSub=render.getInteractor().onLeftButtonPress((event:any)=>{const position=event.position;const selected=manifest.fields?.find((f:any)=>f.field_id===fieldRef.current);const association=selected?.association==='cell'?'cell':'point';const activePicker=association==='cell'?cellPicker:picker;activePicker.pick([position.x,position.y,0],renderer);const id=association==='cell'?cellPicker.getCellId():picker.getPointId();if(id<0)return;const picked={association,display_id:id,position:[...activePicker.getPickPosition()],generated:!!manifest.entity_mapping?.generated_entities,original_id:null as string|null,values:null as string[]|null};const mapping=manifest.entity_mapping?.[association];
   (async()=>{if(mapping){const ids=await decodeBuffer(await load(mapping.path),mapping);picked.original_id=String(ids[id]);}if(selected){const values=await decodeBuffer(await load(selected.buffer.path),selected.buffer);picked.values=Array.from({length:selected.components},(_,i)=>String(values[id*selected.components+i]));}if(!disposed)pickCallback.current?.(picked);})().catch(e=>{if(!disposed)onError?.(e);});
  });
  (async()=>{const p=manifest.geometry_buffers[0];const points=await decodeBuffer(await load(p.path),p);if(disposed)return;mesh.getPoints().setData(points,3);
   for(const b of manifest.topology_buffers){const a=await decodeBuffer(await load(b.path),b);if(disposed)return;const cells=b.name==='polys'?mesh.getPolys():b.name==='lines'?mesh.getLines():mesh.getVerts();cells.setData(a);}
   renderer.resetCamera();if(latestCamera.current){synchronizing.current=true;renderer.getActiveCamera().set(latestCamera.current);synchronizing.current=false;}window.resize();paint();setReady(x=>x+1);
  })().catch(e=>{if(!disposed)onError?.(e);});
  return()=>{disposed=true;element.removeEventListener('webglcontextlost',lost,true);element.removeEventListener('webglcontextrestored',restored,true);visibility.disconnect();document.removeEventListener('visibilitychange',resume);observer.disconnect();sub.unsubscribe();pickSub.unsubscribe();picker.delete();cellPicker.delete();actor.delete();mapper.delete();mesh.delete();lut.delete();window.delete();for(const key of held.keys())releaseBuffer(key);held.clear();runtime.current=null;};
 },[manifest,generation]);
 useEffect(()=>{const r=runtime.current;if(!r)return;const property=r.actor.getProperty();property.setRepresentation(representation==='wireframe'?1:representation==='points'?0:2);property.setOpacity(opacity);property.setPointSize(3);r.render.render();},[representation,opacity,manifest,ready]);
 useEffect(()=>{let gone=false;const r=runtime.current;if(!r)return;if(!field){r.mapper.setScalarVisibility(false);r.render.render();return;}
 (async()=>{const f=manifest.fields.find((x:any)=>x.field_id===field);if(!f)return;const values=await decodeBuffer(await r.load(f.buffer.path),f.buffer);if(gone)return;if(values instanceof BigInt64Array||values instanceof BigUint64Array)throw new Error('64位整数字段请在数值表查看，三维着色不做有损转换');
 const array=vtkDataArray.newInstance({name:f.name,numberOfComponents:f.components,values});(f.association==='cell'?r.mesh.getCellData():r.mesh.getPointData()).setScalars(array);
 r.lut.removeAllPoints();const bounds=range||(component==='magnitude'&&f.components>1?f.magnitude_range:f.component_ranges?.[Number(component)]||f.range)||[0,1];const [lo,hi]=bounds;r.lut.addRGBPoint(lo,.12,.3,.8);r.lut.addRGBPoint((lo+hi)/2,.93,.95,.97);r.lut.addRGBPoint(hi,.82,.12,.12);r.lut.setNanColor(.5,.5,.5,1);
 if(component==='magnitude'&&f.components>1)r.lut.setVectorModeToMagnitude();else {r.lut.setVectorModeToComponent();r.lut.setVectorComponent(component==='magnitude'?0:Number(component));}
 r.mapper.setScalarMode(f.association==='cell'?2:1);r.mapper.setScalarVisibility(true);r.mapper.setScalarRange(lo,hi===lo?lo+1:hi);r.render.render();})().catch(e=>{if(!gone)onError?.(e);});return()=>{gone=true;};
 },[field,component,range,manifest,ready]);
 useEffect(()=>{const r=runtime.current;if(!r||!camera)return;synchronizing.current=true;r.renderer.getActiveCamera().set(camera);r.render.render();synchronizing.current=false;},[camera]);
 useEffect(()=>{const r=runtime.current;if(!r||!command)return;
  if(command.kind==='reset'){r.renderer.resetCamera();r.render.render();}
  if(command.kind==='projection'){const c=r.renderer.getActiveCamera();c.setParallelProjection(!c.getParallelProjection());r.render.render();}
  if(command.kind==='screenshot'){const pending=r.window.getOpenGLRenderWindow().captureNextImage();r.render.render();pending.then((image:string)=>onImage?.(image)).catch((e:Error)=>onError?.(e));}
 },[command]);
 return <div className="viz-canvas" ref={host} aria-label="真实三维视图" data-context-state={contextLost?'lost':'ready'}>{contextLost&&<div className="viz-context-notice" role="status">图形上下文已丢失，等待浏览器恢复…</div>}</div>;
}
