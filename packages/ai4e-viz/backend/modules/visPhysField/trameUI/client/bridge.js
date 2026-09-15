/** Trame 只发业务事件，保存位置与输出表单由 Vis React 持有。 */
window.ai4eVisBridge = {
  request(action, payload) {
    window.parent.postMessage({ type: 'ai4e-vis:' + action, request_id: crypto.randomUUID(), payload }, window.location.origin);
  }
};

/** 隐藏后再显示才通知视口测量；已可见时重复消息不派发 resize，避免工作进程连读网格。 */
window.addEventListener('message',event=>{
  if(event.origin!==window.location.origin||event.source!==window.parent||event.data?.type!=='ai4e-vis:visibility'||typeof event.data.request_id!=='string')return;
  const visible=event.data.visible===true;
  if(visible&&!window.__ai4eVisShown){
    window.__ai4eVisShown=true;
    requestAnimationFrame(()=>window.dispatchEvent(new Event('resize')));
  }
  if(!visible)window.__ai4eVisShown=false;
});
