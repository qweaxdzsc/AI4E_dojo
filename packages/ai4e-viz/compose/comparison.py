"""比较产物的离线 HTML 表达，无训练或物理计算依赖。"""

import html
import json
from pathlib import Path

from ai4e_viz.render.comparison import render


def _compose(paths, output, *, title):
    """同一数据集多个域合成报告，失败报告拒绝展示为完整结果。"""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    reports = [json.loads(Path(p).read_text()) for p in paths]
    if any(report["status"] != "succeeded" for report in reports):
        raise ValueError("比较计算未完成")
    sections = []
    images = []
    for report in reports:
        rows = []
        for model, metrics in report["metrics"].items():
            for field, values in metrics.items():
                cells = [
                    model,
                    field,
                    values["count"],
                    values["mse"],
                    values["mae"],
                    values["relative_l2"],
                ]
                rows.append(
                    "<tr>"
                    + "".join(
                        "<td>"
                        + html.escape(
                            "undefined"
                            if v is None
                            else f"{v:.6g}"
                            if isinstance(v, float)
                            else str(v)
                        )
                        + "</td>"
                        for v in cells
                    )
                    + "</tr>"
                )
        sections.append(
            "<h2>"
            + html.escape(report["domain"])
            + "</h2><table><tr><th>Model</th><th>Field</th><th>Elements</th><th>MSE</th><th>MAE</th><th>Relative L2</th></tr>"
            + "".join(rows)
            + "</table>"
        )
        for i, visual in enumerate(report["visuals"]):
            for field in visual["fields"]:
                filename = f"{report['domain']}-{i}-{field}.png"
                image = render({**visual, "models": report["models"]}, field, output / filename)
                images.append(image)
                (output / "render-progress.json").write_text(
                    json.dumps({"status": "running", "completed": images}, indent=2)
                )
                sections.append(
                    "<figure><figcaption>"
                    + html.escape(
                        visual["sample"]
                        + " | "
                        + visual.get("field_labels", {}).get(field, field)
                        + " | "
                        + visual["kind"]
                    )
                    + '</figcaption><img src="'
                    + filename
                    + '"></figure>'
                )
    text = (
        '<!doctype html><html lang="en"><meta charset="utf-8"><title>'
        + html.escape(title)
        + "</title><style>body{font:16px system-ui;margin:30px;color:#182333;background:#f8fafc}table{border-collapse:collapse;background:white}td,th{padding:9px 16px;border-bottom:1px solid #ddd;text-align:right}img{width:100%;background:white}figure{margin:24px 0}figcaption{font-weight:600}h1{font-size:28px}</style><h1>"
        + html.escape(title)
        + "</h1><p>Training budget and execution environment are recorded in the source run artifacts. Five fixed test samples; full valid points. First three samples visualized. Identical geometry and scales for model predictions. Undefined relative error means zero truth norm. No accuracy threshold.</p>"
        + "".join(sections)
        + "</html>"
    )
    target = output / "index.html"
    target.write_text(text)
    (output / "rendering.json").write_text(json.dumps(images, indent=2))
    return target


def compose(paths: list, output: str | Path, *, title: str) -> Path:
    """逐项记录渲染交付；失败保留图像并撤下本次完整报告状态。"""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    progress = output / "render-progress.json"
    progress.write_text(json.dumps({"status": "running", "completed": []}))
    (output / "index.html").write_text(
        "<!doctype html><meta charset=utf-8><h1>Report incomplete</h1><p>Rendering in progress. Inspect render-progress.json for delivery status.</p>"
    )
    try:
        result = _compose(paths, output, title=title)
        record = json.loads(progress.read_text())
        record["status"] = "succeeded"
        progress.write_text(json.dumps(record, indent=2))
        return result
    except BaseException as error:
        record = json.loads(progress.read_text())
        record.update(status="failed", error={"type": type(error).__name__, "message": str(error)})
        progress.write_text(json.dumps(record, indent=2))
        raise
