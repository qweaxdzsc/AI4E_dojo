import { useEffect, useRef, useState } from 'react';
import { Alert } from 'antd';

function specFor(payload) {
  const matrix = payload.data.values ?? payload.data.matrix ?? [];
  const values = matrix.flatMap((row, y) => row.map((value, x) => ({ x, y, value: Number(value) })));
  const params = payload.resolved_spec?.params ?? {};
  return {
    $schema: 'https://vega.github.io/schema/vega-lite/v6.json',
    width: 'container', height: params.height ?? 420, background: params.background_color ?? '#ffffff',
    title: params.title || undefined, data: { values }, mark: { type: 'rect', tooltip: params.show_tooltip !== false },
    encoding: {
      x: { field: 'x', type: 'ordinal', title: null }, y: { field: 'y', type: 'ordinal', title: null },
      color: { field: 'value', type: 'quantitative', scale: { scheme: params.colormap ?? 'viridis', reverse: Boolean(params.reverse_colormap), domain: Number.isFinite(params.range_min) && Number.isFinite(params.range_max) ? [params.range_min, params.range_max] : undefined } }
    },
    config: { view: { stroke: null }, axis: { labelFontSize: params.font_size ?? 12 } }
  };
}

export default function VegaRenderer({ payload }) {
  const ref = useRef(null);
  const [error, setError] = useState(null);
  useEffect(() => {
    let active = true;
    let view;
    import('vega-embed').then((module) => module.default(ref.current, specFor(payload), { actions: true, renderer: 'svg' })).then((result) => { view = result?.view; }).catch((reason) => active && setError(reason));
    return () => { active = false; view?.finalize(); };
  }, [payload]);
  if (error) return <Alert type="error" showIcon message="Vega 加载失败" description={error.message} />;
  return <div ref={ref} className="vega-renderer" />;
}

