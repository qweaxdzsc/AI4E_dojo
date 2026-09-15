/** 可视化工作台页面：组合数据集、参数配置、预览和资产保存。 */

import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Alert, App as AntApp, Button, Collapse, Empty, Input, InputNumber, Result, Select,
  Skeleton, Space, Switch, Tabs, Tag, Tooltip
} from 'antd';
import {
  ArrowLeftOutlined, CheckOutlined, CodeOutlined, EditOutlined, EyeOutlined,
  ReloadOutlined, SaveOutlined, SettingOutlined
} from '@ant-design/icons';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { apiArtifact } from '../../dataAssets/index.js';
import { apiArtifactRecommendations } from '../api.js';
import { apiCreateArtifactVisualization, apiPreviewArtifactVisualization, apiVisualization } from '../../visIO/index.js';
import ExamplePreview from '../components/ExamplePreview.jsx';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

const clone = (value) => JSON.parse(JSON.stringify(value ?? {}));

function pathValue(parameters, field) {
  return parameters?.[field];
}

function FieldError({ error }) {
  return error ? <span className="config-field-error" role="alert">{error.message}</span> : null;
}

function JsonValueInput({ value, onChange, disabled, rows = 3 }) {
  const [text, setText] = useState(() => JSON.stringify(value ?? [], null, 2));
  const [error, setError] = useState('');
  useEffect(() => setText(JSON.stringify(value ?? [], null, 2)), [value]);
  return <div>
    <Input.TextArea value={text} disabled={disabled} autoSize={{ minRows: rows, maxRows: 8 }} onChange={(event) => {
      const next = event.target.value;
      setText(next);
      try { onChange(JSON.parse(next)); setError(''); } catch { setError('请输入合法 JSON'); }
    }} />
    {error ? <span className="config-field-error" role="alert">{error}</span> : null}
  </div>;
}

function SchemaField({ name, schema, value, onChange, error, disabled }) {
  const title = schema.title || name;
  const description = schema.description;
  let control;
  const types = Array.isArray(schema.type) ? schema.type : [schema.type];
  if (schema.enum) {
    control = <Select value={value ?? null} allowClear={!schema.enum.includes(null)} disabled={disabled} onChange={onChange} options={schema.enum.map((item) => ({ value: item, label: item === null ? '自动' : String(item) }))} />;
  } else if (types.includes('boolean')) {
    control = <Switch checked={Boolean(value)} disabled={disabled} checkedChildren="开启" unCheckedChildren="关闭" onChange={onChange} />;
  } else if (types.includes('integer') || types.includes('number')) {
    control = <InputNumber value={value} disabled={disabled} min={schema.minimum} max={schema.maximum} step={schema.multipleOf || (types.includes('integer') ? 1 : 0.1)} onChange={onChange} />;
  } else if (types.includes('array') && schema.items?.enum) {
    control = <Select mode="multiple" value={Array.isArray(value) ? value : []} disabled={disabled} onChange={onChange} options={schema.items.enum.map((item) => ({ value: item, label: item }))} />;
  } else if (types.includes('array') && schema.items?.type === 'number' && schema.minItems === schema.maxItems) {
    const values = Array.isArray(value) ? value : Array.from({ length: schema.minItems }, () => 0);
    control = <Space.Compact block>{values.map((item, index) => <InputNumber aria-label={`${title} ${index + 1}`} key={index} value={item} disabled={disabled} onChange={(next) => onChange(values.map((current, i) => i === index ? next : current))} />)}</Space.Compact>;
  } else if (types.includes('array') || types.includes('object')) {
    control = <JsonValueInput value={value} onChange={onChange} disabled={disabled} />;
  } else if (schema.pattern?.includes('0-9A-Fa-f')) {
    control = <Space.Compact block><input className="config-color-input" aria-label={`${title} 取色器`} type="color" value={value || '#FFFFFF'} disabled={disabled} onChange={(event) => onChange(event.target.value.toUpperCase())} /><Input value={value} disabled={disabled} onChange={(event) => onChange(event.target.value)} /></Space.Compact>;
  } else {
    control = <Input value={value ?? ''} disabled={disabled} maxLength={schema.maxLength} onChange={(event) => onChange(event.target.value)} />;
  }
  return <label className={`config-field ${error ? 'has-error' : ''}`}>
    <span className="config-field-label"><b>{title}</b>{schema.default !== undefined ? <Tooltip title={`默认值：${JSON.stringify(schema.default)}`}><small>默认</small></Tooltip> : null}</span>
    {control}
    {description ? <span className="config-field-description">{description}</span> : null}
    <FieldError error={error} />
  </label>;
}

