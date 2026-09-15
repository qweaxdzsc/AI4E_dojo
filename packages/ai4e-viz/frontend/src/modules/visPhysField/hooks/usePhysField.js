/** 工作区会话生命周期、保存修订和导出状态；所有页面复用本 Hook。 */
import { useEffect, useRef, useState } from 'react';
import { physApi } from '../api.js';

/** JSON 对象键序不同不表示配置变更。 */
function canonical(value) { if(Array.isArray(value)) return value.map(canonical); if(value && typeof value==='object') return Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])); return value; }


/** 管理固定上下文下的独立物理会话。 */
export function usePhysField(params = new URLSearchParams()) {
  params = params instanceof URLSearchParams ? params : new URLSearchParams(window.location.hash.split('?')[1] || '');
  const context = params.get('context') || '';
  const closing = useRef(new Map()), initial = useRef(null);
  const [session, setSession] = useState(null);
  const [asset, setAsset] = useState(null), [assets, setAssets] = useState([]), [error, setError] = useState(''), [busy, setBusy] = useState(false), [output, setOutput] = useState(null), [target, setTarget] = useState(null);
  const fail = (e) => setError(e.message || String(e));
  const refresh = async () => setAssets((await physApi.list(context)).items.filter((item) => item.kind === 'phys_field'));
  useEffect(() => {
    if (!context) return;
    physApi.context(context).then((value) => setTarget(value.target)).catch(fail);
    refresh().catch(fail);
    if (params.get('asset')) physApi.read(context, params.get('asset')).then(setAsset).catch(fail);
  }, [context]);
  useEffect(() => {
    const id = params.get('session');
    if (!context || !id) return;
    let mounted = true;
    // StrictMode 两次挂载复用同一次接管，过期会话从已保存配置重建。
    if (!initial.current) initial.current = (async () => {
      try {
        await physApi.heartbeat(context, id);
        return {session_id: id, secret: params.get('secret')};
      } catch (e) {
        const saved = params.get('asset') ? await physApi.read(context, params.get('asset')) : null;
        return physApi.create(context, saved?.spec);
      }
    })();
    initial.current.then((value) => {
      if (mounted) setSession(value);
    }).catch((e) => { if (mounted) fail(e); });
    return () => { mounted = false; };
  }, [context]);
  useEffect(() => {
    if (!session) return;
    clearTimeout(closing.current.get(session.session_id));
    const timer = setInterval(() => physApi.heartbeat(context, session.session_id).catch(fail), 30000);
    return () => { clearInterval(timer); closing.current.set(session.session_id, setTimeout(() => physApi.close(context, session.session_id).catch(() => {}), 100)); };
  }, [context, session?.session_id]);
  useEffect(() => {
    if (!output || output.status !== 'running') return;
    const timer = setInterval(() => physApi.status(context, output.visualization_id, output.export_id).then(setOutput).catch(fail), 500);
    return () => clearInterval(timer);
  }, [output?.export_id, output?.status, context]);
  const perform = async (fn) => { setError(''); setBusy(true); try { return await fn(); } catch (e) { fail(e); } finally { setBusy(false); } };
  const snapshot = () => physApi.command(context, session.session_id, {operation:'snapshot'});
  return { snapshot, visibility: visible => physApi.command(context, session.session_id, {operation:'visibility', visible}), needsSave: async () => !asset || JSON.stringify(canonical((await snapshot()).spec))!==JSON.stringify(canonical(asset.spec)), apply: async spec => physApi.command(context, session.session_id, {operation:'apply',spec}), context, session, asset, assets, error, busy, output, target, setOutput, fail,
    open: (id, renderer) => perform(async () => { const saved = id ? await physApi.read(context, id) : null; const next = await physApi.create(context, saved?.spec, renderer); setSession(next); setAsset(saved); }),
    save: (name) => perform(async () => { const snapshot = await physApi.command(context, session.session_id, { operation: 'snapshot' }); const saved = await physApi.save(context, { name, spec: snapshot.spec, ...(asset ? { visualization_id: asset.visualization_id, expected_revision: asset.revision } : {}), request_id: crypto.randomUUID() }); setAsset({...saved,spec:snapshot.spec}); await refresh(); return saved; }),
    export: (options) => perform(async () => { if (!asset) throw new Error('请先保存配置，导出固定修订'); const current = await snapshot(); if(JSON.stringify(canonical(current.spec))!==JSON.stringify(canonical(asset.spec))) throw new Error('画面存在未保存改动，请先保存当前配置再导出'); if(options.format === 'csv') { const snapshot = await physApi.command(context, session.session_id, {operation:'snapshot'}); if(!snapshot.extraction) throw new Error('请先执行空间或时序提取'); options = {...options, ...snapshot.extraction}; } setOutput(await physApi.export(context, asset.visualization_id, asset.revision, options)); }),
    cancel: () => perform(async () => setOutput(await physApi.cancel(context, output.visualization_id, output.export_id))),
  };
}

export default usePhysField;
