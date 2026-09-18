/** Trame 多视口指针归属：其他 tracker 不得截获正在进行的拖动。 */
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import {expect, test, vi} from 'vitest';

test('only the initiating viewport handles movement and release',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const make=()=>{
  const viewport={contains:()=>false,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
  const tracker={$el:{closest:()=>viewport},$emit:vi.fn(),view:null,eventPoint:()=>({x:.2,y:.3})};
  component.mounted.call(tracker);return tracker;
 };
 const first=make(),second=make();
 window.__physPlaneDrag=true;second._dragActive=true;second._dragObject='child';second._dragId='gesture';
 const event={preventDefault:vi.fn(),stopImmediatePropagation:vi.fn()};
 first.onPlaneMove(event);first.onPlaneUp();
 expect(event.preventDefault).not.toHaveBeenCalled();expect(first.$emit).not.toHaveBeenCalled();expect(window.__physPlaneDrag).toBe(true);
 second.onPlaneMove(event);second.onPlaneUp();
 expect(second.$emit).toHaveBeenCalledWith('plane-move',{x:.2,y:.3,identity:'child',token:'gesture'});
 expect(second.$emit).toHaveBeenCalledWith('plane-release',{identity:'child',token:'gesture'});
 expect(window.__physPlaneDrag).toBe(false);
});

