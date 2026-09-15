/** 可视化推荐页面：按语义类型组合方法目录和可运行案例。 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Button, Select, Tag } from 'antd';
import { ArrowRightOutlined, CloudDownloadOutlined, SettingOutlined } from '@ant-design/icons';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { apiCatalog, apiSpecs } from '../api.js';
import { UI_TERMS } from '../terminology.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import { fallbackCatalog, fallbackSpecs } from '../fallback.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import ExamplePreview from '../components/ExamplePreview.jsx';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

const rendererNames = {
  'echarts-svg': 'ECharts SVG', perspective: 'Perspective', 'trame-vtkjs': 'Trame + vtk.js',
  o3dv: 'Online3DViewer', 'browser-native': '浏览器原生', 'react-flow': 'React Flow',
  plotly: 'Plotly', react: 'React', vega: 'Vega'
};

export default function RecommendationsPage() {
  const { kind: kindParam } = useParams();
  const navigate = useNavigate();
  const catalogRemote = useRemoteSnapshot('catalog-v2', useCallback(() => apiCatalog(), []), fallbackCatalog);
  const specsRemote = useRemoteSnapshot('functions-v2', useCallback(() => apiSpecs(), []), fallbackSpecs);
  const catalog = catalogRemote.data?.counts?.kinds === 19 ? catalogRemote.data : fallbackCatalog;
  const registry = specsRemote.data?.functions?.length === 23 ? specsRemote.data : fallbackSpecs;
  const activeKind = catalog.kinds.find((item) => item.id === kindParam) ?? catalog.kinds[0];
  const methods = useMemo(
    () => registry.functions.filter((item) => item.compatible_kinds.includes(activeKind.id)),
    [activeKind.id, registry.functions]
  );
  const [methodId, setMethodId] = useState(methods[0]?.id);
  const activeMethod = methods.find((item) => item.id === methodId) ?? methods[0];

  useEffect(() => {
    if (!kindParam || !catalog.kinds.some((item) => item.id === kindParam)) navigate(`/recommendations/${activeKind.id}`, { replace: true });
  }, [activeKind.id, catalog.kinds, kindParam, navigate]);

  useEffect(() => setMethodId(methods[0]?.id), [activeKind.id, methods]);

  return (
    <div className="workspace-page recommendations-page">
      <PageTitle
        title="可视化推荐"
        description="先识别数据语义类型，再从兼容方法中选择。每个方法都有格式要求、默认配置和独立案例。"
        meta={<ConnectionStatus state={catalogRemote.state} updatedAt={catalogRemote.updatedAt} onRetry={catalogRemote.retry} />}
        actions={<Link to="/specs"><Button>查看 {registry.counts?.functions ?? registry.functions.length} 个方法 <ArrowRightOutlined /></Button></Link>}
      />
      <div className="catalog-counts" aria-label="注册表统计">
        {[[UI_TERMS.family, catalog.counts.families], [UI_TERMS.kind, catalog.counts.kinds], [UI_TERMS.method, catalog.counts.functions]].map(([label, value]) => <div key={label}><strong>{value}</strong><span>{label}</span></div>)}
      </div>

      <div className="recommendation-layout">
        <aside className="kind-rail" aria-label="数据语义类型目录">
          <div className="mobile-kind-select"><Select value={activeKind.id} onChange={(value) => navigate(`/recommendations/${value}`)} options={catalog.kinds.map((item) => ({ value: item.id, label: `${item.family} · ${item.label}` }))} /></div>
          {catalog.families.map((family) => (
            <section key={family.id}>
              <h2>{family.id}<span>{family.label}</span></h2>
              {catalog.kinds.filter((item) => item.family === family.id).map((item) => (
                <button key={item.id} className={item.id === activeKind.id ? 'is-active' : ''} onClick={() => navigate(`/recommendations/${item.id}`)}>
                  <span>{item.label}</span><small>{item.method_ids.length} 个方法</small>
                </button>
              ))}
            </section>
          ))}
        </aside>

        <main className="kind-detail">
          <section className="kind-summary">
            <div><span className="family-code">{activeKind.family} · {activeKind.id}</span><h2>{activeKind.label}</h2><p>{activeKind.definition}</p></div>
            <div className="method-explainer">
              <div className="method-heading"><h3>兼容的可视化方法</h3><p>选择方法后，下方同步显示该方法的默认配置和案例。</p></div>
              <div className="method-grid" aria-label={`${activeKind.label}可视化方法`}>
                {methods.map((method) => (
                  <button type="button" key={method.id} className={method.id === activeMethod?.id ? 'is-method-active' : ''} onClick={() => setMethodId(method.id)}>
                    <span><strong>{method.label}</strong><Tag color={method.capabilities.offline ? 'green' : 'blue'}>{method.capabilities.offline ? '可离线' : '需要服务'}</Tag></span>
                    <code>{method.id}</code>
                    <p>{method.description}</p>
                    <small>{rendererNames[method.renderer] ?? method.renderer}</small>
                    <div className="format-tags" aria-label="可接受数据格式">{method.accepted_formats.map((format) => <Tag key={format}>{format}</Tag>)}</div>
                  </button>
                ))}
              </div>
            </div>
          </section>

          {activeMethod ? <section className="method-contract panel-surface">
            <div className="section-heading">
              <div><h2><SettingOutlined /> {activeMethod.label}的默认配置</h2><p>点击上方其他方法可切换。保存可视化配置时会复制这些默认值，再允许逐项调整。</p></div>
              <Link to="/specs"><Button>在方法与配置中打开</Button></Link>
            </div>
            <div className="method-contract-grid">
              <dl><div><dt>方法 ID</dt><dd><code>{activeMethod.id}</code></dd></div><div><dt>渲染器</dt><dd>{rendererNames[activeMethod.renderer] ?? activeMethod.renderer}</dd></div><div><dt>输入格式</dt><dd>{activeMethod.accepted_formats.join('、')}</dd></div><div><dt>案例 ID</dt><dd><code>{activeMethod.example_id}</code></dd></div></dl>
              <pre aria-label={`${activeMethod.label}默认配置 JSON`}>{JSON.stringify(activeMethod.default_parameters, null, 2)}</pre>
            </div>
          </section> : null}

          {activeMethod ? <section className="example-section">
            <div className="section-heading"><div><h2>方法案例</h2><p>该案例与当前方法一一配套，数据在本地可重复加载。</p></div><Tag>{activeMethod.example_id}</Tag></div>
            <ExamplePreview artifactId={activeMethod.example_id} embedded />
          </section> : null}

          {activeKind.id === 'mesh' ? <div className="geo-contract"><CloudDownloadOutlined /><div><strong>GEO 契约</strong><p>几何网格由 Online3DViewer 独占；带物理量的场数据使用 Trame + vtk.js。</p></div></div> : null}
        </main>
      </div>
    </div>
  );
}
