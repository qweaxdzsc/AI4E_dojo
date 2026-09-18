"""线段提取的 Line Chart View：X/Y 轴映射、折线标记和 CSV。

对齐 ParaView Displaying Data 中 Line Chart View 的 X Array Name、
Use Index for XAxis 与 Series Parameters，以及 Plot Over Line 输出的
arc_length / Points_X|Y|Z。计算仍由 visEngine 取样，这里只做图表表达。
"""

from __future__ import annotations

import csv
import html
import io
import math
from pathlib import Path

# ParaView Line Chart View 常见独立变量；缺省横轴为弧长。
X_BUILTIN = (
    ("arc_length", "弧长 (arc_length)"),
    ("index", "采样点序号 (Use Index for XAxis)"),
    ("Points_X", "点坐标 X (Points_X)"),
    ("Points_Y", "点坐标 Y (Points_Y)"),
    ("Points_Z", "点坐标 Z (Points_Z)"),
)
_SKIP_FIELDS = {"vtkValidPointMask", "vtkGhostType"}
_SERIES_COLORS = ("#1677ff", "#d4380d", "#389e0d", "#722ed1", "#d48806", "#13c2c2")


def _field_map(row: dict) -> dict:
    """优先用带归属前缀的场，避免同名 point/cell 混淆。"""
    return row.get("fields") or row.get("values") or {}


def _is_number(value) -> bool:
    """只接受有限标量，不把布尔当成坐标。"""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _scalar(value, component=None):
    """把取样单元格收成一个有限标量；矢量按分量或模长。"""
    if isinstance(value, list):
        if component == "magnitude":
            if not value or not all(_is_number(item) for item in value):
                return None
            return math.sqrt(sum(float(item) * float(item) for item in value))
        index = 0 if component is None else int(component)
        if index < 0 or index >= len(value) or not _is_number(value[index]):
            return None
        return float(value[index])
    return float(value) if _is_number(value) else None


def _parse_series(name: str) -> tuple[str, object]:
    """把 `场:0` / `场:magnitude` 拆成场名与分量。"""
    if name.endswith(":magnitude"):
        return name[: -len(":magnitude")], "magnitude"
    if ":" in name:
        head, tail = name.rsplit(":", 1)
        if tail.isdigit():
            return head, int(tail)
    return name, None


def sampled_field_names(rows: list[dict]) -> list[str]:
    """已取样场名，排除 VTK 内部掩码。"""
    names: list[str] = []
    for row in rows:
        for key in _field_map(row):
            if key in _SKIP_FIELDS or key in names:
                continue
            names.append(key)
    return names


