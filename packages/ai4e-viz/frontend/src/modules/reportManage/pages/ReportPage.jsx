/** 报告详情页面：组合冻结版本、可视化引用和导出。 */

import { useCallback, useEffect, useState } from 'react';
import { Alert, App as AntApp, Button, Dropdown, Modal, Result, Table, Tag } from 'antd';
import { ArrowLeftOutlined, CopyOutlined, DownloadOutlined, EditOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart, HeatmapChart, LineChart } from 'echarts/charts';
import { AriaComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent, VisualMapComponent } from 'echarts/components';
import { SVGRenderer } from 'echarts/renderers';
import { Link, useParams, useSearchParams } from 'react-router-dom';
import { apiCreateReportExport, apiReport, apiReportExport, apiReportSnapshot, reportExportDownloadUrl } from '../api.js';
import useRemoteSnapshot from '../../../infrastructure/hooks/useRemoteSnapshot.js';
import ConnectionStatus from '../../../infrastructure/components/ConnectionStatus.jsx';
import { ExamplePreview } from '../../visTaskManage/index.js';
import PageTitle from '../../../infrastructure/components/PageTitle.jsx';

const stableRowKey = (row) => row.id ?? row.key ?? JSON.stringify(row);
const reportPalette = ['#1677ff', '#0e9f9f', '#8250df', '#d97706', '#dc2626', '#18934e', '#5b6b7f', '#c2418c'];

echarts.use([BarChart, HeatmapChart, LineChart, AriaComponent, GridComponent, LegendComponent, TitleComponent, TooltipComponent, VisualMapComponent, SVGRenderer]);

function ReportDownload({ reportId }) {
  const { message } = AntApp.useApp();
  const [task, setTask] = useState(null);
  const create = async (format) => {
    try {
      setTask(await apiCreateReportExport(reportId, { format, mode: format === 'html' ? 'portable' : 'static' }));
    } catch (error) {
      message.error(error.detail?.message || error.detail?.code || error.message);
    }
  };
  useEffect(() => {
    if (!task || !['queued', 'running'].includes(task.status)) return undefined;
    const timer = setInterval(async () => {
      try { setTask(await apiReportExport(task.export_id)); } catch { /* keep last visible stage */ }
    }, 900);
    return () => clearInterval(timer);
  }, [task]);
  const items = [
    { key: 'html', label: '下载当前报告 HTML', onClick: () => create('html') },
    { key: 'pdf', label: '下载当前报告 PDF', onClick: () => create('pdf') },
  ];
  return <>
    <Dropdown menu={{ items }}><Button icon={<DownloadOutlined />}>下载当前报告</Button></Dropdown>
    <Modal open={Boolean(task)} title="生成当前报告" footer={null} onCancel={() => setTask(null)}>
      {task ? <div className="export-task-status">
        <Tag color={task.status === 'succeeded' ? 'success' : task.status === 'failed' ? 'error' : 'processing'}>{task.status}</Tag>
        <p>阶段：<code>{task.stage}</code></p>
        {task.error ? <Alert type="error" showIcon message={task.error.code} description={task.error.message} /> : null}
        {task.status === 'failed' ? <Button onClick={() => create(task.format)}>重新生成</Button> : null}
        {task.status === 'succeeded' ? <a href={reportExportDownloadUrl(task.export_id)} download><Button type="primary" icon={<DownloadOutlined />}>下载 {String(task.format).toUpperCase()}</Button></a> : null}
      </div> : null}
    </Modal>
  </>;
}

function ReportChart({ option, label, height = 360 }) {
  return <div className="report-chart" role="img" aria-label={label}><ReactEChartsCore echarts={echarts} option={option} opts={{ renderer: 'svg' }} style={{ height }} /></div>;
}

