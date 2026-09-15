/** 数据资产列表页面：组织上传、筛选、质量状态和详情导航。 */

import { useCallback, useMemo, useState } from 'react';
import { Alert, Button, Drawer, Input, Progress, Select, Space, Table, Tag, Upload } from 'antd';
import {
  ArrowDownOutlined, ArrowUpOutlined, CloudUploadOutlined, DatabaseOutlined,
  InboxOutlined, MinusOutlined, ReloadOutlined
} from '@ant-design/icons';
import { apiArtifacts, apiUpload } from '../api.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';

const { Dragger } = Upload;

const KIND_META = {
  scalar: ['标量', 'PLT', '#1677ff'], table: ['表格', 'PLT', '#1677ff'], series: ['序列', 'PLT', '#0e9f9f'], timeseries: ['时序', 'PLT', '#0e9f9f'],
  distribution: ['分布', 'PLT', '#8250df'], matrix: ['矩阵', 'PLT', '#8250df'], tensor: ['张量', 'PLT', '#8250df'],
  raster: ['栅格场', 'FLD', '#d97706'], field: ['物理场', 'FLD', '#dc2626'], volume: ['体数据', 'FLD', '#b45309'],
  point_set: ['点集', 'ENT', '#18934e'], trajectory: ['轨迹', 'ENT', '#18934e'], graph: ['关系图', 'ENT', '#18934e'],
  mesh: ['几何网格', 'GEO', '#d97706'], text_document: ['文档', 'ASSET', '#64748b'], image: ['图片', 'ASSET', '#64748b'], video: ['视频', 'ASSET', '#64748b']
};

const statusMeta = {
  passed: ['success', '通过'], warning: ['warning', '需关注'], error: ['error', '阻断'], pending: ['default', '待分析']
};

function KindTag({ kind, family }) {
  const [label, fallbackFamily, color] = KIND_META[kind] ?? [kind || '未知', family || '—', '#64748b'];
  const resolvedFamily = family || fallbackFamily;
  return <span className="asset-kind"><i style={{ background: color }} /><span><b>{resolvedFamily}</b> · {label}</span><code>ArtifactKind {kind}</code></span>;
}

function Stat({ label, value, note, trend }) {
  const Icon = trend === 'up' ? ArrowUpOutlined : trend === 'down' ? ArrowDownOutlined : MinusOutlined;
  return <div className="asset-stat"><span>{label}</span><strong>{value}</strong><small><Icon /> {note}</small></div>;
}

