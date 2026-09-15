/** 原可视化应用壳；独立和嵌入模式共用模块与任务上下文。 */
import { lazy, Suspense, useEffect, useMemo, useRef, useState } from 'react';
import { App as AntApp, Avatar, Button, ConfigProvider, Result, Skeleton, theme, Tooltip } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import {
  BellOutlined, BulbOutlined, CodeOutlined, DatabaseOutlined, FileTextOutlined,
  MenuOutlined, QuestionCircleOutlined, SyncOutlined
} from '@ant-design/icons';
import { HashRouter, Link, Navigate, Route, Routes, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ArtifactDetailPage as ArtifactDetail, DataAssetsPage as DataAssets } from './modules/dataAssets/index.js';
import { StorageScopeProvider } from './app/StorageScopeProvider.jsx';
import { runningTasks, workspace } from './app/workspace.js';

// 应用壳只从模块index.js加载业务页面，避免跨模块访问内部文件。
const RecommendationsPage = lazy(() => import('./modules/visTaskManage/index.js').then((module) => ({ default: module.RecommendationsPage })));
const ExamplePage = lazy(() => import('./modules/visTaskManage/index.js').then((module) => ({ default: module.ExamplePage })));
const SpecsPage = lazy(() => import('./modules/visTaskManage/index.js').then((module) => ({ default: module.SpecsPage })));
const VisualizationConfiguratorPage = lazy(() => import('./modules/visTaskManage/index.js').then((module) => ({ default: module.VisualizationConfiguratorPage })));
const ReportsPage = lazy(() => import('./modules/reportManage/index.js').then((module) => ({ default: module.ReportsPage })));
const ReportPage = lazy(() => import('./modules/reportManage/index.js').then((module) => ({ default: module.ReportPage })));
const ReportComposerPage = lazy(() => import('./modules/reportDesigner/index.js').then((module) => ({ default: module.ReportComposerPage })));

const PhysFieldWorkspacePage = lazy(() => import('./modules/visPhysField/index.js').then((module) => ({ default: module.PhysFieldWorkspacePage })));

const navItems = [
  { key: 'assets', label: '数据资产', mobileLabel: '资产', icon: DatabaseOutlined, to: '/' },
  { key: 'recommendations', label: '可视化推荐', mobileLabel: '推荐', icon: BulbOutlined, to: '/recommendations/scalar' },
  { key: 'specs', label: '方法与配置', mobileLabel: '方法配置', icon: CodeOutlined, to: '/specs' },
  { key: 'reports', label: '报告中心', mobileLabel: '报告', icon: FileTextOutlined, to: '/reports' }
];

function readSeedTokens() {
  const style = getComputedStyle(document.documentElement);
  const value = (name) => style.getPropertyValue(name).trim();
  return {
    bg: value('--seed-bg') || '#f4f6fa', surface: value('--seed-surface') || '#fff', fg: value('--seed-fg') || '#182230',
    primary: value('--seed-primary') || '#1677ff', accent: value('--seed-accent') || '#0e9f9f', radius: Number.parseInt(value('--seed-radius'), 10) || 8
  };
}

function luminance(hex) {
  const value = (hex || '').replace('#', '');
  if (value.length < 6) return 1;
  return (0.2126 * Number.parseInt(value.slice(0, 2), 16) + 0.7152 * Number.parseInt(value.slice(2, 4), 16) + 0.0722 * Number.parseInt(value.slice(4, 6), 16)) / 255;
}

function Brand() {
  return <Link className="v2-brand" to="/"><span className="v2-brand-mark" aria-hidden="true"><svg viewBox="0 0 24 24"><path d="M3 18 8.3 6.8l4.1 7 3.1-4.2L21 18" /><circle cx="8.3" cy="6.8" r="1.7" /></svg></span><span><strong>AI4E VizReport</strong><small>科学数据可视化报告平台</small></span></Link>;
}

function RouteAssets() {
  const navigate = useNavigate();
  return <DataAssets onOpenDetail={(id) => navigate(`/assets/${id}`)} onOpenRecommend={(id) => navigate(`/examples/${id}`)} />;
}

function RouteArtifact() {
  const { artifactId } = useParams();
  const navigate = useNavigate();
  return <ArtifactDetail artifactId={artifactId} onBack={() => navigate('/')} onConfigure={(id, recommendationId) => navigate(`/assets/${id}/visualizations/new/${recommendationId}`)} />;
}

function WorkspaceRoutes() {
  return <Routes>
    <Route path="/phys" element={<PhysFieldWorkspacePage />} />
    <Route path="/" element={<RouteAssets />} />
    <Route path="/assets/:artifactId" element={<RouteArtifact />} />
    <Route path="/assets/:artifactId/visualizations/new/:recommendationId" element={<VisualizationConfiguratorPage />} />
    <Route path="/visualizations/:visualizationId" element={<VisualizationConfiguratorPage />} />
    <Route path="/visualizations/:visualizationId/edit" element={<VisualizationConfiguratorPage />} />
    <Route path="/recommendations" element={<Navigate replace to="/recommendations/scalar" />} />
    <Route path="/recommendations/:kind" element={<RecommendationsPage />} />
    <Route path="/examples/:artifactId" element={<ExamplePage />} />
    <Route path="/specs" element={<SpecsPage />} />
    <Route path="/specs/:specId/v/:version" element={<SpecsPage />} />
    <Route path="/reports" element={<ReportsPage />} />
    <Route path="/reports/:reportId" element={<ReportPage />} />
    <Route path="/reports/:reportId/edit" element={<ReportComposerPage />} />
    <Route path="*" element={<Result status="404" title="页面不存在" subTitle="这个链接不属于当前工作区。" extra={<Link to="/"><Button type="primary">返回数据资产</Button></Link>} />} />
  </Routes>;
}