test('plane press does not lock until server confirms',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const viewport={contains:()=>false,addEventListener:()=>{},setPointerCapture:vi.fn(),releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  view:null,
  planeDragging:'',
  planeWidget:{visible:true,object:'slice',view:0,hitGeometry:{}},
  eventPoint:()=>({x:.2,y:.3,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
 };
 component.mounted.call(tracker);
 window.__physPlaneDrag=false;
 tracker.onPlaneDown({button:0,pointerId:1,preventDefault:vi.fn(),stopImmediatePropagation:vi.fn()});
 expect(window.__physPlaneDrag).toBe(false);
  tracker._pendingPress=true;
  tracker.planeDragging='axis_x';
  component.methods.confirmPlaneLock.call(tracker);
  expect(window.__physPlaneDrag).toBe(true);
  expect(tracker._dragActive).toBe(true);
});

test('rotate pan and wheel skip camera sync and plane hover',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const viewport={contains:()=>true,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  $nextTick:(fn)=>fn(),
  view:null,
  planeWidget:{visible:true,object:'slice',view:0,hitGeometry:{}},
  eventPoint:()=>({x:.2,y:.3,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
  syncAxes:vi.fn(),
  syncCameras:vi.fn(),
 };
 Object.assign(tracker,component.methods);
 tracker.syncAxes=vi.fn();
 tracker.syncCameras=vi.fn();
 component.mounted.call(tracker);
 tracker.markWheel();
 expect(window.__physWheelZoom).toBe(true);
 expect(window.__physCameraOrbit).toBe(true);
 tracker.onPlaneMove({preventDefault:vi.fn(),stopImmediatePropagation:vi.fn(),target:viewport});
 expect(tracker.$emit).toHaveBeenCalledWith('wheel-zoom',true);
 expect(tracker.$emit).toHaveBeenCalledWith('camera-navigate',true);
 expect(tracker.$emit).not.toHaveBeenCalledWith('plane-hover',expect.anything());
 component.watch.cameras.call(tracker);
 expect(tracker.syncCameras).not.toHaveBeenCalled();
 tracker.$emit.mockClear();
 window.__physWheelZoom=false;
 window.__physCameraOrbit=false;
 tracker._orbitActive=false;
 tracker._wheelActive=false;
 tracker.onOrbitStart({button:2,preventDefault:vi.fn()});
 expect(window.__physCameraOrbit).toBe(true);
 tracker.onPlaneMove({preventDefault:vi.fn(),stopImmediatePropagation:vi.fn(),target:viewport});
 expect(tracker.$emit).not.toHaveBeenCalledWith('plane-hover',expect.anything());
 component.watch.cameras.call(tracker);
 expect(tracker.syncCameras).not.toHaveBeenCalled();
});

test('axes follow local camera during orbit not only pointerup',()=>{
 const listeners={};
 const frames=[];
 const raf=(fn)=>{frames.push(fn);return frames.length;};
 const window={
  addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),
  removeEventListener:()=>{},
  requestAnimationFrame:raf,
  cancelAnimationFrame:()=>{},
 };
 const sandbox={
  window,
  document:{addEventListener:()=>{}},
  setTimeout,
  clearTimeout,
  requestAnimationFrame:raf,
  cancelAnimationFrame:()=>{},
  ResizeObserver:class{observe(){} disconnect(){}},
 };
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const markerCamera={set:vi.fn()};
 const mainCamera={
  position:[4,5,6],
  focal:[1,1,1],
  viewUp:[0,0,1],
  getPosition(){return this.position;},
  getFocalPoint(){return this.focal;},
  getViewUp(){return this.viewUp;},
 };
 const viewport={contains:()=>true,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  view:{
   renderWindow:{
    render:vi.fn(),
    getRenderers:()=>[
     {getLayer:()=>0,getViewport:()=>[0,0,1,1],getActiveCamera:()=>mainCamera},
     {getLayer:()=>2,getViewport:()=>[0.02,0.03,0.18,0.22],getActiveCamera:()=>markerCamera},
    ],
   },
   interactor:{
    onStartAnimation:()=>({unsubscribe:()=>{}}),
    onAnimation:(fn)=>({unsubscribe:()=>{},fn}),
    onEndAnimation:()=>({unsubscribe:()=>{}}),
   },
  },
  planeWidget:{visible:false,hitGeometry:{}},
  eventPoint:()=>({x:.2,y:.3,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
  cameraNavigating:false,
  wheelZooming:false,
 };
 Object.assign(tracker,component.methods);
 component.mounted.call(tracker);
 tracker.onOrbitStart({button:2,preventDefault:vi.fn()});
 expect(markerCamera.set).toHaveBeenCalled();
 markerCamera.set.mockClear();
 mainCamera.position=[10,11,12];
 tracker.onPlaneMove({preventDefault:vi.fn(),stopImmediatePropagation:vi.fn(),target:viewport});
 expect(markerCamera.set).toHaveBeenCalledWith(expect.objectContaining({
  position:[9,10,11],
  focalPoint:[0,0,0],
  viewUp:[0,0,1],
 }));
 frames[0]?.();
 expect(tracker.view.renderWindow.render).toHaveBeenCalled();
});

test('geometry scene reload does not reapply stale cameras',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const viewport={contains:()=>true,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  $nextTick:(fn)=>fn(),
  view:null,
  planeWidget:{visible:true,hitGeometry:{}},
  eventPoint:()=>({x:.2,y:.3,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
  syncCameras:vi.fn(),
  cameraNavigating:false,
  wheelZooming:false,
 };
 Object.assign(tracker,component.methods);
 tracker.syncCameras=vi.fn();
 component.mounted.call(tracker);
 tracker.ready();
 expect(tracker.syncCameras).toHaveBeenCalledTimes(1);
 tracker.syncCameras.mockClear();
 tracker.ready();
 expect(tracker.syncCameras).not.toHaveBeenCalled();
 component.watch.cameras.call(tracker);
 expect(tracker.syncCameras).toHaveBeenCalledTimes(1);
});

test('pointer down activates the viewport under the pointer',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const viewport={contains:()=>true,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  view:{
   renderWindow:{
    getRenderers:()=>[
     {getLayer:()=>0,getViewport:()=>[0,0,0.5,1]},
     {getLayer:()=>0,getViewport:()=>[0.5,0,1,1]},
    ],
   },
   interactor:{
    onStartAnimation:()=>({unsubscribe:()=>{}}),
    onAnimation:()=>({unsubscribe:()=>{}}),
    onEndAnimation:()=>({unsubscribe:()=>{}}),
   },
  },
  viewIds:[0,1],
  cameras:[],
  planeWidget:{visible:false,hitGeometry:{}},
  eventPoint:()=>({x:0.7,y:0.4,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
 };
 Object.assign(tracker,component.methods);
 tracker.eventPoint=()=>({x:0.7,y:0.4,width:10,height:10});
 component.mounted.call(tracker);
 tracker.onOrbitStart({button:2,preventDefault:vi.fn()});
 expect(tracker.$emit).toHaveBeenCalledWith('view-activate',1);
});

test('handoff does not emit remote camera gestures',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const viewport={contains:()=>true,addEventListener:()=>{},releasePointerCapture:vi.fn(),style:{}};
 const tracker={
  $el:{closest:()=>viewport},
  $emit:vi.fn(),
  view:null,
  planeWidget:{visible:false,hitGeometry:{}},
  eventPoint:()=>({x:.2,y:.3,width:10,height:10}),
  worldRay:()=>[[0,0,0],[1,0,0]],
  remoteHandoff:true,
  useRemoteView:true,
  remoteReady:false,
 };
 Object.assign(tracker,component.methods);
 component.mounted.call(tracker);
 tracker.onOrbitStart({button:2,preventDefault:vi.fn()});
 tracker.onWheel();
 expect(tracker.$emit).not.toHaveBeenCalledWith('camera-navigate',true);
 expect(tracker.$emit).not.toHaveBeenCalledWith('wheel-zoom',true);
 expect(window.__physCameraOrbit).not.toBe(true);
 expect(window.__physWheelZoom).not.toBe(true);
});

test('syncAxes copies main camera orientation onto decoration layer',()=>{
 const listeners={};
 const window={addEventListener:(name,fn)=>(listeners[name]??=[]).push(fn),removeEventListener:()=>{}};
 const sandbox={window,document:{addEventListener:()=>{}},setTimeout,clearTimeout,ResizeObserver:class{observe(){} disconnect(){}}};
 vm.createContext(sandbox);
 vm.runInContext(readFileSync('../backend/modules/visPhysField/trameUI/client/interaction.js','utf8'),sandbox);
 let component;window.PhysInteraction.install({component:(_name,value)=>{component=value;}});
 const markerCamera={set:vi.fn()};
 const tracker={
  view:{
   renderWindow:{
    getRenderers:()=>[
     {getLayer:()=>0,getViewport:()=>[0,0,1,1],getActiveCamera:()=>({
      getPosition:()=>[4,5,6],
      getFocalPoint:()=>[1,1,1],
      getViewUp:()=>[0,0,1],
     })},
     {getLayer:()=>2,getViewport:()=>[0.02,0.03,0.18,0.22],getActiveCamera:()=>markerCamera},
    ],
   },
  },
 };
 component.methods.syncAxes.call(tracker);
 expect(markerCamera.set).toHaveBeenCalledWith({
  position:[3,4,5],
  focalPoint:[0,0,0],
  viewUp:[0,0,1],
  parallelProjection:true,
  parallelScale:1.4,
 });
});
