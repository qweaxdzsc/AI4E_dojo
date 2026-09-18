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
  if (!widget?.visible || !ray) return null;
  // 浏览器和服务端都消费同一份三角面，避免宽泛圆盘与细线两套命中。
  const direction=physSub(ray[1],ray[0]);
  const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
  let best=null,nearest=Infinity;
  for(const [name,triangles] of Object.entries(widget.hitGeometry||{})) {
    for(let i=0;i<triangles.length;i+=9){
      const a=triangles.slice(i,i+3),b=triangles.slice(i+3,i+6),c=triangles.slice(i+6,i+9);
      const e1=physSub(b,a),e2=physSub(c,a),h=cross(direction,e2),det=physDot(e1,h);
      if(Math.abs(det)<1e-12)continue;
      const q=physSub(ray[0],a),u=physDot(q,h)/det;if(u<0||u>1)continue;
      const r=cross(q,e1),v=physDot(direction,r)/det;if(v<0||u+v>1)continue;
      const t=physDot(e2,r)/det;
      if(t>=0&&t<=1&&t<nearest){nearest=t;best=name;}
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
   inject: {view:{default:null}},
   props: {viewIds: {type:Array,default:()=>[]},cameras:{type:Array,default:()=>[]},planeWidget:{type:Object,default:()=>({visible:false})},planeDragging:{type:String,default:''},wheelZooming:{type:Boolean,default:false},cameraNavigating:{type:Boolean,default:false},remoteHandoff:{type:Boolean,default:false},useRemoteView:{type:Boolean,default:false},remoteReady:{type:Boolean,default:true}},
   methods:{
    eventPoint(event){
     const box=this.$el.closest('.phys-viewport')?.getBoundingClientRect?.();
     if(!box?.width||!box.height){
      return {x:0,y:0,width:0,height:0};
     }
     return {
      x:(event.clientX-box.left)/box.width,
      y:1-(event.clientY-box.top)/box.height,
      width:box.width,
      height:box.height,
     };
    },
    worldRay(x, y){
     if(!this.view){
      const entry=this.cameras.find(e=>e.layer===0&&e.viewport[0]<=x&&x<=e.viewport[2]&&e.viewport[1]<=y&&y<=e.viewport[3]);
      if(!entry)return null;
      const c=entry.camera,[x0,y0,x1,y1]=entry.viewport;
      const box=this.$el.closest('.phys-viewport').getBoundingClientRect();
      const forward=physNorm(physSub(c.focal_point,c.position));
      const cross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
      const right=physNorm(cross(forward,c.view_up)),up=cross(right,forward);
      const nx=2*(x-x0)/(x1-x0)-1,ny=2*(y-y0)/(y1-y0)-1;
      const aspect=box.width*(x1-x0)/(box.height*(y1-y0));
      return entry.clipping_range.map(depth=>{
       const scale=c.parallel_projection?c.parallel_scale:depth*Math.tan((entry.view_angle||30)*Math.PI/360);
       return c.position.map((v,i)=>v+forward[i]*depth+right[i]*nx*scale*aspect+up[i]*ny*scale);
      });
     }
     const renderers=this.view.renderWindow.getRenderers().filter(r=>r.getLayer()===0);
     const renderer=renderers.find(r=>{const [x0,y0,x1,y1]=r.getViewport();return x0<=x&&x<=x1&&y0<=y&&y<=y1;})||renderers[0];
     if(!renderer)return null;
     const view=this.view.renderWindow.getViews()[0];
     const size=view.getSize();
     const display=[x*size[0], y*size[1]];
     return [view.displayToWorld(display[0], display[1], 0, renderer), view.displayToWorld(display[0], display[1], 1, renderer)];
    },
    orbiting(){
     return !!(this._orbitActive||this._wheelActive||window.__physCameraOrbit||window.__physWheelZoom||this.cameraNavigating||this.wheelZooming);
    },
    syncCameras(){
     if(!this.view||this.orbiting())return;
     // 服务端回写相机后再 render 会触发 EndAnimation；同步期间不能再上报，否则会整屏刷新。
     this._syncing = true;
     // Trame 的相机序列化只初始化一次；后续服务端方向命令必须显式同步。
     for(const entry of this.cameras){
      const renderer=this.view.renderWindow.getRenderers().find(r=>r.getLayer()===entry.layer&&r.getViewport().every((v,i)=>Math.abs(v-entry.viewport[i])<1e-8));
      if(!renderer)continue;
      const c=entry.camera;
     renderer.getActiveCamera().set({position:c.position,focalPoint:c.focal_point,viewUp:c.view_up,parallelScale:c.parallel_scale,parallelProjection:c.parallel_projection,clippingRange:entry.clipping_range});
     // 本地与服务端消费相同色标声明，避免本地重置用户位置和字号。
     const legends=renderer.getViewProps().filter(a=>a.isA?.('vtkScalarBarActor') && a.getVisibility());
     for(const [index,actor] of legends.entries()){
      const style=entry.legend_styles?.[index]||{};
      if(style.orientation==='horizontal')actor.setOrientationToHorizontal?.();else actor.setOrientationToVertical?.();
      actor.setAutoLayout(helper=>{
       const [width,height]=helper.getLastSize();
       Object.assign(helper.getAxisTextStyle(),{fontColor:'white',fontFamily:'Arial',fontStyle:'normal',fontSize:style.title_font_size||25});
       Object.assign(helper.getTickTextStyle(),{fontColor:'white',fontFamily:'Arial',fontStyle:'normal',fontSize:style.label_font_size||25});
       helper.setTopTitle(true);helper.setAxisTitlePixelOffset(10);helper.setTickLabelPixelOffset(7);
       const sizes=helper.updateTextureAtlas();
       const horizontal=style.orientation==='horizontal',position=style.position||'right';
       const length=position==='custom'?(style.length||.6):Math.min(style.length||.6,.8/legends.length-.03);
       const thick=style.thickness||25;
       const titleOffset=horizontal?sizes.tickHeight+17:10;
       helper.setAxisTitlePixelOffset(titleOffset);
       const w=horizontal?length:(sizes.tickWidth+thick+7)/width,h=horizontal?(sizes.titleHeight+titleOffset+thick)/height:length;
       const shift=index*.8/legends.length;
       const positions={right:[1-w-.025,.92-h-shift],left:[.025,.92-h-shift],top:[.12+shift,1-h-.07],bottom:[.12+shift,.04]};
       const [x,y]=positions[position]||[style.x??.8,style.y??.2];
       helper.setBoxPosition([2*Math.min(x,1-w-.01)-1,2*Math.min(y,1-h-.01)-1]);
       helper.setBoxSize([2*w,2*h]);
       helper.recomputeBarSegments(sizes);
      });
     }
     }
     this.syncAxes();
     this.view.renderWindow.render();
     requestAnimationFrame(()=>{this._syncing=false;});
    },
    syncAxes(){
     if(!this.view)return;
     const mains=this.view.renderWindow.getRenderers().filter(r=>r.getLayer()===0);
     const decorations=this.view.renderWindow.getRenderers().filter(r=>r.getLayer()===2);
     for(const marker of decorations){
      const viewport=marker.getViewport();
      const main=mains.find(r=>{
       const box=r.getViewport();
       return viewport[0]>=box[0]-1e-6&&viewport[1]>=box[1]-1e-6&&viewport[2]<=box[2]+1e-6&&viewport[3]<=box[3]+1e-6;
      })||mains[0];
      if(!main)continue;
      const camera=main.getActiveCamera();
      const position=camera.getPosition(),focal=camera.getFocalPoint();
      marker.getActiveCamera().set({
       position:[position[0]-focal[0],position[1]-focal[1],position[2]-focal[2]],
       focalPoint:[0,0,0],
       viewUp:camera.getViewUp(),
       parallelProjection:true,
       parallelScale:1.4,
      });
     }
    },
    followAxes(){
     // 轴跟本地当前相机，不读 render_cameras，避免轨道中被旧位姿盖住。
     this.syncAxes();
    },
    startAxesFollow(){
     if(this._axesRaf||typeof requestAnimationFrame!=='function')return;
     const tick=()=>{
      this.followAxes();
      if(this.view&&!this._syncing)this.view.renderWindow?.render?.();
      if(this._orbitActive||this._wheelActive||window.__physCameraOrbit||window.__physWheelZoom){
       this._axesRaf=requestAnimationFrame(tick);
      }else{
       this._axesRaf=0;
       this.followAxes();
      }
     };
     this._axesRaf=requestAnimationFrame(tick);
    },
    blockedRemote(){
     return !!(this.remoteHandoff || (this.useRemoteView && this.remoteReady!==true));
    },
    confirmPlaneLock(){
     if(this.planeDragging && this._pendingPress){
      this._dragActive=true;
      window.__physPlaneDrag=true;
     }
    },
    applyPushedCameras(){
     // 只在 render_cameras 真正推过新位姿时回写。几何/悬停的
     // after_scene_loaded 不得用添加平面时的旧位姿盖住本地轨道。
     if(this.orbiting())return;
     if(this._appliedCamerasEpoch===this._camerasEpoch)return;
     this.syncCameras();
     this._appliedCamerasEpoch=this._camerasEpoch;
    }
   },
   watch:{
    cameras(){
     this._camerasEpoch=(this._camerasEpoch||0)+1;
     this.$nextTick(()=>this.applyPushedCameras());
    },
    planeDragging(){this.confirmPlaneLock();},
   },
   mounted() {
    this.$el.__physTracker=this;
    this._syncing=false;
    this._pendingPress=false;
    this._orbitActive=false;
    this._axesRaf=0;
    this._lastSize='';
    this._camerasEpoch=0;
    this._appliedCamerasEpoch=-1;
    this.orbiting=()=>!!(this._orbitActive||this._wheelActive||window.__physCameraOrbit||window.__physWheelZoom||this.cameraNavigating||this.wheelZooming);
    this.ready=()=>this.applyPushedCameras();window.addEventListener('phys-scene-ready',this.ready);
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
    this.viewIdAtPoint=(x, y)=>{
     // 按下时按指针所在视口切活跃窗，避免 VTK 吃掉点击后树眼睛不更新。
     const ids=this.viewIds||[];
     if(this.view?.renderWindow){
      const renderers=this.view.renderWindow.getRenderers().filter((item)=>item.getLayer()===0);
      const index=renderers.findIndex((item)=>{
       const [x0,y0,x1,y1]=item.getViewport();
       return x0<=x&&x<=x1&&y0<=y&&y<=y1;
      });
      if(index>=0&&ids[index]!=null)return ids[index];
     }
     const layered=(this.cameras||[]).filter((item)=>item.layer===0);
     const hit=layered.find((item)=>{
      const [x0,y0,x1,y1]=item.viewport||[];
      return x0<=x&&x<=x1&&y0<=y&&y<=y1;
     });
     return hit?ids[layered.indexOf(hit)]:null;
    };
    this.activateViewAt=(event)=>{
     const point=this.eventPoint?.(event);
     if(!point)return;
     const identity=this.viewIdAtPoint(point.x,point.y);
     if(identity!=null)this.$emit('view-activate',identity);
    };
    this.onPlaneDown=(event)=>{
     if(event.button!==0)return;
     this.activateViewAt(event);
     const point=this.eventPoint(event);
     const ray=this.worldRay(point.x, point.y);
     const handle=physHitHandle(this.planeWidget, ray);
     if(!handle)return;
     this._pendingPress=true;
     this._dragId=String(Date.now())+'-'+Math.random();
     this._dragObject=this.planeWidget.object;
     this._dragView=this.planeWidget.view;
     this._pointerId=event.pointerId;
     this.$emit('plane-press', {...point,handle,identity:this._dragObject,token:this._dragId,view:this._dragView});
     if(this.planeDragging){
      event.preventDefault();event.stopImmediatePropagation();
      viewport.setPointerCapture?.(event.pointerId);
      this.confirmPlaneLock();
     }
    };
    this.onPlaneMove=(event)=>{
     if(!window.__physPlaneDrag){
      if(this.orbiting()){
       this.syncAxes();
       return;
      }
      if(!viewport.contains(event.target))return;
      const p=this.eventPoint(event);const handle=physHitHandle(this.planeWidget,this.worldRay(p.x,p.y));
      viewport.style.cursor=handle?'grab':'';
      if(handle!==this._hover){this._hover=handle;this.$emit('plane-hover',{handle,identity:this.planeWidget.object});}
      return;
     }
     if(!this._dragActive)return;
     event.preventDefault();event.stopImmediatePropagation();
     this._pendingPlane = {...this.eventPoint(event),identity:this._dragObject,token:this._dragId};
     // 最多每 40ms 发最新位置；普通移动不产生 RPC，松开时提交最终位置。
     if (!this._planeTimer) this._planeTimer=setTimeout(()=>{
      this._planeTimer=null;
      if(this._pendingPlane)this.$emit('plane-move',this._pendingPlane);
      this._pendingPlane=null;
     },40);
    };
    this.onPlaneUp=()=>{
     if(!this._dragActive && !this._pendingPress)return;
     this._dragActive=false;
     this._pendingPress=false;
     clearTimeout(this._planeTimer);this._planeTimer=null;
     if(this._pendingPlane)this.$emit('plane-move',this._pendingPlane);
     this._pendingPlane=null;window.__physPlaneDrag=false;
     this.$emit('plane-release',{identity:this._dragObject,token:this._dragId});
     viewport.releasePointerCapture?.(this._pointerId);
     this._suppressClick=true;setTimeout(()=>{this._suppressClick=false;},0);
    };
    this.onClick=(event)=>{if(this._suppressClick||window.__physPlaneDrag){event.preventDefault();event.stopImmediatePropagation();}};
    window.addEventListener('pointermove', this.onPlaneMove,true);
    window.addEventListener('pointerup', this.onPlaneUp,true);
    window.addEventListener('pointercancel', this.onPlaneUp,true);
    window.addEventListener('blur', this.onPlaneUp);
    viewport.addEventListener('pointerdown', this.onPlaneDown, true);
    viewport.addEventListener('click',this.onClick,true);
    this.markOrbit=()=>{
     // 远程静帧未就绪时不向远程送手势，避免未登记视图吃到交互。
     if(this.remoteHandoff || (this.useRemoteView && this.remoteReady===false))return;
     // 旋转/平移/缩放共用占用：期间既不发 plane-hover，也不把服务端旧相机写回。
     this._orbitActive=true;
     this._wheelActive=true;
     window.__physCameraOrbit=true;
     window.__physWheelZoom=true;
     this.syncAxes();
     this.startAxesFollow?.();
     this.$emit('camera-navigate',true);
     this.$emit('wheel-zoom',true);
     clearTimeout(this._orbitTimer);
     this._orbitTimer=setTimeout(()=>{
      this._orbitActive=false;
      this._wheelActive=false;
      window.__physCameraOrbit=false;
      window.__physWheelZoom=false;
      this.$emit('camera-navigate',false);
      this.$emit('wheel-zoom',false);
     },280);
    };
    this.markWheel=()=>{this.markOrbit();};
    this.onOrbitStart=(event)=>{
     if(window.__physPlaneDrag||this._pendingPress)return;
     if(event&&event.button===0){
      const point=this.eventPoint(event);
      if(physHitHandle(this.planeWidget,this.worldRay(point.x,point.y)))return;
     }
     if(event)this.activateViewAt(event);
     this.markOrbit();
    };
    this.onWheel=()=>{this.markOrbit();};
    viewport.addEventListener('pointerdown',this.onOrbitStart,true);
    viewport.addEventListener('wheel',this.onWheel,{passive:true});
    this.startSub=this.view?.interactor.onStartAnimation(()=>{
     if(this._syncing||window.__physPlaneDrag||this._pendingPress)return;
     this.markOrbit();
    });
    this.animSub=this.view?.interactor?.onAnimation?.(()=>{
     if(this._syncing)return;
     this.syncAxes();
    });
    this.subscription=this.view?.interactor.onEndAnimation(()=>{
     if(this._syncing||this.remoteHandoff||(this.useRemoteView&&this.remoteReady===false))return;
     this.syncAxes();
     if(window.__physPlaneDrag)return;
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
    this.startSub?.unsubscribe();
    this.animSub?.unsubscribe();
    if(this._axesRaf&&typeof cancelAnimationFrame==='function')cancelAnimationFrame(this._axesRaf);
    this._axesRaf=0;
    this.resizeObserver?.disconnect();
    clearTimeout(this._resizeTimer);
    clearTimeout(this._planeTimer);
    clearTimeout(this._orbitTimer);
    clearTimeout(this._wheelTimer);
    window.__physWheelZoom=false;
    window.__physCameraOrbit=false;
    if(this._dragActive)this.onPlaneUp();
    window.removeEventListener('pointermove',this.onPlaneMove,true);
    window.removeEventListener('pointerup',this.onPlaneUp,true);
    window.removeEventListener('pointercancel',this.onPlaneUp,true);
    window.removeEventListener('blur',this.onPlaneUp);
    window.removeEventListener('phys-scene-ready',this.ready);
    this.$el.closest('.phys-viewport')?.removeEventListener('pointerdown', this.onPlaneDown, true);
    this.$el.closest('.phys-viewport')?.removeEventListener('pointerdown', this.onOrbitStart, true);
    this.$el.closest('.phys-viewport')?.removeEventListener('click',this.onClick,true);
    this.$el.closest('.phys-viewport')?.removeEventListener('wheel',this.onWheel);
   },
   render(h) {return h('span',{style:{display:'none'}});}
  });
 }
};