function TrainingCurves({ block }) {
  const option = {
    animation: false,
    aria: { enabled: true, description: `${block.title}。八条曲线比较 epoch 与验证损失，纵轴为对数尺度。` },
    color: reportPalette,
    grid: { left: 64, right: 112, top: 52, bottom: 52 },
    legend: { type: 'scroll', top: 0, left: 0, right: 0 },
    tooltip: { trigger: 'axis', valueFormatter: (value) => Number(value).toExponential(3) },
    xAxis: { type: 'value', name: block.x_label, nameLocation: 'middle', nameGap: 31 },
    yAxis: { type: 'log', name: block.y_label, nameLocation: 'middle', nameGap: 48, minorSplitLine: { show: true } },
    series: block.series.map((item) => ({
      name: item.name, type: 'line', showSymbol: false, data: item.x.map((x, index) => [x, item.values[index]]),
      endLabel: { show: true, formatter: item.name, fontSize: 10 }, labelLayout: { moveOverlap: 'shiftY' }, emphasis: { focus: 'series' }
    }))
  };
  return <ReportChart option={option} label={block.title} height={390} />;
}

function GeometryErrors({ block }) {
  const ordered = [...block.items].sort((a, b) => a.value - b.value);
  const option = {
    animation: false,
    aria: { enabled: true, description: `${block.title}。条形越短表示误差越小。` },
    grid: { left: 90, right: 76, top: 12, bottom: 45 },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, valueFormatter: (value) => Number(value).toFixed(3) },
    xAxis: { type: 'value', name: block.y_label, nameLocation: 'middle', nameGap: 30 },
    yAxis: { type: 'category', data: ordered.map((item) => item.name), axisLabel: { interval: 0 } },
    series: [{ type: 'bar', data: ordered.map((item, index) => ({ value: item.value, itemStyle: { color: index === 0 ? reportPalette[1] : reportPalette[0] } })), label: { show: true, position: 'right', formatter: ({ value }) => Number(value).toFixed(3) } }]
  };
  return <ReportChart option={option} label={block.title} height={370} />;
}

function DiagnosticsChart({ block }) {
  const option = {
    animation: false,
    aria: { enabled: true, description: `${block.title}。比较场能量、增长率、频率、CFL、Wφ 和 Qi 随时间的变化。` },
    color: reportPalette,
    grid: { left: 60, right: 68, top: 58, bottom: 50 },
    legend: { type: 'scroll', top: 0, left: 0, right: 0 },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', name: block.x_label, nameLocation: 'middle', nameGap: 32, data: block.x, axisLabel: { interval: Math.max(0, Math.floor(block.x.length / 8) - 1) } },
    yAxis: [
      { type: 'value', name: '归一化/诊断值', min: 0 },
      { type: 'value', name: 'Wφ', min: 0, splitLine: { show: false } }
    ],
    series: block.series.map((item) => ({
      name: item.name, type: 'line', showSymbol: false, data: item.values,
      yAxisIndex: item.name === 'Wφ' ? 1 : 0, lineStyle: { width: 2 }, emphasis: { focus: 'series' }
    }))
  };
  return <ReportChart option={option} label={block.title} height={380} />;
}

function SpectrumHeatmap({ block }) {
  const data = [];
  block.values.forEach((row, timeIndex) => row.forEach((value, kyIndex) => data.push([timeIndex, kyIndex, value])));
  const option = {
    animation: false,
    aria: { enabled: true, description: `${block.title}。横轴为时间，纵轴为归一化 k_y，颜色越亮表示谱强度越高，白线为主峰位置。` },
    grid: { left: 62, right: 86, top: 18, bottom: 58 },
    tooltip: { formatter: ({ data: point }) => `t ${block.times[point[0]]}<br/>k_y ${block.ky[point[1]]}<br/>强度 ${Number(point[2]).toFixed(4)}` },
    xAxis: { type: 'category', name: 't (R/vti)', nameLocation: 'middle', nameGap: 36, data: block.times, axisLabel: { interval: Math.max(0, Math.floor(block.times.length / 8) - 1) } },
    yAxis: { type: 'category', name: 'k_yρ_s', data: block.ky, axisLabel: { interval: 7 } },
    visualMap: { min: 0, max: 1, orient: 'vertical', right: 4, top: 'middle', calculable: false, text: ['高', '低'], inRange: { color: ['#071b3d', '#1677ff', '#0e9f9f', '#f4d35e', '#f15b40'] } },
    series: [
      { name: '谱强度', type: 'heatmap', data, progressive: 4000, emphasis: { itemStyle: { borderColor: '#fff', borderWidth: 1 } } },
      { name: '主峰', type: 'line', data: block.peak.map((value, index) => [index, block.ky.indexOf(value)]), showSymbol: false, lineStyle: { color: '#fff', width: 2 }, z: 3, tooltip: { show: false } }
    ]
  };
  return <ReportChart option={option} label={block.title} height={420} />;
}

