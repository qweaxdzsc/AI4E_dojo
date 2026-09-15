"""散点图、折线图和柱状图字段映射业务规则。"""


def validate_basic_chart(chart: str, x_field: str, y_field: str) -> tuple[str, str, str]:
    """校验基础图表类型及横纵字段。"""

    normalized = chart.strip().lower()
    if normalized not in {"scatter", "line", "bar"}:
        raise ValueError("基础图表仅支持散点、折线和柱状图")
    if not x_field.strip() or not y_field.strip():
        raise ValueError("基础图表横纵字段不能为空")
    return normalized, x_field, y_field


def history_curve(rows: list[dict]) -> str:
    """为查询结果生成轻量 SVG 曲线，无效时刻处断开连线。"""
    import html
    segments, current = [], []
    for row in rows:
        if row.get('valid') and row.get('values'):
            name, value = next(iter(row['values'].items()))
            current.append((row.get('time', len(current)), value[0], name))
        elif current:
            segments.append(current)
            current = []
    if current:
        segments.append(current)
    samples = [point for segment in segments for point in segment]
    if len(samples) < 2:
        return ''
    xmin, xmax = min(p[0] for p in samples), max(p[0] for p in samples)
    ymin, ymax = min(p[1] for p in samples), max(p[1] for p in samples)
    lines = []
    for segment in segments:
        points = ' '.join(f'{20+220*(x-xmin)/(xmax-xmin or 1):.2f},{100-80*(y-ymin)/(ymax-ymin or 1):.2f}' for x,y,_ in segment)
        lines.append(f'<polyline points="{points}" fill="none" stroke="#1677ff" stroke-width="2"/>')
    return f'<svg viewBox="0 0 260 125"><text x="10" y="12" font-size="11">{html.escape(samples[0][2])}</text>{"".join(lines)}<text x="10" y="120" font-size="10">t={xmin:g} — {xmax:g}</text></svg>'
