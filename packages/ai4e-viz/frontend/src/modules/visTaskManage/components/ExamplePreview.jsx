/** 可视化任务案例预览：按 renderer owner 选择共享渲染器或几何模块。 */

import { lazy, Suspense, useCallback, useEffect, useRef, useState } from 'react';
import { Alert, Button, Empty, Skeleton, Table, Tag } from 'antd';
import ReactMarkdown from 'react-markdown';
import { Link } from 'react-router-dom';
import { GeometryViewer as GEOViewer } from '../../visGeometry/index.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import { apiExample, apiRendererHealth } from '../api.js';
import { apiVisualization } from '../../visIO/index.js';

const EChartsRenderer = lazy(() => import('../../../infrastructure/rendering/renderers/EChartsRenderer.jsx'));
const PlotlyRenderer = lazy(() => import('../../../infrastructure/rendering/renderers/PlotlyRenderer.jsx'));
const VegaRenderer = lazy(() => import('../../../infrastructure/rendering/renderers/VegaRenderer.jsx'));
const ReactFlowRenderer = lazy(() => import('../../../infrastructure/rendering/renderers/ReactFlowRenderer.jsx'));
const stableRowKey = (row) => row.id ?? row.point_id ?? row.key ?? JSON.stringify(row);
const sourceColors = { 'file-fixture': 'blue', 'generated-demo': 'cyan', 'open-source-reconstruction': 'geekblue', 'negative-validation': 'red', 'user-upload': 'green' };

function RendererLoading() {
  return <div className="renderer-loading"><Skeleton active paragraph={{ rows: 5 }} /></div>;
}

function PerspectiveTable({ data, params }) {
  const ref = useRef(null);
  const [ready, setReady] = useState(false);
  useEffect(() => {
    let active = true;
    Promise.all([import('@finos/perspective-viewer'), import('@finos/perspective-viewer-datagrid')])
      .then(async () => {
        if (!active || !ref.current) return;
        await ref.current.load(data.rows);
        const selectedColumns = (params.columns ?? []).filter((column) => data.columns.includes(column));
        await ref.current.restore({ columns: selectedColumns.length ? selectedColumns : undefined, settings: Boolean(params.show_search) });
        if (active) setReady(true);
      })
      .catch(() => setReady(false));
    return () => { active = false; };
  }, [data, params.columns, params.show_search]);
  const rows = data.rows ?? [];
  const visible = (params.columns?.length ? params.columns : data.columns ?? Object.keys(rows[0] ?? {})).filter((key) => key in (rows[0] ?? {}));
  const columns = visible.map((key) => ({ title: key, dataIndex: key, key, ellipsis: true }));
  return <div className={`perspective-wrap density-${params.density ?? 'normal'}`}>
    <perspective-viewer ref={ref} plugin="Datagrid" className="perspective-frame" aria-label="可筛选排序的 Perspective 数据表" style={{ display: ready ? 'block' : 'none' }} />
    {ready ? null : <Table size="small" rowKey={stableRowKey} columns={columns} dataSource={rows.slice(0, params.page_size ?? 20)} pagination={false} scroll={{ x: 720 }} />}
  </div>;
}

function ScalarEvidence({ payload }) {
  const params = payload.resolved_spec?.params ?? {};
  const data = payload.data;
  const precision = params.precision ?? 2;
  const value = typeof data.value === 'number' ? data.value.toFixed(precision) : data.value;
  return <div className="scalar-evidence" style={{ background: params.background_color }}><strong>{value}</strong><span>{params.unit || data.unit}</span><p>目标 {params.target ?? data.target}{params.unit || data.unit} · {payload.artifact.takeaway}</p></div>;
}

function BrowserNativeEvidence({ payload }) {
  const { artifact, data } = payload;
  const params = payload.resolved_spec?.params ?? {};
  if (artifact.kind === 'text_document') return <article className={`markdown-evidence theme-${params.theme ?? 'report'}`} style={{ maxWidth: params.max_width ?? 820 }}><ReactMarkdown>{data.markdown}</ReactMarkdown></article>;
  if (artifact.kind === 'image') return <figure className="native-media"><img src={data.url} alt={params.alt_text || data.alt || artifact.name} style={{ objectFit: params.fit === 'natural' ? undefined : params.fit }} /><figcaption>{params.caption || artifact.takeaway}</figcaption></figure>;
  if (artifact.kind === 'video') return <figure className="native-media"><video controls={params.controls !== false} muted={params.muted !== false} autoPlay={Boolean(params.autoplay)} loop={Boolean(params.loop)} playsInline poster={params.poster || data.poster_url} src={data.url}>浏览器不支持视频播放。</video><figcaption>{params.caption || artifact.takeaway}</figcaption></figure>;
  return <Empty description="浏览器原生渲染器不支持当前数据" />;
}