function FieldFrames({ block }) {
  return <div className="miller-frame-grid">{block.items.map((item) => {
    const data = [];
    item.values.forEach((row, rowIndex) => row.forEach((value, colIndex) => data.push([colIndex, rowIndex, value])));
    const option = {
      animation: false,
      aria: { enabled: true, description: `${item.label}帧，帧 ${item.frame}，时间 ${item.time}，${block.unit}范围 ${item.range[0]} 到 ${item.range[1]}。` },
      title: { text: `${item.label} · 帧 ${item.frame}`, subtext: `t=${item.time} · ${item.range[0]} … ${item.range[1]}`, left: 8, top: 2, textStyle: { fontSize: 13 }, subtextStyle: { fontSize: 10 } },
      grid: { left: 8, right: 48, top: 52, bottom: 8 },
      tooltip: { formatter: ({ data: point }) => `${block.field}<br/>网格 [${point[1]}, ${point[0]}]<br/>${Number(point[2]).toFixed(5)}` },
      xAxis: { type: 'category', show: false }, yAxis: { type: 'category', show: false, inverse: true },
      visualMap: { min: item.range[0], max: item.range[1], right: 2, top: 60, bottom: 12, itemWidth: 8, text: ['', ''], inRange: { color: ['#15489b', '#58a7d8', '#f5f5f0', '#e97742', '#9e1b32'] } },
      series: [{ type: 'heatmap', data, progressive: 3000 }]
    };
    return <ReportChart key={item.frame} option={option} label={`${block.title}·${item.label}`} height={280} />;
  })}</div>;
}

function Metrics({ items }) {
  return <div className="report-metrics">{items.map((item) => <div key={item.label} data-state={item.state}><span>{item.label}</span><strong>{item.value}<small>{item.unit}</small></strong></div>)}</div>;
}

function Diagnostic({ report }) {
  const diagnostic = report.diagnostic;
  return <div className="diagnostic-grid"><div><span>失败阶段</span><strong>{diagnostic.stage}</strong></div><div><span>错误码</span><strong>{diagnostic.error_codes.join(' · ')}</strong></div><section><h3>缺失引用</h3><ul>{diagnostic.missing_refs.map((item) => <li key={item}>{item}</li>)}</ul></section><section><h3>恢复建议</h3><ol>{diagnostic.recovery.map((item) => <li key={item}>{item}</li>)}</ol></section><pre>{diagnostic.logs.join('\n')}</pre></div>;
}