export default function DataAssets({ onOpenDetail, onOpenRecommend }) {
  const loader = useCallback(() => apiArtifacts(), []);
  const remote = useRemoteSnapshot('artifacts', loader, null);
  const rows = remote.data?.items ?? [];
  const [kindFilter, setKindFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [query, setQuery] = useState('');
  const [uploadOpen, setUploadOpen] = useState(false);
  const [declaredKind, setDeclaredKind] = useState('auto');
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [uploadError, setUploadError] = useState(null);

  const filtered = useMemo(() => rows.filter((row) => {
    if (kindFilter !== 'all' && row.kind !== kindFilter) return false;
    if (statusFilter !== 'all' && row.validation_status !== statusFilter) return false;
    if (query && !`${row.name}${row.file_name}${row.id}${row.dataset_id ?? ''}`.toLowerCase().includes(query.toLowerCase())) return false;
    return true;
  }), [kindFilter, query, rows, statusFilter]);

  const counts = useMemo(() => ({
    total: rows.length,
    passed: rows.filter((row) => row.validation_status === 'passed').length,
    uploaded: rows.filter((row) => row.source === 'uploaded').length,
    gs: rows.filter((row) => row.dataset_id === 'gs-pino-audit').length
  }), [rows]);

  const resetUpload = () => {
    setFile(null); setUploadResult(null); setUploadError(null); setUploading(false); setDeclaredKind('auto');
  };

  const submitUpload = async () => {
    if (!file) return;
    setUploading(true); setUploadError(null);
    try {
      const result = await apiUpload(file, declaredKind === 'auto' ? null : declaredKind);
      setUploadResult(result);
      remote.retry();
    } catch (error) {
      setUploadError(error.message);
    } finally {
      setUploading(false);
    }
  };

  const columns = [
    { title: '数据资产', dataIndex: 'name', minWidth: 250, render: (_, row) => <button className="asset-name-button" onClick={() => onOpenDetail(row.id)}><strong>{row.name}</strong><span><code>{row.id}</code> · {row.file_name}</span></button> },
    { title: '数据家族 / 数据语义类型', dataIndex: 'kind', width: 210, render: (kind, row) => <KindTag kind={kind} family={row.family} /> },
    { title: '文件格式', dataIndex: 'format', width: 90, render: (value) => <code>{value}</code> },
    { title: '规模 / 解析', dataIndex: 'scale', width: 250, render: (value, row) => <div className="asset-scale"><span>{value}</span><small>{row.parse_status === 'ready' ? `${row.recommendation_count} 个推荐方法` : row.parse_status === 'error' ? '解析失败，可进入详情诊断' : '打开详情后自动分析'}</small></div> },
    { title: '大小', dataIndex: 'size_label', width: 90 },
    { title: '校验', dataIndex: 'validation_status', width: 100, render: (value) => <Tag color={(statusMeta[value] ?? statusMeta.pending)[0]}>{(statusMeta[value] ?? statusMeta.pending)[1]}</Tag> },
    { title: '来源', dataIndex: 'source', width: 105, render: (value, row) => <div><span>{value === 'gs-fixture' ? 'G-S fixture' : value === 'builtin' ? '内置案例' : '用户上传'}</span>{row.dataset_id ? <small className="cell-note">{row.dataset_id}</small> : null}</div> },
    { title: '操作', width: 158, fixed: 'right', render: (_, row) => <Space size={0}><Button type="link" onClick={() => onOpenDetail(row.id)}>详情</Button><Button type="link" onClick={() => onOpenRecommend(row.id)}>默认预览</Button></Space> }
  ];

  const kindOptions = [...new Set(rows.map((row) => row.kind).filter(Boolean))].sort().map((value) => ({ value, label: KIND_META[value]?.[0] ?? value }));
  const result = uploadResult?.artifact;

  return <div className="page" data-component="Data Assets" data-qoder-id="qel-data-assets-runtime">
    <header className="page-header asset-page-header">
      <div><h1>数据资产</h1><p>上传后自动识别数据家族和数据语义类型，再推荐一种或多种可视化方法；完成参数配置后生成可复用的可视化结果。</p></div>
      <div className="page-header-actions"><ConnectionStatus state={remote.state} updatedAt={remote.updatedAt} onRetry={remote.retry} /><Button type="primary" icon={<CloudUploadOutlined />} onClick={() => setUploadOpen(true)}>上传数据</Button></div>
    </header>

    {remote.error ? <Alert type="warning" showIcon message="资产服务暂时不可用" description="已保留本会话最近快照；服务恢复后可重试。" action={<Button icon={<ReloadOutlined />} onClick={remote.retry}>重试</Button>} /> : null}

    <section className="asset-stat-strip" aria-label="资产统计">
      <Stat label="数据资产总数" value={`${counts.total} 个`} note="SQLite 持久化" trend="up" />
      <Stat label="校验通过" value={`${counts.passed} 个`} note="错误资产保留诊断" trend="up" />
      <Stat label="用户上传" value={`${counts.uploaded} 个`} note="按 SHA-256 去重" />
      <Stat label="G-S 测试资产" value={`${counts.gs} 个`} note="精选可移植数据集" trend="up" />
    </section>

    <section className="panel-surface asset-table-panel">
      <div className="filter-bar">
        <Select value={kindFilter} onChange={setKindFilter} options={[{ value: 'all', label: '全部语义类型' }, ...kindOptions]} />
        <Select value={statusFilter} onChange={setStatusFilter} options={[{ value: 'all', label: '全部校验状态' }, { value: 'passed', label: '通过' }, { value: 'warning', label: '需关注' }, { value: 'error', label: '阻断' }, { value: 'pending', label: '待分析' }]} />
        <Input.Search value={query} onChange={(event) => setQuery(event.target.value)} allowClear placeholder="搜索名称 / 文件名 / ID / 数据集" />
        <span className="filter-count">{filtered.length} / {rows.length} 个资产</span>
      </div>
      <Table rowKey="id" columns={columns} dataSource={filtered} loading={!remote.data && !remote.error} pagination={{ pageSize: 16, showSizeChanger: false }} scroll={{ x: 1220 }} />
    </section>

    <Drawer title="上传并推荐可视化方法" width={520} open={uploadOpen} onClose={() => { setUploadOpen(false); resetUpload(); }} destroyOnClose extra={result ? <Button type="primary" onClick={() => { setUploadOpen(false); onOpenDetail(result.id); }}>打开数据资产</Button> : null}>
      <div className="upload-flow">
        <Alert type="info" showIcon message="无需 Agent" description="系统按文件结构、列角色和数组维度识别数据语义类型，再确定性推荐多个可视化方法；声明值与识别结果会分别保留。" />
        <label className="form-label">声明的数据语义类型（ArtifactKind）</label>
        <Select value={declaredKind} onChange={setDeclaredKind} options={[{ value: 'auto', label: '自动识别（推荐）' }, { value: 'table', label: 'PLT · 表格' }, { value: 'series', label: 'PLT · 序列' }, { value: 'tensor', label: 'PLT · 张量' }, { value: 'raster', label: 'FLD · 栅格场' }, { value: 'field', label: 'FLD · 物理场' }, { value: 'volume', label: 'FLD · 体数据' }, { value: 'trajectory', label: 'ENT · 轨迹' }, { value: 'mesh', label: 'GEO · 几何网格' }]} />
        <Dragger beforeUpload={(next) => { setFile(next); setUploadResult(null); setUploadError(null); return false; }} onRemove={() => setFile(null)} maxCount={1} fileList={file ? [file] : []} accept=".csv,.parquet,.pq,.npz,.json,.vti,.vtu,.vtp,.vts,.vtm,.stl,.ply,.obj,.png,.jpg,.jpeg,.md,.html,.pt">
          <p className="ant-upload-drag-icon"><InboxOutlined /></p><p className="ant-upload-text">拖入数据文件，或点击选择</p><p className="ant-upload-hint">CSV / Parquet / NPZ / JSON / VTK / STL / PLY / OBJ / 图片 / 文档</p>
        </Dragger>
        {uploading ? <div><Progress percent={62} status="active" showInfo={false} /><p className="cell-note">正在保存、解析数据画像并生成推荐…</p></div> : null}
        {uploadError ? <Alert type="error" showIcon message="上传或解析失败" description={uploadError} /> : null}
        {result ? <div className="upload-success"><DatabaseOutlined /><div><strong>{result.name}</strong><span>数据资产 ID {result.id} · 识别为 {result.family} / {KIND_META[result.kind]?.[0] ?? result.kind}（{result.kind}）</span><small>{uploadResult.deduplicated ? '检测到相同内容，已返回持久化数据资产。' : `已生成 ${result.recommendation_count} 个可视化方法选项。`}</small></div></div> : null}
        <Button type="primary" size="large" block disabled={!file || uploading || Boolean(result)} loading={uploading} onClick={submitUpload}>上传、分析并推荐方法</Button>
      </div>
    </Drawer>
  </div>;
}