def axis_choices(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """X 轴含官方独立变量和已取样场；Y 轴为可多选系列。"""
    fields = sampled_field_names(rows)
    extras = [{"text": name, "value": name} for name in fields]
    x_items = [{"text": label, "value": key} for key, label in X_BUILTIN]
    seen = {item["value"] for item in x_items}
    for item in extras:
        if item["value"] not in seen:
            x_items.append(item)
            seen.add(item["value"])
    y_items = [
        {"text": "弧长 (arc_length)", "value": "arc_length"},
        {"text": "点坐标 X (Points_X)", "value": "Points_X"},
        {"text": "点坐标 Y (Points_Y)", "value": "Points_Y"},
        {"text": "点坐标 Z (Points_Z)", "value": "Points_Z"},
    ]
    y_seen = {item["value"] for item in y_items}
    for name in fields:
        sample = next((_field_map(row).get(name) for row in rows if name in _field_map(row)), None)
        if name not in y_seen:
            y_items.append({"text": name, "value": name})
            y_seen.add(name)
        if isinstance(sample, list) and len(sample) > 1:
            for index in range(len(sample)):
                key = f"{name}:{index}"
                if key not in y_seen:
                    y_items.append({"text": f"{name}[{index}]", "value": key})
                    y_seen.add(key)
            if len(sample) == 3:
                key = f"{name}:magnitude"
                if key not in y_seen:
                    y_items.append({"text": f"{name} 模长", "value": key})
                    y_seen.add(key)
    return x_items, y_items


def default_y_arrays(rows: list[dict]) -> list[str]:
    """缺省画第一条标量场，没有场则不选。"""
    for name in sampled_field_names(rows):
        sample = next((_field_map(row).get(name) for row in rows if name in _field_map(row)), None)
        if sample is None:
            continue
        if not isinstance(sample, list) or len(sample) == 1:
            return [name]
    names = sampled_field_names(rows)
    return names[:1]


def resolve_x(row: dict, index: int, x_array: str):
    """按 ParaView X Array Name / Use Index 取独立变量。"""
    if x_array == "index":
        return float(index)
    return resolve_series(row, x_array)


def resolve_series(row: dict, name: str):
    """从一行取样读弧长、点坐标或已取样场。"""
    if name == "arc_length":
        value = row.get("distance")
        return float(value) if _is_number(value) else None
    if name == "Points_X":
        position = row.get("position") or []
        return float(position[0]) if len(position) > 0 and _is_number(position[0]) else None
    if name == "Points_Y":
        position = row.get("position") or []
        return float(position[1]) if len(position) > 1 and _is_number(position[1]) else None
    if name == "Points_Z":
        position = row.get("position") or []
        return float(position[2]) if len(position) > 2 and _is_number(position[2]) else None
    field_name, component = _parse_series(name)
    return _scalar(_field_map(row).get(field_name), component)


def line_chart_table(rows: list[dict], x_array: str, y_arrays: list[str]) -> tuple[list[str], list[list]]:
    """当前图用的采样表：第一列 X，其后为所选 Y。"""
    headers = [x_array, *y_arrays]
    body = []
    for index, row in enumerate(rows):
        x_value = resolve_x(row, index, x_array)
        cells = [x_value]
        for name in y_arrays:
            cells.append(resolve_series(row, name) if row.get("valid") else None)
        body.append(cells)
    return headers, body


def line_chart_csv_text(rows: list[dict], x_array: str, y_arrays: list[str]) -> str:
    """导出当前折线图使用的列，无效 Y 留空。"""
    headers, body = line_chart_table(rows, x_array, y_arrays)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    for cells in body:
        writer.writerow(["" if cell is None else cell for cell in cells])
    return buffer.getvalue()


def write_line_chart_csv(path: Path, rows: list[dict], x_array: str, y_arrays: list[str]) -> Path:
    """把当前图表写成 CSV 文件，供下载读回。"""
    target = Path(path)
    target.write_text(line_chart_csv_text(rows, x_array, y_arrays), encoding="utf-8")
    return target


def line_chart_markup(
    rows: list[dict],
    x_array: str,
    y_arrays: list[str],
    *,
    width: int = 720,
    height: int = 400,
    title: str = "",
) -> str:
    """视口区折线图：多系列、坐标轴、图例，不是侧栏缩略图。"""
    if not y_arrays:
        y_arrays = default_y_arrays(rows)
    series = []
    for name in y_arrays:
        points = []
        for index, row in enumerate(rows):
            x_value = resolve_x(row, index, x_array)
            y_value = resolve_series(row, name) if row.get("valid") else None
            if x_value is None or y_value is None:
                if points and points[-1] is not None:
                    points.append(None)
                continue
            points.append((x_value, y_value))
        usable = [point for point in points if point]
        if len(usable) >= 2:
            series.append((name, usable))
    if not series:
        return ""
    xs = [x for _, points in series for x, _ in points]
    ys = [y for _, points in series for _, y in points]
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)
    if xmin == xmax:
        xmax = xmin + 1
    if ymin == ymax:
        ymax = ymin + 1
    left, right, top, bottom = 64, width - 16, 36, height - 48
    span_x, span_y = right - left, bottom - top

    def px(x, y):
        """数据坐标落到 SVG 像素。"""
        return (
            left + span_x * (x - xmin) / (xmax - xmin),
            bottom - span_y * (y - ymin) / (ymax - ymin),
        )

    parts = [
        (
            f'<svg class="phys-line-chart-svg" viewBox="0 0 {width} {height}" '
            f'preserveAspectRatio="none" role="img" aria-label="折线图">'
            f'<rect x="0" y="0" width="{width}" height="{height}" fill="#ffffff"/>'
        )
    ]
    for step in range(5):
        x = left + span_x * step / 4
        y = top + span_y * step / 4
        parts.append(
            f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" '
            f'stroke="#e6edf5" stroke-width="1"/>'
        )
        parts.append(
            f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" '
            f'stroke="#e6edf5" stroke-width="1"/>'
        )
    parts.append(
        f'<line x1="{left}" y1="{bottom}" x2="{right}" y2="{bottom}" stroke="#334155" />'
        f'<line x1="{left}" y1="{top}" x2="{left}" y2="{bottom}" stroke="#334155" />'
    )
    for step in range(5):
        x_value = xmin + (xmax - xmin) * step / 4
        y_value = ymin + (ymax - ymin) * step / 4
        x = left + span_x * step / 4
        y = bottom - span_y * step / 4
        parts.append(
            f'<text x="{x:.1f}" y="{bottom + 16}" text-anchor="middle" '
            f'font-size="11" fill="#334155">{html.escape(f"{x_value:g}")}</text>'
        )
        parts.append(
            f'<text x="{left - 8}" y="{y + 4:.1f}" text-anchor="end" '
            f'font-size="11" fill="#334155">{html.escape(f"{y_value:g}")}</text>'
        )
    heading = title or " / ".join(name for name, _ in series[:3])
    parts.append(
        f'<text x="{left}" y="20" font-size="13" fill="#102853">'
        f"{html.escape(heading)}</text>"
    )
    parts.append(
        f'<text x="{(left + right) / 2:.1f}" y="{height - 8}" text-anchor="middle" '
        f'font-size="12" fill="#334155">{html.escape(x_array)}</text>'
    )
    for index, (name, points) in enumerate(series):
        color = _SERIES_COLORS[index % len(_SERIES_COLORS)]
        polyline = " ".join(f"{px(x, y)[0]:.2f},{px(x, y)[1]:.2f}" for x, y in points)
        parts.append(
            f'<polyline points="{polyline}" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linejoin="round"/>'
        )
        parts.append(
            f'<rect x="{right - 140}" y="{12 + index * 16}" width="10" height="10" fill="{color}"/>'
            f'<text x="{right - 126}" y="{21 + index * 16}" font-size="11" fill="#102853">'
            f"{html.escape(name)}</text>"
        )
    parts.append("</svg>")
    return "".join(parts)