function ReportBlock({ block, report }) {
  if (block.type === 'metrics') return <section className="report-block"><h3>{block.title}</h3><Metrics items={block.items} /></section>;
  if (block.type === 'markdown') return <section className="report-block markdown-evidence"><h3>{block.title}</h3><ReactMarkdown>{block.body}</ReactMarkdown></section>;
  if (block.type === 'example') return <section className="report-block"><h3>{block.title}</h3><p>{block.caption}</p><ExamplePreview artifactId={block.artifact_id} embedded /></section>;
  if (block.type === 'table') return <section className="report-block"><h3>{block.title}</h3><Table size="small" rowKey={stableRowKey} columns={block.columns.map((title, index) => ({ title, dataIndex: index, key: title }))} dataSource={block.rows} pagination={false} scroll={{ x: 620 }} /></section>;
  if (block.type === 'error') return <Alert className="report-block" type="error" showIcon message={`${block.title} · ${block.code}`} description={<div><p>{block.message}</p><strong>恢复方法：</strong>{block.recovery}</div>} />;
  if (block.type === 'source') return <section className="report-block source-block"><h3>{block.title}</h3><p>{block.body}</p></section>;
  if (block.type === 'diagnostic') return <section className="report-block"><h3>{block.title}</h3><Diagnostic report={report} /></section>;
  if (block.type === 'training_curves') return <section className="report-block"><h3>{block.title}</h3><TrainingCurves block={block} /><p className="report-chart-note">纵轴为对数尺度；末端标签和下方排名表保证无需 hover 也能完成比较。</p></section>;
  if (block.type === 'geometry_errors') return <section className="report-block"><h3>{block.title}</h3><GeometryErrors block={block} /><p className="report-chart-note">单位：无量纲相对误差；精确值同时保留在后续审计表中。</p></section>;
  if (block.type === 'timeseries_diagnostics') return <section className="report-block"><h3>{block.title}</h3><DiagnosticsChart block={block} /><p className="report-chart-note">Wφ 使用右轴；其余序列使用左轴，数值可在后续范围表中精确核对。</p></section>;
  if (block.type === 'spectrum_heatmap') return <section className="report-block"><h3>{block.title}</h3><SpectrumHeatmap block={block} /><p className="report-chart-note">颜色表示归一化谱强度，主峰位置同时用白线编码，不依赖 hover。</p></section>;
  if (block.type === 'field_frames') return <section className="report-block"><h3>{block.title}</h3><FieldFrames block={block} /><p className="report-chart-note">三幅图均由同一 NPZ 的 {block.field} 按规则网格抽样生成，不是占位热力图。</p></section>;
  if (block.type === 'image_gallery') return <section className="report-block"><h3>{block.title}</h3><div className="gs-image-gallery">{block.items.map((item) => <figure key={item.name}><img loading="lazy" src={item.url} alt={`${item.name}：PINO、传统解、差值与残差比较图`} /><figcaption><strong>{item.name}</strong><span>ψ L2 相对误差 {item.psi_l2_relative}</span></figcaption></figure>)}</div></section>;
  if (block.type === 'source_link') return <section className="report-block source-block"><h3>{block.title}</h3><p>{block.body}</p></section>;
  return null;
}

function DocumentBlock({ block }) {
  if (block.layout?.hidden) return null;
  if (block.type === 'visualization') return <div className="document-report-block"><ExamplePreview visualizationId={block.source_ref?.visualization_id} embedded /></div>;
  if (block.type === 'markdown') return <article className="document-report-block markdown-evidence">{block.title && block.title !== '待补充' ? <h3>{block.title}</h3> : null}<ReactMarkdown>{block.body || ''}</ReactMarkdown></article>;
  if (block.type === 'metric') return <div className="document-report-block document-metric"><span>{block.title}</span><strong>{block.value}<small>{block.unit}</small></strong></div>;
  if (block.type === 'table') return <div className="document-report-block"><h3>{block.title}</h3><Table size="small" pagination={false} rowKey={stableRowKey} columns={(block.columns ?? []).map((title, index) => ({ title, dataIndex: index }))} dataSource={block.rows ?? []} /></div>;
  if (block.type === 'callout') return <Alert className="document-report-block" type="info" showIcon message={block.title} description={block.body} />;
  if (block.type === 'divider') return <div className="document-report-block"><hr /></div>;
  if (block.type === 'page_break') return <div className="document-page-break">导出时分页</div>;
  if (block.type === 'toc') return <nav className="document-report-block"><b>目录</b><span>导出时由 Quarto 自动生成</span></nav>;
  if (block.type === 'source') return <section className="document-report-block source-block"><h3>{block.title}</h3><p>{block.body}</p></section>;
  return <section className="document-report-block"><h3>{block.title || block.type}</h3><p>{block.body}</p></section>;
}

