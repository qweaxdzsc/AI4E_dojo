/** 数据资产详情页面：组织画像、检测、分类修正和可视化推荐。 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert, App as AntApp, Button, Descriptions, Empty, Result, Skeleton, Space, Steps, Table, Tabs, Tag
} from 'antd';
import {
  ArrowLeftOutlined, CopyOutlined, ExperimentOutlined,
  FileSearchOutlined, ReloadOutlined, SettingOutlined, WarningOutlined
} from '@ant-design/icons';
import { apiArtifact, apiClassifyArtifact } from '../api.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import { apiAnalyzeArtifact } from '../../visDatasets/index.js';
import { apiArtifactRecommendations, ExamplePreview } from '../../visTaskManage/index.js';

const KIND_LABELS = {
  scalar: 'PLT / 标量（scalar）', table: 'PLT / 表格（table）', series: 'PLT / 序列（series）', timeseries: 'PLT / 序列（series）', distribution: 'PLT / 分布（distribution）',
  matrix: 'PLT / 矩阵（matrix）', tensor: 'PLT / 张量（tensor）', raster: 'FLD / 栅格场（raster）', field: 'FLD / 物理场（field）', volume: 'FLD / 体数据（volume）',
  point_set: 'ENT / 点集（point_set）', trajectory: 'ENT / 轨迹（trajectory）', graph: 'ENT / 关系图（graph）', mesh: 'GEO / 几何网格（mesh）',
  text_document: 'ASSET / 文本文档（text_document）', image: 'ASSET / 静态图像（image）', video: 'ASSET / 视频（video）'
};

function ProfileTable({ profile }) {
  const rows = [];
  const add = (label, value) => { if (value !== undefined && value !== null && value !== '') rows.push({ label, value: typeof value === 'object' ? JSON.stringify(value, null, 2) : String(value) }); };
  add('解析摘要', profile.summary);
  add('识别的数据语义类型', KIND_LABELS[profile.inferred_kind] ?? profile.inferred_kind);
  add('行数', profile.rows?.toLocaleString());
  add('列', profile.columns?.join('、'));
  add('数值列', profile.numeric_columns?.join('、'));
  add('时间 / 顺序列', profile.time_column);
  add('日志等级', profile.level_counts);
  add('数组', profile.arrays);
  add('场变量', profile.field_variables);
  add('维度', profile.dimensions?.join(' × ') ?? profile.shape?.join(' × '));
  add('点 / 单元', profile.points !== undefined ? `${profile.points.toLocaleString()} / ${profile.cells?.toLocaleString()}` : null);
  add('包围盒', profile.bounds ?? profile.spatial?.bbox);
  return <Table size="small" rowKey="label" pagination={false} columns={[{ title: '画像字段', dataIndex: 'label', width: 150 }, { title: '实际解析结果', dataIndex: 'value', render: (value) => value.startsWith('{') || value.startsWith('[') ? <pre className="profile-json">{value}</pre> : <span>{value}</span> }]} dataSource={rows} />;
}

function RecommendationTable({ recommendations, selected, onSelect, blocked }) {
  const rows = recommendations.detected_candidates ?? recommendations.candidates ?? [];
  const columns = [
    { title: '选项', dataIndex: 'task_label', width: 190, render: (value, row) => <button className={`recommendation-name ${selected === row.recommendation_id ? 'is-selected' : ''}`} onClick={() => onSelect(row.recommendation_id)} aria-pressed={selected === row.recommendation_id}><strong>{value}</strong><span>{row.reason}</span></button> },
    { title: '方法 / 渲染器', dataIndex: 'function_id', width: 230, render: (value, row) => <div className="recommendation-engine"><code>{value}</code><span>{row.renderer_label}</span></div> },
    { title: '编码', dataIndex: 'encoding', render: (value) => <code className="encoding-code">{Object.keys(value ?? {}).length ? JSON.stringify(value) : '自动'}</code> },
    { title: '能力', dataIndex: 'capabilities', width: 148, render: (value, row) => <Space size={[4, 4]} wrap><Tag>{value?.interactive ? '交互' : '静态'}</Tag><Tag>{row.offline ? '离线' : '需服务'}</Tag><Tag color="blue">{row.score} 分</Tag></Space> }
  ];
  return <><Table rowKey="recommendation_id" size="small" pagination={false} columns={columns} dataSource={rows} scroll={{ x: 880 }} /><p className="table-footnote">{blocked ? '当前声明被阻断，但仍允许按识别出的语义类型预览；修正类型后方可保存可视化配置。' : '所有方法选项均由数据画像确定性生成；没有 Agent 或隐藏模型调用。'}</p></>;
}

export default function ArtifactDetail({ artifactId, onBack, onConfigure }) {
  const { message } = AntApp.useApp();
  const loader = useCallback(async () => {
    const [artifact, recommendations] = await Promise.all([apiArtifact(artifactId), apiArtifactRecommendations(artifactId)]);
    return { artifact, recommendations, updated_at: artifact.updated_at };
  }, [artifactId]);
  const remote = useRemoteSnapshot(`artifact:${artifactId}`, loader, null);
  const artifact = remote.data?.artifact;
  const recommendations = remote.data?.recommendations;
  const candidates = recommendations?.detected_candidates ?? recommendations?.candidates ?? [];
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const first = candidates[0];
    setSelected(first?.recommendation_id ?? null);
  }, [artifactId, candidates.length]);

  const selectedCandidate = useMemo(() => candidates.find((item) => item.recommendation_id === selected) ?? candidates[0], [candidates, selected]);

  const reanalyze = async () => {
    try { await apiAnalyzeArtifact(artifactId); remote.retry(); message.success('数据画像与推荐已重新生成'); } catch (error) { message.error(error.message); }
  };

  const fixClassification = async () => {
    try {
      await apiClassifyArtifact(artifactId, { declared_kind: recommendations.kind, reason: '按解析器识别结果修正声明的语义类型' });
      remote.retry(); message.success('已创建语义类型修正版本，原版本未被覆盖');
    } catch (error) { message.error(error.message); }
  };

  if (!artifact && remote.error?.status === 404) return <Result status="404" title="数据资产不存在" extra={<Button type="primary" onClick={onBack}>返回数据资产</Button>} />;
  if (!artifact && remote.state === 'offline') return <Result status="warning" title="数据资产服务离线" subTitle="当前没有该数据资产的最近快照。" extra={<Button onClick={remote.retry}>重试</Button>} />;
  if (!artifact || !recommendations) return <div className="page"><Skeleton active paragraph={{ rows: 12 }} /></div>;

  const blocked = recommendations.blocked;
  const pipeline = [
    { title: '保存数据资产', description: `SQLite · SHA ${artifact.sha256.slice(0, 8)}`, status: 'finish' },
    { title: '解析数据画像', description: artifact.profile?.summary ?? '解析失败', status: artifact.parse_status === 'ready' ? 'finish' : 'error' },
    { title: '识别语义类型', description: blocked ? '声明类型与识别结果不一致' : '识别与校验完成', status: blocked ? 'error' : 'finish' },
    { title: '推荐可视化方法', description: `${candidates.length} 个方法选项`, status: candidates.length ? 'finish' : 'wait' },
    { title: '配置并预览', description: selectedCandidate ? '等待调整参数' : '等待选择方法', status: selectedCandidate ? 'process' : 'wait' },
    { title: '保存配置与结果', description: '生成不可变配置版本和可复用结果', status: 'wait' }
  ];

  const overviewItems = [
    { key: 'id', label: '数据资产 ID', children: <code>{artifact.id}</code> },
    { key: 'file', label: '源文件', children: artifact.file_name },
    { key: 'format', label: '文件格式', children: <code>{artifact.format}</code> },
    { key: 'kind', label: '声明类型 / 识别类型', children: <span>{KIND_LABELS[artifact.declared_kind] ?? artifact.declared_kind ?? '自动'} → <b>{KIND_LABELS[artifact.detected_kind] ?? artifact.detected_kind}</b></span> },
    { key: 'size', label: '大小', children: artifact.size_label },
    { key: 'source', label: '来源 / 数据集', children: `${artifact.source}${artifact.dataset_id ? ` · ${artifact.dataset_id}` : ''}` },
    { key: 'version', label: '语义类型版本', children: `v${artifact.version}` },
    { key: 'updated', label: '更新时间', children: new Date(artifact.updated_at).toLocaleString('zh-CN') }
  ];

  return <div className="page artifact-runtime" data-component="Artifact Detail" data-qoder-id="qel-artifact-detail-runtime">
    <Button icon={<ArrowLeftOutlined />} onClick={onBack} className="back-button">返回数据资产</Button>
    <header className="artifact-runtime-header">
      <div><div className="artifact-kicker">数据家族 / 数据语义类型：{KIND_LABELS[artifact.detected_kind] ?? artifact.detected_kind} · 数据资产 ID {artifact.id}</div><h1>{artifact.name}</h1><p>{artifact.profile?.summary ?? '该文件尚未完成解析。'}</p></div>
      <div className="artifact-header-actions"><ConnectionStatus state={blocked ? 'error' : remote.state} updatedAt={remote.updatedAt} onRetry={remote.retry} /><Button icon={<CopyOutlined />} onClick={() => navigator.clipboard?.writeText(artifact.sha256)}>复制哈希</Button><Button icon={<ReloadOutlined />} onClick={reanalyze}>重新分析</Button></div>
    </header>

    <section className="panel-surface pipeline-panel"><Steps responsive items={pipeline} /></section>

    {blocked ? <Alert className="classification-alert" type="error" showIcon icon={<WarningOutlined />} message="声明类型是 FLD / 物理场（field），识别类型是 GEO / 几何网格（mesh）" description="系统不会把没有物理场数组的 STL 几何当作物理场。你可以先按识别类型预览，或保存一个新的类型修正版本。" action={<Space direction="vertical"><Button onClick={() => setSelected(candidates[0]?.recommendation_id)}>按识别类型预览</Button><Button type="primary" onClick={fixClassification}>修正为几何网格（mesh）</Button></Space>} /> : null}

    <Tabs defaultActiveKey="recommendations" items={[
      { key: 'overview', label: '概览与画像', children: <div className="artifact-tab-stack"><section className="panel-surface"><Descriptions column={{ xs: 1, sm: 2, lg: 4 }} items={overviewItems} /></section><section className="panel-surface"><header className="section-heading"><FileSearchOutlined /><div><h2>真实解析画像</h2><p>以下内容来自源文件，不是前端样例数据。</p></div></header><ProfileTable profile={artifact.profile ?? {}} /></section></div> },
      { key: 'recommendations', label: <span>推荐方法 <Tag color="blue">{candidates.length}</Tag></span>, children: <div className="artifact-tab-stack"><section className="panel-surface"><header className="section-heading"><ExperimentOutlined /><div><h2>基于数据画像推荐的可视化方法</h2><p>默认方法 100 分，离线能力加 2 分；任务优先级保证排序稳定。</p></div></header>{candidates.length ? <RecommendationTable recommendations={recommendations} selected={selected} onSelect={setSelected} blocked={blocked} /> : <Empty description="没有可用方法" />}</section>{selectedCandidate ? <section className="panel-surface recommendation-selection"><div><span>已选方法</span><strong>{selectedCandidate.task_label}</strong><code>{selectedCandidate.function_id} · {selectedCandidate.renderer_label}</code><small>{Object.keys(selectedCandidate.parameter_schema?.properties ?? {}).length} 个可配置参数 · 参数定义 {selectedCandidate.schema_revision}</small></div><Button type="primary" size="large" icon={<SettingOutlined />} disabled={blocked} onClick={() => onConfigure?.(artifactId, selectedCandidate.recommendation_id)}>配置并预览</Button></section> : null}</div> },
      { key: 'result', label: '默认参数预览', children: selectedCandidate ? <section className="panel-surface result-panel"><Alert type="info" showIcon message="这是未保存的默认参数预览" description="预览用于确认方法是否适合当前数据，不是已保存的可视化结果。进入“配置并预览”并保存后，系统才会创建不可变配置版本和可复用结果。" /><ExamplePreview artifactId={artifactId} recommendationId={selectedCandidate.recommendation_id} /></section> : <Empty description="请先选择可视化方法" /> },
      { key: 'lineage', label: '版本与可追溯性', children: <section className="panel-surface lineage-panel"><h2>内容与类型谱系</h2><p><code>sha256:{artifact.sha256}</code></p><p>内容哈希用于上传去重；语义类型修正只增加版本，不覆盖原始文件或旧声明。</p><p>当前类型版本：<b>v{artifact.version}</b> · 最近更新 {new Date(artifact.updated_at).toLocaleString('zh-CN')}</p></section> }
    ]} />
  </div>;
}