function TrameEvidence({ payload, rendererState, onRetryHealth }) {
  const hasFallback = Boolean(payload.renderer.fallback_url);
  const [showFallback, setShowFallback] = useState(hasFallback);
  const [interactiveMounted, setInteractiveMounted] = useState(!hasFallback);
  useEffect(() => {
    const nextHasFallback = Boolean(payload.renderer.fallback_url);
    setShowFallback(nextHasFallback);
    setInteractiveMounted(!nextHasFallback);
  }, [payload.renderer.fallback_url, payload.renderer.url]);
  useEffect(() => {
    if (rendererState === 'live' && payload.renderer.url && !payload.renderer.fallback_url) {
      setInteractiveMounted(true);
      setShowFallback(false);
    } else if (rendererState !== 'live' || !payload.renderer.url) {
      setShowFallback(true);
    }
  }, [payload.renderer.fallback_url, payload.renderer.url, rendererState]);
  const interactive = rendererState === 'live' && payload.renderer.url;
  const toggleInteractive = useCallback(() => {
    if (showFallback) setInteractiveMounted(true);
    setShowFallback((value) => !value);
  }, [showFallback]);
  return <div className="remote-evidence">
    <div className="remote-evidence-bar">
      <span><b>{payload.renderer.label}</b> · {interactive ? showFallback ? '交互服务在线，当前显示同源静态证据' : '交互服务在线' : '交互服务离线，显示同源数据证据'}</span>
      <div className="remote-evidence-actions">
        {interactive && hasFallback ? <Button onClick={toggleInteractive}>{showFallback ? '打开交互视图' : '查看静态降级'}</Button> : null}
        <Button onClick={onRetryHealth}>刷新服务状态</Button>
      </div>
    </div>
    {interactive && interactiveMounted
      ? <iframe
          className="trame-frame"
          title={`${payload.artifact.name} · Trame/vtk.js 交互视图`}
          src={payload.renderer.url}
          hidden={showFallback}
          aria-hidden={showFallback}
        />
      : null}
    {!interactive || showFallback
      ? payload.renderer.fallback_url
        ? <figure className="data-derived-fallback"><img src={payload.renderer.fallback_url} alt={`${payload.artifact.name} 的 Trame/vtk.js 同参数静态表示`} /><figcaption>{payload.data.fallback_label ?? '同源同参数静态证据'}</figcaption></figure>
        : <Alert type="warning" showIcon message="Trame/vtk.js 表示当前不可用" description={<span>原始数据资产、冻结的可视化配置与数据摘要已保留；当前没有由同一渲染器生成的静态快照，因此不使用 ECharts 或其他引擎冒充。{payload.data.fallback_label ? ` 数据摘要：${payload.data.fallback_label}。` : ''}</span>} />
      : null}
  </div>;
}

function RendererEvidence({ payload, rendererState, onRetryHealth }) {
  const owner = payload.renderer.owner;
  const params = payload.resolved_spec?.params ?? {};
  if (owner === 'trame-vtkjs') return <TrameEvidence payload={payload} rendererState={rendererState} onRetryHealth={onRetryHealth} />;
  if (owner === 'o3dv') return <GEOViewer modelUrl={payload.renderer.url} title={payload.artifact.name} height={params.height ?? 480} fallbackUrl={payload.renderer.fallback_url} parameters={params} />;
  if (owner === 'perspective') return <PerspectiveTable data={payload.data} params={params} />;
  if (owner === 'react') return <ScalarEvidence payload={payload} />;
  if (owner === 'browser-native') return <BrowserNativeEvidence payload={payload} />;
  if (owner === 'echarts-svg') return <Suspense fallback={<RendererLoading />}><EChartsRenderer payload={payload} /></Suspense>;
  if (owner === 'plotly') return <Suspense fallback={<RendererLoading />}><PlotlyRenderer payload={payload} /></Suspense>;
  if (owner === 'vega') return <Suspense fallback={<RendererLoading />}><VegaRenderer payload={payload} /></Suspense>;
  if (owner === 'react-flow') return <Suspense fallback={<RendererLoading />}><ReactFlowRenderer payload={payload} /></Suspense>;
  return <Empty description={`暂无 ${owner} 渲染适配器`} />;
}