function DocumentReport({ report, state, remote }) {
  const document = report.document;
  return <article className="workspace-page report-reader document-report-reader"><PageTitle title={document.metadata?.title || report.title} description={document.metadata?.goal || report.summary} meta={<ConnectionStatus state={state} updatedAt={remote.updatedAt} onRetry={remote.retry} />} actions={<><Link to="/reports"><Button icon={<ArrowLeftOutlined />}>报告中心</Button></Link>{report.editable ? <Link to={`/reports/${report.id}/edit`}><Button type="primary" icon={<EditOutlined />}>继续编排</Button></Link> : null}<ReportDownload reportId={report.id} /><Button icon={<CopyOutlined />} onClick={() => navigator.clipboard?.writeText(location.href)}>复制链接</Button></>} />
    <div className="report-byline"><span>作者 {document.metadata?.author || report.author}</span><span>面向 {document.metadata?.audience || '项目团队'}</span><span>草稿修订 r{report.draft_revision}</span><Tag color="processing">{report.status}</Tag></div>
    {document.sections.map((section, sectionIndex) => <section className="report-section document-section" key={section.id}><header><span>{String(sectionIndex + 1).padStart(2, '0')}</span><h2>{section.title}</h2></header>{section.description ? <p>{section.description}</p> : null}{section.rows.map((row) => <div className="document-report-row" key={row.id}>{row.blocks.map((block) => <div key={block.id} style={{ gridColumn: `span ${block.layout?.span ?? 12}` }}><DocumentBlock block={block} /></div>)}</div>)}</section>)}
  </article>;
}

export default function ReportPage() {
  const { reportId } = useParams();
  const [searchParams] = useSearchParams();
  const snapshotReportId = searchParams.get('exportSnapshot');
  const snapshotVersion = searchParams.get('snapshotVersion');
  const loader = useCallback(() => snapshotReportId && snapshotVersion ? apiReportSnapshot(snapshotReportId, snapshotVersion) : apiReport(reportId), [reportId, snapshotReportId, snapshotVersion]);
  const remote = useRemoteSnapshot(`report:${reportId}:${snapshotReportId || 'live'}:${snapshotVersion || 'current'}`, loader, null);
  const report = remote.data;

  if (!report && remote.error?.status === 404) return <Result status="404" title="报告不存在" subTitle={`未找到报告 ${reportId}，系统不会回退到其他报告。`} extra={<Link to="/reports"><Button type="primary">返回报告中心</Button></Link>} />;
  if (!report && remote.state === 'offline') return <Result status="warning" title="报告服务离线" subTitle="当前没有该报告的最近快照。服务恢复后可重试。" extra={<Button onClick={remote.retry}>重试</Button>} />;
  if (!report) return <div className="workspace-page"><Alert type="info" message="正在加载报告…" /></div>;

  const state = report.status === 'failed' ? 'error' : report.status === 'partial' ? 'partial' : remote.state;
  if (report.document) return <DocumentReport report={report} state={state} remote={remote} />;
  return <article className="workspace-page report-reader"><PageTitle title={report.title} description={report.summary} meta={<ConnectionStatus state={state} updatedAt={remote.updatedAt} onRetry={remote.retry} />} actions={<><Link to="/reports"><Button icon={<ArrowLeftOutlined />}>报告中心</Button></Link><ReportDownload reportId={report.id} /><Button icon={<CopyOutlined />} onClick={() => navigator.clipboard?.writeText(location.href)}>复制链接</Button></>} />
    <div className="report-byline"><span>作者 {report.author}</span><span>生成于 {report.generated_at}</span><span>报告配置 {report.spec}</span><Tag color={report.status === 'failed' ? 'error' : report.status === 'partial' ? 'warning' : 'success'}>{report.status}</Tag></div>
    <section className="report-conclusions"><h2>结论</h2><ul>{report.takeaways.map((item) => <li key={item}>{item}</li>)}</ul></section>
    {report.sections.map((section) => <section className="report-section" key={section.id}><header><span>{String(report.sections.indexOf(section) + 1).padStart(2, '0')}</span><h2>{section.title}</h2></header>{section.blocks.map((block, index) => <ReportBlock block={block} report={report} key={`${block.type}-${index}`} />)}</section>)}
  </article>;
}
