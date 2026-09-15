/** VisualizationSpec页面：组织方法参数、版本和乐观锁保存。 */

import { useCallback, useEffect, useMemo, useState } from 'react';
import { Alert, App as AntApp, Button, Drawer, Form, Input, Select, Table, Tag } from 'antd';
import { HistoryOutlined, PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import {
  apiAppendVisualizationSpec, apiCreateVisualizationSpec, apiSpecs,
  apiVisualizationSpecVersion, apiVisualizationSpecVersions
} from '../api.js';
import { terminologyLabel } from '../terminology.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import { fallbackSpecs } from '../fallback.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

const blank = { spec_id: '', version: null, artifact_id: 'CASE-SCALAR-NUMBER', function_id: 'core.scalar-number@2.0.0', kind: 'scalar', params: {} };

export default function SpecsPage() {
  const { message } = AntApp.useApp();
  const { specId, version } = useParams();
  const navigate = useNavigate();
  const remote = useRemoteSnapshot('functions-v2', useCallback(() => apiSpecs(), []), fallbackSpecs);
  const registry = remote.data?.functions?.length === 23 ? remote.data : fallbackSpecs;
  const [family, setFamily] = useState('ALL');
  const [query, setQuery] = useState('');
  const [form, setForm] = useState(blank);
  const [paramsText, setParamsText] = useState('{}');
  const [errors, setErrors] = useState({});
  const [saving, setSaving] = useState(false);
  const [conflict, setConflict] = useState(null);
  const [history, setHistory] = useState(null);
  const [loadingVersion, setLoadingVersion] = useState(false);

  useEffect(() => {
    if (!specId || !version) return;
    let active = true;
    setLoadingVersion(true);
    apiVisualizationSpecVersion(specId, version)
      .then((item) => {
        if (!active) return;
        setForm(item);
        setParamsText(JSON.stringify(item.params, null, 2));
        setConflict(null);
      })
      .catch((error) => active && setConflict({ code: 'LOAD_FAILED', message: error.message }))
      .finally(() => active && setLoadingVersion(false));
    return () => { active = false; };
  }, [specId, version]);

  const functions = useMemo(() => registry.functions.filter((item) => {
    if (family !== 'ALL' && item.family !== family) return false;
    return !query || `${item.id}${item.label}${item.renderer}${item.compatible_kinds.join(' ')}${item.accepted_formats.join(' ')}`.toLowerCase().includes(query.toLowerCase());
  }), [family, query, registry.functions]);

  const kinds = registry.kinds ?? fallbackSpecs.kinds;
  const compatibleFunctions = registry.functions.filter((item) => item.compatible_kinds.includes(form.kind));
  const activeFunction = registry.functions.find((item) => item.id === form.function_id) ?? compatibleFunctions[0];

  const loadFunctionDefaults = (item, { resetRoute = true } = {}) => {
    const kind = item.compatible_kinds[0];
    setForm({ ...blank, artifact_id: item.example_id, function_id: item.id, kind, params: item.default_parameters });
    setParamsText(JSON.stringify(item.default_parameters, null, 2));
    setErrors({});
    setConflict(null);
    if (resetRoute) navigate('/specs');
  };

  const changeKind = (kind) => {
    const next = registry.functions.find((item) => item.compatible_kinds.includes(kind));
    if (next) loadFunctionDefaults(next);
  };

  const changeFunction = (functionId) => {
    const next = registry.functions.find((item) => item.id === functionId);
    if (next) loadFunctionDefaults(next);
  };

  const validate = () => {
    const next = {};
    let params = {};
    try { params = JSON.parse(paramsText); } catch (error) { next.params = `JSON 解析失败：${error.message}`; }
    if (!form.artifact_id.trim()) next.artifact_id = '数据资产 ID 不能为空';
    if (!compatibleFunctions.some((item) => item.id === form.function_id)) next.function_id = '可视化方法与当前语义类型不兼容';
    setErrors(next);
    return Object.keys(next).length ? null : { ...form, params };
  };

  const save = async () => {
    const payload = validate();
    if (!payload) return;
    setSaving(true);
    setConflict(null);
    try {
      const saved = form.spec_id
        ? await apiAppendVisualizationSpec(form.spec_id, { ...payload, base_version: form.version })
        : await apiCreateVisualizationSpec(payload);
      message.success(`已保存 ${saved.spec_id} v${saved.version}`);
      navigate(`/specs/${saved.spec_id}/v/${saved.version}`);
    } catch (error) {
      setConflict(error.detail ?? { code: 'SAVE_FAILED', message: error.message });
    } finally { setSaving(false); }
  };

  const openHistory = async () => {
    if (!form.spec_id) return;
    try { setHistory((await apiVisualizationSpecVersions(form.spec_id)).items); }
    catch (error) { message.error(error.message); }
  };

  const columns = [
    { title: '可视化方法', minWidth: 280, render: (_, row) => <button className="function-link method-name-cell" onClick={() => loadFunctionDefaults(row)}><strong>{row.label}</strong><code>{row.id}</code><span>{row.description}</span></button> },
    { title: '数据语义类型', width: 150, render: (_, row) => { const kind = kinds.find((candidate) => candidate.id === row.compatible_kinds[0]); return <Tag>{kind?.label ?? row.compatible_kinds[0]}</Tag>; } },
    { title: '可接受数据格式', width: 260, render: (_, row) => <div className="format-tags">{row.accepted_formats.map((format) => <Tag key={format}>{format}</Tag>)}</div> },
    { title: '渲染器', dataIndex: 'renderer', width: 150 },
    { title: '交互 / 静态 / 离线', width: 165, render: (_, row) => `${row.capabilities.interactive ? '✓' : '—'} / ${row.capabilities.static ? '✓' : '—'} / ${row.capabilities.offline ? '✓' : '—'}` }
  ];

  return (
    <div className="workspace-page specs-page">
      <PageTitle title="可视化方法与配置" description="选择方法即可载入其默认配置；同一种数据语义类型可以有多种方法。" meta={<ConnectionStatus state={remote.state} updatedAt={remote.updatedAt} onRetry={remote.retry} />} actions={<Button icon={<PlusOutlined />} onClick={() => loadFunctionDefaults(registry.functions[0])}>新建可视化配置</Button>} />
      <div className="spec-grid">
        <section className="spec-registry panel-surface">
          <div className="panel-heading"><div><h2>{terminologyLabel('method')}目录</h2><p>{registry.counts.functions} 个方法 · 19 种数据语义类型 · 点击方法载入默认配置</p></div></div>
          <div className="filter-bar"><Select value={family} onChange={setFamily} options={[{ value: 'ALL', label: '全部数据家族' }, ...registry.families.map((item) => ({ value: item.id, label: `${item.id} · ${item.label}` }))]} /><Input.Search allowClear value={query} onChange={(event) => setQuery(event.target.value)} placeholder="搜索方法、格式、数据语义类型或渲染器" /></div>
          <Table rowKey="id" columns={columns} dataSource={functions} size="small" pagination={{ pageSize: 8, showSizeChanger: false }} scroll={{ x: 1020 }} />
        </section>

        <section className="spec-editor panel-surface" aria-busy={loadingVersion}>
          <div className="panel-heading"><div><h2>{form.spec_id ? `${form.spec_id} · v${form.version}` : terminologyLabel('spec')}</h2><p>可视化配置 = 数据资产 + 可视化方法 + 参数；保存后形成不可变版本。</p></div>{form.spec_id ? <Button icon={<HistoryOutlined />} onClick={openHistory}>配置历史</Button> : null}</div>
          {conflict ? <Alert type={conflict.code === 'STALE_BASE_VERSION' ? 'warning' : 'error'} showIcon message={conflict.code === 'STALE_BASE_VERSION' ? '版本冲突：服务器已有更新版本' : '无法保存可视化配置'} description={conflict.message || (conflict.expected ? `当前最新版本 v${conflict.expected}，你正在基于 v${conflict.received} 保存。` : JSON.stringify(conflict))} /> : null}
          <Form layout="vertical" className="spec-form">
            <div className="form-row"><Form.Item label="数据资产 ID" extra="当前方法的配套案例已自动填入；可替换为兼容的真实数据资产。" validateStatus={errors.artifact_id ? 'error' : ''} help={errors.artifact_id}><Input value={form.artifact_id} onChange={(event) => setForm((current) => ({ ...current, artifact_id: event.target.value }))} /></Form.Item><Form.Item label="数据语义类型（ArtifactKind）"><Select value={form.kind} onChange={changeKind} options={kinds.map((item) => ({ value: item.id, label: `${item.family} · ${item.label}（${item.id}）` }))} /></Form.Item></div>
            <Form.Item label="可视化方法" extra={`${activeFunction?.description ?? ''} 可接受：${activeFunction?.accepted_formats.join('、') ?? '—'}`} validateStatus={errors.function_id ? 'error' : ''} help={errors.function_id}><Select value={form.function_id} onChange={changeFunction} options={compatibleFunctions.map((item) => ({ value: item.id, label: `${item.label} · ${item.renderer}` }))} /></Form.Item>
            <Form.Item label="配置参数 JSON" extra="点击左侧任一方法会载入该方法的具体默认值。" validateStatus={errors.params ? 'error' : ''} help={errors.params}><Input.TextArea className="code-editor" rows={15} value={paramsText} onChange={(event) => setParamsText(event.target.value)} spellCheck={false} /></Form.Item>
          </Form>
          <div className="editor-actions"><Button disabled>报告仅接收已保存的可视化结果</Button><Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={save}>保存{form.spec_id ? '配置新版本' : '可视化配置'}</Button></div>
        </section>
      </div>
      <Drawer title={`${form.spec_id} 配置历史版本`} open={Boolean(history)} onClose={() => setHistory(null)} width={480}>{history?.map((item) => <button className="history-row" key={item.version} onClick={() => { setHistory(null); navigate(`/specs/${item.spec_id}/v/${item.version}`); }}><strong>v{item.version}</strong><span>{item.function_id}</span><small>{new Date(item.created_at).toLocaleString('zh-CN')}</small></button>)}</Drawer>
    </div>
  );
}
