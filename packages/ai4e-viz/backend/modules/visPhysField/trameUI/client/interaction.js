/** 多视图相机桥接；使用 VTK 视图提供的上下文，逐视图回传实际相机。 */
function physSub(a, b) {
  return [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
}
function physDot(a, b) {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}
function physLen(a) {
  return Math.hypot(a[0], a[1], a[2]);
}
function physNorm(a) {
  const n = physLen(a);
  return n ? a.map((x) => x / n) : a;
}
function physClosestOnAxis(ray, origin, axis) {
  const dir = physNorm(physSub(ray[1], ray[0]));
  axis = physNorm(axis);
  const start = physSub(ray[0], origin);
  const denom = 1 - physDot(dir, axis) ** 2;
  if (Math.abs(denom) < 1e-10) return physDot(start, axis);
  return (physDot(start, axis) - physDot(start, dir) * physDot(dir, axis)) / denom;
}
function physRayPlane(ray, origin, normal) {
  const dir = physSub(ray[1], ray[0]);
  const denom = physDot(normal, dir);
  if (Math.abs(denom) < 1e-12) return null;
  const t = physDot(normal, physSub(origin, ray[0])) / denom;
  return [ray[0][0] + t * dir[0], ray[0][1] + t * dir[1], ray[0][2] + t * dir[2]];
}
function physHitHandle(widget, ray) {
  if (!widget || !widget.visible) return null;
  const origin = widget.origin;
  const normal = physNorm(widget.normal);
  const bounds = widget.bounds;
  const size = Math.max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4], 1e-6) * 0.55;
  const threshold = size * 0.08;
  let best = null;
  let bestD = Infinity;
  const axes = {axis_x: [1, 0, 0], axis_y: [0, 1, 0], axis_z: [0, 0, 1]};
  for (const [name, axis] of Object.entries(axes)) {
    const s = physClosestOnAxis(ray, origin, axis);
    if (s < -threshold || s > size * 0.45 + threshold) continue;
    const point = [origin[0] + axis[0] * s, origin[1] + axis[1] * s, origin[2] + axis[2] * s];
    const dir = physNorm(physSub(ray[1], ray[0]));
    const t = physDot(physSub(point, ray[0]), dir);
    const closest = [ray[0][0] + dir[0] * t, ray[0][1] + dir[1] * t, ray[0][2] + dir[2] * t];
    const d = physLen(physSub(point, closest));
    if (d < threshold && d < bestD) {
      best = name;
      bestD = d;
    }
  }
  const hit = physRayPlane(ray, origin, normal);
  if (hit) {
    const radial = physLen(physSub(hit, origin));
    const ring = Math.abs(radial - size * 0.32);
    if (ring < threshold && ring < bestD) {
      best = "rotate";
      bestD = ring;
    } else if (radial <= size * 0.5 && bestD === Infinity) {
      best = "plane";
    }
  }
  return best;
}