function StructuredForm({ candidate, parameters, onChange, errors, disabled }) {
  const properties = candidate?.parameter_schema?.properties ?? {};
  const groups = candidate?.ui_schema?.groups ?? [{ id: 'all', label: '参数', fields: Object.keys(properties) }];
  const errorByPath = Object.fromEntries((errors ?? []).map((item) => [item.path, item]));
  return <Collapse className="config-groups" defaultActiveKey={groups.slice(0, 3).map((group) => group.id)} items={groups.map((group) => ({
    key: group.id,
    label: <span>{group.label}<Tag>{group.fields.length}</Tag></span>,
    children: <div className="config-field-grid">{group.fields.map((field) => <SchemaField key={field} name={field} schema={properties[field] ?? { type: 'string' }} value={pathValue(parameters, field)} disabled={disabled} error={errorByPath[`/${field}`]} onChange={(value) => onChange({ ...parameters, [field]: value })} />)}</div>
  }))} />;
}

function AdvancedJson({ parameters, onChange, errors, disabled }) {
  const [text, setText] = useState(() => JSON.stringify(parameters, null, 2));
  const [syntaxError, setSyntaxError] = useState('');
  useEffect(() => setText(JSON.stringify(parameters, null, 2)), [parameters]);
  return <div className="advanced-json-panel">
    <Alert type="info" showIcon message="高级 JSON 使用同一参数 Schema" description="只接受数据参数；JavaScript、Python、HTML 和可执行表达式不会被运行。" />
    <Input.TextArea className="advanced-json-editor" value={text} disabled={disabled} spellCheck={false} autoSize={{ minRows: 22, maxRows: 38 }} onChange={(event) => {
      const next = event.target.value;
      setText(next);
      try { const parsed = JSON.parse(next); setSyntaxError(''); onChange(parsed); } catch (error) { setSyntaxError(error.message); }
    }} />
    {syntaxError ? <Alert type="error" showIcon message="JSON 语法错误" description={syntaxError} /> : null}
    {(errors ?? []).length ? <ul className="config-error-list" aria-label="参数错误">{errors.map((item) => <li key={`${item.path}-${item.message}`}><code>{item.path}</code>{item.message}{item.legal ? `；合法值 ${JSON.stringify(item.legal)}` : ''}</li>)}</ul> : null}
  </div>;
}