function Shell() {
  const location = useLocation();
  const [mobileMenu, setMobileMenu] = useState(false);
  const contentRef = useRef(null);
  useEffect(() => {
    const content = contentRef.current;
    if (!content) return undefined;
    const reset = () => {
      content.scrollTop = 0;
      content.scrollLeft = 0;
    };
    // Reset once for the route commit and once after the lazy page/layout has
    // settled. This prevents browser scroll anchoring from reopening a newly
    // configured asset or report halfway down the workspace.
    reset();
    const frame = requestAnimationFrame(reset);
    return () => cancelAnimationFrame(frame);
  }, [location.key, location.pathname]);
  const embedded = new URLSearchParams(location.search).get('embed') === '1';
  if (embedded) return <main className="v2-embed-content"><Suspense fallback={<Skeleton active paragraph={{ rows: 8 }} />}><WorkspaceRoutes /></Suspense></main>;
  const active = location.pathname.startsWith('/recommendations') || location.pathname.startsWith('/examples') ? 'recommendations' : location.pathname.startsWith('/specs') ? 'specs' : location.pathname.startsWith('/reports') ? 'reports' : 'assets';
  const pageLabel = navItems.find((item) => item.key === active)?.label;
  return <div className="v2-shell">
    <aside className={`v2-sidebar ${mobileMenu ? 'is-open' : ''}`}><Brand /><nav aria-label="主导航">{navItems.map((item) => { const Icon = item.icon; return <Link key={item.key} className={active === item.key ? 'is-active' : ''} to={item.to} onClick={() => setMobileMenu(false)}><Icon /><span>{item.label}</span></Link>; })}</nav><div className="v2-storage"><span>存储用量</span><strong>{workspace.storageUsedGB} / {workspace.storageQuotaGB} GB</strong><i><b style={{ width: `${workspace.storageUsedGB / workspace.storageQuotaGB * 100}%` }} /></i></div></aside>
    {mobileMenu ? <button className="mobile-scrim" aria-label="关闭导航" onClick={() => setMobileMenu(false)} /> : null}
    <div className="v2-main-column">
      <header className="v2-topbar"><button className="mobile-menu-button" aria-label="打开导航" onClick={() => setMobileMenu(true)}><MenuOutlined /></button><div className="mobile-brand"><Brand /></div><div className="v2-workspace"><strong>{pageLabel}</strong><span>{workspace.id} · 租户工作区</span></div><div className="v2-top-actions"><Button className="task-button" icon={<SyncOutlined spin />}><b>{runningTasks.length}</b> 个任务进行中</Button><Tooltip title="通知"><Button type="text" aria-label="通知" icon={<BellOutlined />} /></Tooltip><Tooltip title="帮助"><Button type="text" aria-label="帮助" icon={<QuestionCircleOutlined />} /></Tooltip><Avatar size={30}>原</Avatar><span className="user-name">{workspace.user}</span></div></header>
      <main ref={contentRef} className="v2-content"><Suspense fallback={<div className="workspace-page"><Skeleton active paragraph={{ rows: 10 }} /></div>}><WorkspaceRoutes /></Suspense></main>
    </div>
    <nav className="mobile-bottom-nav" aria-label="移动端主导航">{navItems.map((item) => { const Icon = item.icon; return <Link key={item.key} className={active === item.key ? 'is-active' : ''} to={item.to}><Icon /><span>{item.mobileLabel}</span></Link>; })}</nav>
  </div>;
}

export default function App() {
  const [seed, setSeed] = useState(readSeedTokens);
  useEffect(() => {
    let frame = 0;
    const sync = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(() => setSeed(readSeedTokens())); };
    const observer = new MutationObserver(sync);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['style', 'class', 'data-theme'] });
    return () => { observer.disconnect(); cancelAnimationFrame(frame); };
  }, []);
  const antdTheme = useMemo(() => ({ cssVar: true, hashed: false, algorithm: luminance(seed.bg) < 0.45 ? theme.darkAlgorithm : theme.defaultAlgorithm, token: { colorPrimary: seed.primary, colorInfo: seed.primary, colorLink: seed.primary, colorBgLayout: seed.bg, colorBgContainer: seed.surface, colorText: seed.fg, borderRadius: seed.radius, fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif' } }), [seed]);
  return <ConfigProvider locale={zhCN} theme={antdTheme}><AntApp className="vis-app-root"><HashRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}><StorageScopeProvider><Shell /></StorageScopeProvider></HashRouter></AntApp></ConfigProvider>;
}