window.PhysInteraction = {
 install(Vue) {
  document.addEventListener('mousemove', (event) => {
   const viewport = document.getElementById('phys-viewport');
   if (!viewport || !viewport.contains(event.target)) return;
   const box = viewport.getBoundingClientRect();
   if (!box.width || !box.height) return;
   window.__visPointer = [(event.clientX - box.left) / box.width, 1 - (event.clientY - box.top) / box.height];
  }, true);
  Vue.component('phys-camera-tracker', {
   inject: ['view'],
   props: {viewIds: {type:Array,default:()=>[]},cameras:{type:Array,default:()=>[]},planeWidget:{type:Object,default:()=>({visible:false})}},
   methods:{
    eventPoint(event){
     const box=event.currentTarget.getBoundingClientRect();
     return {
      x:(event.clientX-box.left)/box.width,
      y:1-(event.clientY-box.top)/box.height,
      width:box.width,
      height:box.height,
     };
    },
    worldRay(x, y){
     const renderers=this.view.renderWindow.getRenderers().filter(r=>r.getLayer()===0);
     const renderer=renderers.find(r=>{const [x0,y0,x1,y1]=r.getViewport();return x0<=x&&x<=x1&&y0<=y&&y<=y1;})||renderers[0];
     if(!renderer)return null;
     const view=this.view.renderWindow.getViews()[0];
     const size=view.getSize();
     const display=[x*size[0], y*size[1]];
     return [view.displayToWorld(display[0], display[1], 0, renderer), view.displayToWorld(display[0], display[1], 1, renderer)];
    },
    syncCameras(){
     // 服务端回写相机后再 render 会触发 EndAnimation；同步期间不能再上报，否则会整屏刷新。
     this._syncing = true;
     // Trame 的相机序列化只初始化一次；后续服务端方向命令必须显式同步。
     for(const entry of this.cameras){
      const renderer=this.view.renderWindow.getRenderers().find(r=>r.getLayer()===entry.layer&&r.getViewport().every((v,i)=>Math.abs(v-entry.viewport[i])<1e-8));
      if(!renderer)continue;
      const c=entry.camera;
     renderer.getActiveCamera().set({position:c.position,focalPoint:c.focal_point,viewUp:c.view_up,parallelScale:c.parallel_scale,parallelProjection:c.parallel_projection,clippingRange:entry.clipping_range});
     // 使用 vtk.js 原生色标布局回调，固定在左上；仍消费同一真实 LookupTable。
     const legends=renderer.getViewProps().filter(a=>a.isA?.('vtkScalarBarActor') && a.getVisibility());
     for(const [index,actor] of legends.entries()){
      actor.setAutoLayout(helper=>{
       const [width,height]=helper.getLastSize();
       Object.assign(helper.getAxisTextStyle(),{fontColor:'white',fontFamily:'Arial',fontStyle:'normal',fontSize:13});
       Object.assign(helper.getTickTextStyle(),{fontColor:'white',fontFamily:'Arial',fontStyle:'normal',fontSize:12});
       helper.setTopTitle(true);helper.setAxisTitlePixelOffset(10);helper.setTickLabelPixelOffset(7);
       const sizes=helper.updateTextureAtlas();
       const slot=Math.min(height*.65,(height-90)/legends.length), gap=35;
       helper.setBoxPosition([-1+32/width,1-2*(45+(index+1)*slot-gap)/height]);
       helper.setBoxSize([2*(sizes.tickWidth+30)/width,2*(slot-gap)/height]);
       helper.recomputeBarSegments(sizes);
      });
     }
     }
     this.view.renderWindow.render();
     requestAnimationFrame(()=>{this._syncing=false;});
    }
   },
   watch:{cameras(){this.$nextTick(this.syncCameras);}},
   mounted() {
    this.$el.__physTracker=this;
    this._syncing=false;
    this._lastSize='';
    this.ready=()=>this.syncCameras();window.addEventListener('phys-scene-ready',this.ready);
    const viewport=this.$el.closest('.phys-viewport');
    this.resizeObserver=new ResizeObserver(entries=>{
     const {width,height}=entries[0].contentRect;
     const next={width:Math.round(width),height:Math.round(height)};
     const key=next.width+'x'+next.height;
     if(!next.width||!next.height||key===this._lastSize)return;
     this._lastSize=key;
     clearTimeout(this._resizeTimer);
     this._resizeTimer=setTimeout(()=>this.$emit('view-resize',next),120);
    });
    this.resizeObserver.observe(viewport);
    this.onPlaneDown=(event)=>{
     if(event.button!==0)return;
     const point=this.eventPoint(event);
     const ray=this.worldRay(point.x, point.y);
     if(!physHitHandle(this.planeWidget, ray))return;
     event.stopImmediatePropagation();
     window.__physPlaneDrag=true;
     this.$emit('plane-press', point);
    };
    this.onPlaneMove=(event)=>{
     if(!window.__physPlaneDrag)return;
     this.$emit('plane-move', this.eventPoint(event));
    };
    this.onPlaneUp=()=>{
     if(!window.__physPlaneDrag)return;
     window.__physPlaneDrag=false;
     this.$emit('plane-release');
    };
    window.__physPlaneMove=(event)=>this.onPlaneMove(event);
    window.__physPlaneRelease=()=>this.onPlaneUp();
    viewport.addEventListener('mousedown', this.onPlaneDown, true);
    this.subscription=this.view.interactor.onEndAnimation(()=>{
     if(this._syncing||window.__physPlaneDrag)return;
     const pointer=window.__visPointer||[.5,.5];
     const renderers=this.view.renderWindow.getRenderers().filter(r=>r.getLayer()===0);
     const index=renderers.findIndex(r=>{const [x0,y0,x1,y1]=r.getViewport();return x0<=pointer[0]&&pointer[0]<=x1&&y0<=pointer[1]&&pointer[1]<=y1;});
     if(index<0)return;
     const c=renderers[index].getActiveCamera();
     this.$emit('camera-change',{view:this.viewIds[index],camera:{position:Array.from(c.getPosition()),focal_point:Array.from(c.getFocalPoint()),view_up:Array.from(c.getViewUp()),parallel_scale:c.getParallelScale(),parallel_projection:c.getParallelProjection()}});
    });
   },
   beforeDestroy() {
    this.subscription?.unsubscribe();
    this.resizeObserver?.disconnect();
    clearTimeout(this._resizeTimer);
    window.removeEventListener('phys-scene-ready',this.ready);
    this.$el.closest('.phys-viewport')?.removeEventListener('mousedown', this.onPlaneDown, true);
   },
   render(h) {return h('span',{style:{display:'none'}});}
  });
 }
};