export default function ExamplePreview({ artifactId, recommendationId, visualizationId, payload, embedded = false }) {
  const loader = useCallback(() => {
    if (payload) return Promise.resolve({ ...payload, updated_at: new Date().toISOString() });
    if (visualizationId) return apiVisualization(visualizationId).then((record) => record.payload);
    return apiExample(artifactId, recommendationId);
  }, [artifactId, payload, recommendationId, visualizationId]);
  const cacheKey = visualizationId ? `visualization:${visualizationId}` : `example:${artifactId}:${recommendationId ?? 'latest'}`;
  const remote = useRemoteSnapshot(cacheKey, loader, null);
  const healthLoader = useCallback(() => apiRendererHealth(), []);
  const health = useRemoteSnapshot('renderer-health', healthLoader, null);
  const data = payload ?? remote.data;
  const state = payload ? 'live' : remote.state;
  const updatedAt = payload ? new Date().toISOString() : remote.updatedAt;
  const error = payload ? null : remote.error;
  const retry = remote.retry;
  const [details, setDetails] = useState(!embedded);
  const rendererState = data?.renderer?.owner === 'trame-vtkjs'
    ? health.data?.renderers?.['trame-vtkjs']?.state ?? 'offline'
    : data?.renderer?.status ?? state;
  const connectionState = data?.artifact?.validation === 'blocked' ? 'error' : data?.renderer?.owner === 'trame-vtkjs' ? rendererState : state;
  const resolvedArtifactId = data?.artifact?.id ?? artifactId;

  if (!data && state === 'offline') return <Alert type="warning" showIcon message="案例服务离线" description={<span>尚无最近快照。启动后端后可重试。 <Button size="small" onClick={retry}>重试</Button></span>} />;
  if (!data) return <Skeleton active />;

  return <article className={`example-preview ${embedded ? 'is-embedded' : ''}`} aria-labelledby={`example-${resolvedArtifactId}`}>
    <header className="example-preview-head">
      <div>
        <div className="example-meta-row"><div className="example-id">数据家族 {data.artifact.family} · 数据语义类型 {data.artifact.kind} · 案例 ID {resolvedArtifactId}</div><Tag color={sourceColors[data.artifact.case_type] ?? 'default'}>{data.artifact.case_type_label ?? '案例数据'}</Tag></div>
        <h2 id={`example-${resolvedArtifactId}`}>{data.artifact.name}</h2><p>{data.artifact.description}</p>
      </div>
      <ConnectionStatus state={connectionState} updatedAt={updatedAt} onRetry={retry} />
    </header>
    <div className="example-takeaway"><strong>阅读结论</strong><span>{data.artifact.takeaway}</span></div>
    {data.artifact.validation === 'blocked'
      ? <Alert type="error" showIcon message="校验阻断" description="声明为 FLD/field，但 STL 不包含任何物理场数组。请改为 GEO/mesh 或补充场数据。" />
      : <div className="evidence-canvas"><RendererEvidence payload={data} rendererState={rendererState} onRetryHealth={health.retry} /></div>}
    <footer className="example-preview-foot">
      <span>渲染器：<b>{data.renderer.owner}</b> · 可视化方法 ID：<code>{data.resolved_spec.function_id}</code>{visualizationId ? <> · 可视化结果 ID：<code>{visualizationId}</code></> : <> · 默认参数预览（未保存）</>}</span>
      <Button type="link" onClick={() => setDetails((value) => !value)}>{details ? '收起来源' : '查看来源'}</Button>
      {embedded ? <Link to={visualizationId ? `/visualizations/${visualizationId}` : `/examples/${resolvedArtifactId}`}>{visualizationId ? '打开已保存结果' : '打开默认参数预览'}</Link> : null}
    </footer>
    {details ? <div className="source-note">{data.artifact.source_note} · 数据格式 {data.artifact.format}{data.artifact.source_url ? <> · <a href={data.artifact.source_url} target="_blank" rel="noreferrer">查看开源来源</a></> : null}{error ? ` · 当前连接错误：${error.message}` : ''}</div> : null}
  </article>;
}
