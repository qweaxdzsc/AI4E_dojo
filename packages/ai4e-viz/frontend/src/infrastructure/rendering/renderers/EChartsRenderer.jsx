import ReactEChartsCore from 'echarts-for-react/lib/core';
import * as echarts from 'echarts/core';
import { BarChart, GraphChart, HeatmapChart, LineChart, ScatterChart } from 'echarts/charts';
import {
  AriaComponent, BrushComponent, DataZoomComponent, GridComponent, LegendComponent,
  TitleComponent, TooltipComponent, VisualMapComponent
} from 'echarts/components';
import { SVGRenderer } from 'echarts/renderers';

echarts.use([
  BarChart, GraphChart, HeatmapChart, LineChart, ScatterChart,
  AriaComponent, BrushComponent, DataZoomComponent, GridComponent, LegendComponent,
  TitleComponent, TooltipComponent, VisualMapComponent, SVGRenderer
]);

const palettes = {
  engineering: ['#1677ff', '#0e9f9f', '#8250df', '#d97706', '#dc2626'],
  viridis: ['#440154', '#3b528b', '#21918c', '#5ec962', '#fde725'],
  plasma: ['#0d0887', '#7e03a8', '#cc4778', '#f89540', '#f0f921'],
  turbo: ['#30123b', '#466be3', '#28bbec', '#a4fc3c', '#f9ba38', '#d93806'],
  coolwarm: ['#3b4cc0', '#8db0fe', '#dddcdc', '#f4987a', '#b40426'],
  grayscale: ['#111827', '#4b5563', '#9ca3af', '#d1d5db'],
};

function heatmapOption(data, title, params) {
  const matrix = data.values ?? data.matrix ?? [];
  const rows = data.rows ?? matrix.length;
  const cols = data.cols ?? matrix[0]?.length ?? 0;
  const values = matrix.flatMap((row, y) => row.map((value, x) => [x, y, Number(value)]));
  const finite = values.map((value) => value[2]).filter(Number.isFinite);
  const minimum = Number.isFinite(params.range_min) ? params.range_min : finite.length ? Math.min(...finite) : 0;
  const maximum = Number.isFinite(params.range_max) ? params.range_max : finite.length ? Math.max(...finite) : 1;
  const labels = data.labels ?? [];
  return {
    animation: Boolean(params.animation),
    aria: { enabled: true, description: title },
    backgroundColor: params.background_color,
    title: params.title ? { text: params.title, subtext: params.subtitle, left: 'center', textStyle: { fontSize: params.font_size + 3 } } : undefined,
    tooltip: { show: params.show_tooltip !== false },
    grid: { left: 52, right: 72, top: params.title ? 70 : 28, bottom: 46 },
    xAxis: { type: 'category', name: data.x_label, data: labels.length ? labels : Array.from({ length: cols }, (_, i) => i), axisLabel: { interval: Math.max(0, Math.floor(cols / 6) - 1), fontSize: params.font_size } },
    yAxis: { type: 'category', name: data.y_label, data: labels.length ? labels : Array.from({ length: rows }, (_, i) => i), axisLabel: { interval: Math.max(0, Math.floor(rows / 5) - 1), fontSize: params.font_size } },
    visualMap: { min: minimum, max: maximum === minimum ? minimum + 1 : maximum, calculable: true, inverse: Boolean(params.reverse_colormap), right: 0, top: 'middle', textStyle: { fontSize: 10 } },
    series: [{ type: 'heatmap', data: values, emphasis: { itemStyle: { borderColor: '#111827', borderWidth: 1 } } }]
  };
}

