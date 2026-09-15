import { useEffect, useRef, useState } from 'react';
import { Alert, Spin } from 'antd';

function tracesFor(payload) {
  const { artifact, data } = payload;
  const params = payload.resolved_spec?.params ?? {};
  if (artifact.kind === 'series') return data.series.map((series) => ({ x: data.x, y: series.values, name: series.name, type: 'scatter', mode: params.show_symbols ? 'lines+markers' : 'lines', line: { width: params.line_width ?? 2, dash: params.line_style === 'dashed' ? 'dash' : params.line_style === 'dotted' ? 'dot' : 'solid', shape: params.smooth ? 'spline' : 'linear' } }));
  if (artifact.kind === 'distribution') return [{ x: data.bins.slice(0, -1), y: data.counts, type: 'bar', name: data.field }];
  if (artifact.kind === 'ensemble') return [
    ...data.members.map((values, index) => ({ x: data.x, y: values, name: `成员 ${index + 1}`, type: 'scatter', mode: 'lines', line: { width: 1 }, opacity: 0.28, showlegend: false })),
    { x: data.x, y: data.mean, name: '均值', type: 'scatter', mode: 'lines', line: { width: 3 } }
  ];
  if (artifact.kind === 'uncertainty') return [
    { x: data.x, y: data.lower, name: '下界', type: 'scatter', mode: 'lines', line: { width: 0 }, showlegend: false },
    { x: data.x, y: data.upper, name: '95% 区间', type: 'scatter', mode: 'lines', line: { width: 0 }, fill: 'tonexty', fillcolor: 'rgba(22,119,255,.24)' },
    { x: data.x, y: data.mean, name: '均值', type: 'scatter', mode: 'lines', line: { width: 2.5 } }
  ];
  if (['matrix', 'tensor'].includes(artifact.kind)) return [{ z: data.values ?? data.matrix, type: 'heatmap', colorscale: params.colormap ?? 'Viridis', reversescale: Boolean(params.reverse_colormap), zmin: params.range_min, zmax: params.range_max }];
  if (artifact.kind === 'optimization') return [{ x: data.points.map((item) => item.efficiency), y: data.points.map((item) => item.loss), text: data.points.map((item) => item.id), mode: 'markers', type: 'scatter' }];
  return [];
}

export default function PlotlyRenderer({ payload }) {
  const ref = useRef(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let active = true;
    let Plotly;
    import('plotly.js-dist-min').then((module) => {
      if (!active || !ref.current) return;
      Plotly = module.default ?? module;
      const params = payload.resolved_spec?.params ?? {};
      return Plotly.newPlot(ref.current, tracesFor(payload), {
        title: params.title ? { text: params.title } : undefined,
        paper_bgcolor: params.background_color ?? '#ffffff', plot_bgcolor: params.background_color ?? '#ffffff',
        showlegend: params.show_legend !== false, hovermode: params.show_tooltip === false ? false : 'closest',
        xaxis: { type: params.x_scale === 'log' ? 'log' : undefined }, yaxis: { type: params.y_scale === 'log' ? 'log' : undefined },
        margin: { l: 58, r: 24, t: params.title ? 62 : 28, b: 48 }
      }, { responsive: true, displaylogo: false, scrollZoom: Boolean(params.zoom) });
    }).catch((reason) => active && setError(reason));
    return () => { active = false; if (Plotly && ref.current) Plotly.purge(ref.current); };
  }, [payload]);
  if (error) return <Alert type="error" showIcon message="Plotly 加载失败" description={error.message} />;
  return <div ref={ref} className="plotly-renderer"><Spin /></div>;
}
