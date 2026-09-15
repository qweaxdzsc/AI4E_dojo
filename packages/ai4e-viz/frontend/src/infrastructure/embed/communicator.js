/** 同源嵌入消息验证；业务载荷由模块 Hook 解释。 */
const actions = ['save','record','animation','export','export_csv','configuration','open','import'];
/** 仅接受已挂载子窗口与已登记动作，卸载时释放监听器。 */
export function listenToFrame(frame, handler) {
  const receive = (event) => {
    if (event.origin !== window.location.origin || event.source !== frame.current?.contentWindow) return;
    const message = event.data;
    if (actions.some(action => message?.type === `ai4e-vis:${action}`) && typeof message.request_id === 'string') handler(message);
  };
  window.addEventListener('message', receive);
  return () => window.removeEventListener('message', receive);
}
/** 回送对应请求状态，避免不同窗口的结果混淆。 */
export function respondToFrame(frame, requestId, result) {
  frame.current?.contentWindow?.postMessage({type:'ai4e-vis:response',request_id:requestId,...result},window.location.origin);
}