function chartOption(kind, data, title, params) {
  const colors = palettes[params.palette] ?? palettes.engineering;
  const common = {
    animation: Boolean(params.animation),
    aria: { enabled: true, description: title },
    color: colors,
    backgroundColor: params.background_color,
    title: params.title ? { text: params.title, subtext: params.subtitle, left: 'center', textStyle: { fontSize: params.font_size + 3 } } : undefined,
    tooltip: { show: params.show_tooltip !== false, trigger: 'axis' },
    legend: { show: params.show_legend !== false && params.legend_position !== 'hidden', [params.legend_position === 'left' || params.legend_position === 'right' ? params.legend_position : 'top']: 0 },
    grid: { left: 58, right: 28, top: params.title ? 76 : 44, bottom: params.zoom ? 70 : 46 },
    dataZoom: params.zoom ? [{ type: 'inside' }, { type: 'slider', height: 18 }] : undefined,
    brush: params.brush ? { toolbox: ['rect', 'clear'], xAxisIndex: 0 } : undefined,
  };
  if (kind === 'scalar') return {
    ...common,
    tooltip: { show: params.show_tooltip !== false, trigger: 'item' },
    xAxis: { type: 'category', data: [data.unit || params.unit || '当前值'] },
    yAxis: { type: 'value', min: 0 },
    series: [{
      type: 'bar', data: [data.value], barMaxWidth: 96,
      label: { show: true, position: 'top', formatter: data.display_value || `{c}${params.unit || data.unit || ''}` },
      markLine: Number.isFinite(params.target ?? data.target) ? {
        symbol: 'none', label: { formatter: `目标 ${params.target ?? data.target}${params.unit || data.unit || ''}` },
        data: [{ yAxis: params.target ?? data.target }]
      } : undefined
    }]
  };
  if (kind === 'series') return {
    ...common,
    xAxis: { type: params.x_scale === 'linear' ? 'value' : params.x_scale === 'time' ? 'time' : 'category', data: data.x, name: data.x_label },
    yAxis: { type: params.y_scale === 'log' ? 'log' : 'value', name: data.y_label },
    series: data.series.map((series) => ({
      name: series.name, type: 'line', showSymbol: Boolean(params.show_symbols), smooth: Boolean(params.smooth),
      symbolSize: 6, lineStyle: { width: params.line_width ?? 2, type: params.line_style ?? 'solid' }, data: series.values
    }))
  };
  if (kind === 'distribution') {
    const horizontal = params.orientation === 'horizontal';
    const category = { type: 'category', data: data.bins.slice(0, -1) };
    const value = { type: 'value', name: data.display_mode === 'density' ? '概率密度' : '样本数' };
    const series = data.display_mode === 'density'
      ? [{ type: 'line', smooth: true, showSymbol: false, areaStyle: { opacity: 0.18 }, data: data.counts, itemStyle: { color: colors[0] } }]
      : [{ type: 'bar', data: data.counts, itemStyle: { color: colors[0] } }];
    return { ...common, xAxis: horizontal ? value : category, yAxis: horizontal ? category : value, series };
  }
  if (kind === 'ensemble') return { ...common, xAxis: { type: 'category', data: data.x }, yAxis: { type: 'value' }, series: [...data.members.map((values, i) => ({ name: `成员 ${i + 1}`, type: 'line', showSymbol: false, lineStyle: { width: 1, opacity: 0.28 }, data: values })), { name: '均值', type: 'line', showSymbol: false, lineStyle: { width: 3 }, data: data.mean }] };
  if (kind === 'uncertainty') return { ...common, xAxis: { type: 'category', data: data.x }, yAxis: { type: 'value' }, series: [{ name: '下界', type: 'line', symbol: 'none', lineStyle: { opacity: 0 }, stack: 'interval', data: data.lower }, { name: '95% 区间', type: 'line', symbol: 'none', lineStyle: { opacity: 0 }, areaStyle: { color: 'rgba(22,119,255,.24)' }, stack: 'interval', data: data.upper.map((value, i) => value - data.lower[i]) }, { name: '均值', type: 'line', data: data.mean }] };
  if (kind === 'optimization' && data.iterations) return { ...common, xAxis: { type: 'category', name: '迭代', data: data.iterations }, yAxis: { type: 'log', name: '目标函数' }, series: [{ type: 'line', showSymbol: false, data: data.objective }] };
  if (kind === 'optimization' && data.factors) return { ...common, xAxis: { type: 'value', name: '敏感度' }, yAxis: { type: 'category', data: data.factors }, series: [{ type: 'bar', data: data.effects, itemStyle: { color: colors[0] } }] };
  if (kind === 'optimization') return { ...common, tooltip: { trigger: 'item' }, xAxis: { type: 'value', name: '效率' }, yAxis: { type: 'value', name: '压降' }, series: [{ type: 'scatter', symbolSize: (value, meta) => meta.data.pareto ? 13 : 8, data: data.points.map((point) => ({ value: [point.efficiency, point.loss], name: point.id, pareto: point.pareto, itemStyle: { color: point.pareto ? colors[1] : '#9aa5b1' } })) }] };
  if (kind === 'point_set') return { ...common, tooltip: { trigger: 'item' }, xAxis: { type: 'value', name: 'x (m)' }, yAxis: { type: 'value', name: 'y (m)' }, series: [{ type: 'scatter', symbolSize: params.point_size ?? 5, data: data.points.map((point) => [point.x, point.y, point.temperature]) }] };
  if (kind === 'trajectory') return { ...common, xAxis: { type: 'value', name: data.position_fields?.[0] ?? 'x' }, yAxis: { type: 'value', name: data.position_fields?.[1] ?? 'y' }, series: data.tracks.map((track) => ({ type: 'line', showSymbol: false, lineStyle: { width: params.line_width ?? 1.3, opacity: params.opacity ?? 0.72 }, data: track.map((point) => [point[0], point[1]]) })) };
  if (kind === 'graph') return { animation: Boolean(params.animation), aria: { enabled: true, description: title }, tooltip: {}, series: [{ type: 'graph', layout: params.layout === 'manual' ? 'none' : params.layout === 'circular' ? 'circular' : 'force', roam: params.zoom !== false, label: { show: params.show_labels !== false, position: 'right' }, symbolSize: params.node_size ?? 28, data: data.nodes.map((node) => ({ ...node, x: node.stage * 150, y: 80 + (node.id.charCodeAt(0) % 3) * 90 })), links: data.links.map(([source, target]) => ({ source, target })), lineStyle: { color: '#9aa5b1', width: params.edge_width ?? 1.5, curveness: 0.08 }, emphasis: { focus: 'adjacency' } }] };
  return null;
}

export default function EChartsRenderer({ payload, height }) {
  const { artifact, data } = payload;
  const params = payload.resolved_spec?.params ?? {};
  const usesHeatmap = ['matrix', 'tensor', 'raster', 'volume', 'field'].includes(artifact.kind);
  const option = usesHeatmap
    ? heatmapOption(data, artifact.takeaway, params)
    : chartOption(artifact.kind, data, artifact.takeaway, params);
  if (!option) return <div className="renderer-empty">ECharts 不支持当前数据结构。</div>;
  return <div role="img" aria-label={`${artifact.name}：${artifact.takeaway}`}>
    <ReactEChartsCore echarts={echarts} option={option} opts={{ renderer: 'svg' }} notMerge style={{ height: height ?? params.height ?? 420 }} />
  </div>;
}
