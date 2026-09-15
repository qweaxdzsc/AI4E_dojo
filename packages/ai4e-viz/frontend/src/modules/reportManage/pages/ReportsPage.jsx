/** 报告中心页面：组织查询、创建、复制和进入编排。 */

import { useCallback, useMemo, useState } from 'react';
import { Alert, App as AntApp, Button, Form, Input, Modal, Select, Space, Table, Tag } from 'antd';
import { EditOutlined, EyeOutlined, PlusOutlined } from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { apiCreateReport, apiDuplicateReport, apiReports } from '../api.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import { fallbackReports } from '../fallback.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

const statusMeta = {
  succeeded: ['success', '完整'], partial: ['warning', '部分完成'], failed: ['error', '失败诊断'], draft: ['processing', '草稿']
};
const reportsFallback = { items: fallbackReports, updated_at: '2026-08-23T00:00:00+08:00' };

export default function ReportsPage() {
  const navigate = useNavigate();
  const { message } = AntApp.useApp();
  const [form] = Form.useForm();
  const loader = useCallback(() => apiReports(), []);
  const remote = useRemoteSnapshot('reports-v2', loader, reportsFallback);
  const [status, setStatus] = useState('ALL');
  const [query, setQuery] = useState('');
  const [creating, setCreating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const rows = useMemo(() => (remote.data?.items ?? fallbackReports).filter((item) => (status === 'ALL' || item.status === status) && (!query || `${item.title}${item.id}${item.author}`.toLowerCase().includes(query.toLowerCase()))), [query, remote.data, status]);
  const counts = Object.fromEntries(['succeeded', 'partial', 'failed'].map((key) => [key, rows.filter((item) => item.status === key).length]));
  const duplicate = async (reportId) => {
    try { const copy = await apiDuplicateReport(reportId); message.success('已创建可编辑副本'); navigate(`/reports/${copy.report_id}/edit`); }
    catch (error) { message.error(error.message); }
  };
  const columns = [
    { title: '报告', dataIndex: 'title', render: (value, row) => <div><Link className="report-link" to={`/reports/${row.id}`}>{value}</Link><div className="cell-note"><code>{row.id}</code> · {row.status_note}</div></div> },
    { title: '状态', dataIndex: 'status', width: 120, render: (value) => <Tag color={(statusMeta[value] ?? statusMeta.draft)[0]}>{(statusMeta[value] ?? statusMeta.draft)[1]}</Tag> },
    { title: '生成时间', dataIndex: 'generated_at', width: 150 },
    { title: '作者', dataIndex: 'author', width: 100 },
    { title: '产物', dataIndex: 'formats', width: 150, render: (items) => items.length ? items.map((item) => <Tag key={item}>{item}</Tag>) : <span className="cell-note">未生成</span> },
    { title: '', width: 190, render: (_, row) => row.editable ? <Link to={`/reports/${row.id}/edit`}><Button type="link" icon={<EditOutlined />}>编排</Button></Link> : <Space.Compact><Link to={`/reports/${row.id}`}><Button type="link" icon={<EyeOutlined />}>阅读</Button></Link><Button type="link" icon={<EditOutlined />} onClick={() => duplicate(row.id)}>复制编排</Button></Space.Compact> }
  ];
  const create = async () => {
    try {
      const values = await form.validateFields();
      setSubmitting(true);
      const report = await apiCreateReport({ ...values, key_questions: values.key_questions ? values.key_questions.split(/\n+/).map((item) => item.trim()).filter(Boolean) : [], dataset_ids: values.dataset_ids ?? [] });
      setCreating(false); form.resetFields(); message.success('报告脚手架已创建'); navigate(`/reports/${report.report_id}/edit`);
    } catch (error) { if (error?.errorFields) return; message.error(error.message); }
    finally { setSubmitting(false); }
  };
  return <div className="workspace-page reports-page"><PageTitle title="报告中心" description="阅读已冻结报告，或用 12 列文档网格编排新的 Quarto 报告。" meta={<ConnectionStatus state={remote.state} updatedAt={remote.updatedAt} onRetry={remote.retry} />} actions={<Button type="primary" icon={<PlusOutlined />} onClick={() => setCreating(true)}>新建报告</Button>} />
    <div className="report-summary-strip"><div><strong>{rows.length}</strong><span>报告数量</span></div><div><strong>{counts.succeeded ?? 0}</strong><span>完整</span></div><div><strong>{counts.partial ?? 0}</strong><span>部分完成</span></div><div><strong>{counts.failed ?? 0}</strong><span>失败诊断</span></div></div>
    <section className="panel-surface"><div className="filter-bar"><Select value={status} onChange={setStatus} options={[{ value: 'ALL', label: '全部状态' }, { value: 'draft', label: '草稿' }, { value: 'succeeded', label: '完整' }, { value: 'partial', label: '部分完成' }, { value: 'failed', label: '失败诊断' }]} /><Input.Search value={query} onChange={(event) => setQuery(event.target.value)} allowClear placeholder="搜索报告标题、ID 或作者" /></div><Table rowKey="id" columns={columns} dataSource={rows} pagination={false} scroll={{ x: 820 }} /></section>
    <Modal title="新建报告" open={creating} width={680} okText="创建并开始编排" cancelText="取消" confirmLoading={submitting} onOk={create} onCancel={() => setCreating(false)}>
      <Form form={form} layout="vertical" initialValues={{ author: '原力', template: 'analysis', audience: '项目团队', page_size: 'A4', orientation: 'portrait' }}>
        <Form.Item name="title" label="报告标题" rules={[{ required: true, message: '请输入报告标题' }]}><Input /></Form.Item>
        <Space.Compact block><Form.Item name="author" label="作者" style={{ flex: 1 }}><Input /></Form.Item><Form.Item name="audience" label="目标读者" style={{ flex: 1 }} rules={[{ required: true, message: '请输入目标读者' }]}><Input /></Form.Item></Space.Compact>
        <Form.Item name="goal" label="项目目标" rules={[{ required: true, message: '请输入项目目标' }]}><Input.TextArea autoSize={{ minRows: 3, maxRows: 6 }} /></Form.Item>
        <Form.Item name="key_questions" label="关键问题（每行一个）"><Input.TextArea autoSize={{ minRows: 3, maxRows: 8 }} /></Form.Item>
        <Space.Compact block><Form.Item name="template" label="模板" style={{ flex: 1 }} rules={[{ required: true }]}><Select options={[{ value: 'analysis', label: '分析报告' }, { value: 'validation', label: '实验验证' }, { value: 'weekly', label: '项目周报' }, { value: 'blank', label: '空白报告' }]} /></Form.Item><Form.Item name="page_size" label="页面规格" style={{ width: 140 }}><Select options={['A4', 'Letter'].map((value) => ({ value, label: value }))} /></Form.Item><Form.Item name="orientation" label="方向" style={{ width: 140 }}><Select options={[{ value: 'portrait', label: '纵向' }, { value: 'landscape', label: '横向' }]} /></Form.Item></Space.Compact>
        <Form.Item name="dataset_ids" label="关联数据集"><Select mode="tags" tokenSeparators={[',']} placeholder="输入数据集 ID 后回车" /></Form.Item>
        <Alert type="info" showIcon message="系统只生成结构，不自动写结论" description="执行摘要、证据、讨论和来源会以待补充提示创建；需要由用户加入已保存的可视化结果和可追溯文字。" />
      </Form>
    </Modal>
  </div>;
}