export default function VisualizationConfiguratorPage() {
  const { artifactId, recommendationId, visualizationId } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { message } = AntApp.useApp();
  const isEditingExisting = Boolean(visualizationId && location.pathname.endsWith('/edit'));
  const readOnly = Boolean(visualizationId && !isEditingExisting);
  const embedded = readOnly && new URLSearchParams(location.search).get('embed') === '1';
  const [loading, setLoading] = useState(true);
  const [artifact, setArtifact] = useState(null);
  const [candidate, setCandidate] = useState(null);
  const [record, setRecord] = useState(null);
  const [parameters, setParameters] = useState({});
  const [preview, setPreview] = useState(null);
  const [previewState, setPreviewState] = useState('idle');
  const [errors, setErrors] = useState([]);
  const [mode, setMode] = useState('form');
  const [saving, setSaving] = useState(false);
  const requestRef = useRef(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      if (visualizationId) {
        const stored = await apiVisualization(visualizationId);
        const [asset, recommendations] = await Promise.all([apiArtifact(stored.artifact_id), apiArtifactRecommendations(stored.artifact_id)]);
        const candidates = recommendations.detected_candidates ?? recommendations.candidates ?? [];
        const selected = candidates.find((item) => item.recommendation_id === stored.recommendation_id);
        setRecord(stored); setArtifact(asset); setCandidate(selected); setParameters(clone(stored.parameters)); setPreview(stored.payload);
      } else {
        const [asset, recommendations] = await Promise.all([apiArtifact(artifactId), apiArtifactRecommendations(artifactId)]);
        const candidates = recommendations.detected_candidates ?? recommendations.candidates ?? [];
        const selected = candidates.find((item) => item.recommendation_id === recommendationId);
        if (!selected) throw Object.assign(new Error('推荐的可视化方法不存在或已失效'), { status: 404 });
        setArtifact(asset); setCandidate(selected); setParameters(clone(selected.default_parameters));
      }
    } catch (error) {
      message.error(error.message);
      setCandidate(null);
    } finally { setLoading(false); }
  }, [artifactId, message, recommendationId, visualizationId]);

  useEffect(() => { load(); }, [load]);

  useEffect(() => {
    if (loading || readOnly || !candidate || !artifact) return undefined;
    const timer = setTimeout(async () => {
      requestRef.current?.abort();
      const controller = new AbortController();
      requestRef.current = controller;
      setPreviewState('loading'); setErrors([]);
      try {
        const result = await apiPreviewArtifactVisualization(artifact.id, { recommendation_id: candidate.recommendation_id, parameters }, controller.signal);
        setParameters((current) => JSON.stringify(current) === JSON.stringify(result.normalized_parameters) ? current : result.normalized_parameters);
        setPreview(result.preview); setPreviewState('live');
      } catch (error) {
        if (controller.signal.aborted) return;
        setErrors(error.detail?.errors ?? [{ path: '/', message: error.message, legal: error.detail?.legal }]);
        setPreviewState('error');
      }
    }, 300);
    return () => { clearTimeout(timer); requestRef.current?.abort(); };
  }, [artifact, candidate, loading, parameters, readOnly]);

  const save = async () => {
    if (!candidate || errors.length) return;
    setSaving(true);
    try {
      const saved = await apiCreateArtifactVisualization(artifact.id, {
        recommendation_id: candidate.recommendation_id,
        parameters,
        ...(isEditingExisting ? { base_spec_id: record.spec_id, base_version: record.spec_version } : {})
      });
      message.success(isEditingExisting ? `已保存新配置版本 ${saved.spec_id} v${saved.spec_version}` : '可视化配置已保存');
      navigate(`/visualizations/${saved.visualization_id}`);
    } catch (error) {
      if (error.status === 409) message.error(`保存冲突：服务器已有较新版本（期望 v${error.detail?.expected ?? '?'}）`);
      else message.error(error.message);
    } finally { setSaving(false); }
  };

  if (loading) return <div className="workspace-page"><Skeleton active paragraph={{ rows: 14 }} /></div>;
  if (!candidate || !artifact) {
    const missingTitle = readOnly ? '可视化结果不存在' : isEditingExisting ? '可视化结果或其配置不存在' : '推荐的可视化方法不存在';
    return <Result status="404" title={missingTitle} extra={<Link to="/"><Button type="primary">返回数据资产</Button></Link>} />;
  }
  if (embedded) return <div className="visualization-embed-view"><ExamplePreview visualizationId={visualizationId} payload={preview} embedded /></div>;

  const title = readOnly ? `可视化结果 · ${artifact.name}` : isEditingExisting ? `编辑配置 · ${artifact.name}` : `配置方法 · ${artifact.name}`;
  const backTo = readOnly ? `/assets/${artifact.id}` : isEditingExisting ? `/visualizations/${visualizationId}` : `/assets/${artifact.id}`;
  return <div className="workspace-page visualization-configurator">
    <PageTitle title={title} description={`${candidate.task_label} · ${candidate.function_id}`} actions={<>
      <Link to={backTo}><Button icon={<ArrowLeftOutlined />}>返回</Button></Link>
      {readOnly ? <Link to={`/visualizations/${visualizationId}/edit`}><Button type="primary" icon={<EditOutlined />}>基于此配置创建新版本</Button></Link> : <Button type="primary" icon={<SaveOutlined />} loading={saving} disabled={errors.length > 0 || previewState !== 'live'} onClick={save}>保存可视化配置</Button>}
    </>} />
    <div className="config-provenance-bar">
      <span><b>{candidate.renderer_label}</b><small>渲染器归属</small></span>
      <span><b>{candidate.schema_revision}</b><small>参数定义版本</small></span>
      <span><b>{record ? `${record.spec_id} v${record.spec_version}` : '尚未保存'}</b><small>可视化配置（Spec）</small></span>
      <span><b>{record?.visualization_id ?? '尚未生成'}</b><small>可视化结果（Visualization）</small></span>
      <Tag color={previewState === 'error' ? 'error' : previewState === 'loading' ? 'processing' : 'success'}>{readOnly ? '已保存结果' : previewState === 'loading' ? '正在生成预览' : previewState === 'error' ? '参数有误' : '实时预览（未保存）'}</Tag>
    </div>
    <div className="configurator-layout">
      <aside className="configurator-controls" aria-label="可视化参数配置">
        <div className="configurator-toolbar">
          <Tabs activeKey={mode} onChange={setMode} items={[{ key: 'form', label: <span><SettingOutlined /> 结构化</span> }, { key: 'json', label: <span><CodeOutlined /> 高级 JSON</span> }]} />
          {!readOnly ? <Button icon={<ReloadOutlined />} onClick={() => { setParameters(clone(candidate.default_parameters)); setErrors([]); }}>恢复默认</Button> : null}
        </div>
        {mode === 'form' ? <StructuredForm candidate={candidate} parameters={parameters} onChange={setParameters} errors={errors} disabled={readOnly} /> : <AdvancedJson parameters={parameters} onChange={setParameters} errors={errors} disabled={readOnly} />}
      </aside>
      <main className="configurator-preview" aria-label="可视化实时预览">
        <div className="preview-heading"><div><h2><EyeOutlined /> {readOnly ? '已保存的可视化结果' : '实时预览（未保存）'}</h2><p>{readOnly ? '该结果引用已冻结的可视化配置；编辑时会创建新配置版本和新结果。' : '参数合法后 300ms 防抖生成；保存前不会创建可视化配置或结果。'}</p></div>{previewState === 'live' ? <Tag icon={<CheckOutlined />} color="success">参数已校验</Tag> : null}</div>
        {errors.length ? <Alert type="error" showIcon message="参数校验未通过" description={<ul className="config-error-list">{errors.map((item) => <li key={`${item.path}-${item.message}`}><code>{item.path}</code>{item.message}</li>)}</ul>} /> : null}
        {preview ? <ExamplePreview artifactId={artifact.id} recommendationId={candidate.recommendation_id} visualizationId={readOnly ? visualizationId : undefined} payload={preview} embedded /> : <Empty description="等待真实预览" />}
        <div className="preview-audit"><b>追溯</b><span>数据资产 ID <code>{artifact.id}</code></span><span>可视化方法 ID <code>{candidate.function_id}</code></span><span>可视化配置 ID / 版本 <code>{record ? `${record.spec_id} / v${record.spec_version}` : '尚未保存'}</code></span><span>可视化结果 ID <code>{readOnly ? visualizationId : '尚未生成'}</code></span><span>渲染器 <code>{candidate.renderer}</code></span></div>
      </main>
    </div>
  </div>;
}
