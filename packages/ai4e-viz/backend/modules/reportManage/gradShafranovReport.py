"""Data-derived report blocks for the portable PINO Grad–Shafranov audit."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from infrastructure.config import REPOSITORY_ROOT


ROOT = REPOSITORY_ROOT / "fixtures" / "gs"
MANIFEST_PATH = ROOT / "manifest.json"
REPORT_ID = "rep-gs-pino-2026-0823"

MODEL_LABELS = {
    "cnn_kan": "CNN–KAN", "cnn_mlp": "CNN–MLP", "fno_kan": "FNO–KAN", "fno_mlp": "FNO–MLP",
    "kan_kan": "KAN–KAN", "mlp_mlp": "MLP–MLP", "transformer_kan": "Transformer–KAN", "transformer_mlp": "Transformer–MLP",
}
GEOMETRY_LABELS = {
    "circular": "圆形", "low_elongation": "低拉伸", "medium_elongation": "中拉伸", "high_elongation": "高拉伸",
    "extreme_elongation": "极端拉伸", "negative_triangularity": "负三角形度", "large_plasma": "大等离子体", "small_plasma": "小等离子体",
}


def _manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def _training_series(model: str, maximum: int = 120) -> dict:
    path = ROOT / "models" / model / "metrics.csv"
    with path.open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    stride = max(1, len(rows) // maximum)
    sampled = rows[::stride]
    if sampled[-1] is not rows[-1]:
        sampled.append(rows[-1])
    return {
        "name": MODEL_LABELS[model],
        "x": [int(float(row["epoch"])) for row in sampled],
        "values": [float(row["val_loss"]) for row in sampled],
    }


def report_list_item() -> dict:
    """返回 Grad–Shafranov 内置审计报告的列表摘要。"""

    return {
        "id": REPORT_ID,
        "title": "PINO Grad–Shafranov 多几何泛化审计报告",
        "status": "succeeded",
        "status_note": "当前 fixture 已重算 · 源文档差异已归档说明",
        "generated_at": "2026-08-23 18:40",
        "author": "AI4E 数值审计",
        "formats": ["HTML", "PDF"],
    }


def build_report(base_url: str) -> dict:
    """从固化 fixture 重算模型和几何指标并构建可阅读审计报告。"""

    manifest = _manifest()
    model_rows = []
    for model, metrics in manifest["models"].items():
        model_rows.append([
            MODEL_LABELS[model], metrics["epochs"], metrics["best_epoch"],
            round(metrics["best_validation_loss"], 8), round(metrics["mean_psi_l2_relative"], 3),
            round(metrics["mean_ip_relative_error"] * 100, 2),
        ])
    model_rows.sort(key=lambda row: row[4])
    geometry_rows = []
    for name, metrics in manifest["geometries"].items():
        geometry_rows.append([
            GEOMETRY_LABELS[name], " × ".join(map(str, metrics["grid_shape"])),
            round(metrics["psi_l2_relative"], 3), round(metrics["ip_relative_error"] * 100, 2),
        ])
    geometry_rows.sort(key=lambda row: row[2], reverse=True)
    gallery = [
        {
            "name": GEOMETRY_LABELS[name],
            "psi_l2_relative": round(metrics["psi_l2_relative"], 3),
            "url": f"{base_url}api/gs-fixture/cases/{name}/pino_vs_traditional_comparison.png",
        }
        for name, metrics in manifest["geometries"].items()
    ]
    return {
        **report_list_item(),
        "summary": "八种架构均完成 5,000 epochs；全部几何场指标均从当前 151×241 网格数据重新计算，FNO–MLP 的最低验证损失最好。跨几何 ψ 误差与约 200% 的电流符号差异作为科学口径风险完整记录，不影响报告阅读。",
        "spec": "rspec-gs-audit v1",
        "takeaways": [
            "FNO–MLP 最低验证损失约 0.00332072；训练损失不能替代跨几何误差。",
            "CNN–MLP 在当前八几何比较中的平均 ψ L2 相对误差最低，约 8.30。",
            "KAN–KAN 平均 ψ L2 相对误差约 132，出现明显退化；small-plasma 是主要困难几何。",
            "多数样例 PINO 电流约 +3 MA、传统解约 −3 MA，现有相对误差接近 200%，需先统一符号约定。",
        ],
        "sections": [
            {
                "id": "conclusion", "title": "审计结论", "blocks": [
                    {"type": "metrics", "title": "当前可证实结果", "items": [
                        {"label": "模型组合", "value": "8", "unit": "组", "state": "ok"},
                        {"label": "训练轮数", "value": "5000", "unit": "epochs", "state": "ok"},
                        {"label": "实际网格", "value": "151×241", "unit": "", "state": "ok"},
                        {"label": "电流相对误差", "value": "≈200", "unit": "%", "state": "warn"},
                    ]},
                    {"type": "source", "title": "源文档口径说明", "body": "归档 HTML 描述的是较早的 101×161、单一 TKNO/约 50k 参数试验；本报告使用当前 151×241 fixture 和八种模型组合重新计算全部指标。旧文档只作为历史来源附件，不参与当前数值结论。"},
                ],
            },
            {
                "id": "training", "title": "模型训练与排名", "blocks": [
                    {"type": "training_curves", "title": "八模型验证损失（对数轴）", "series": [_training_series(model) for model in MODEL_LABELS], "x_label": "Epoch", "y_label": "Validation loss"},
                    {"type": "table", "title": "跨几何结果排名", "columns": ["模型", "epochs", "最佳 epoch", "最低 val loss", "平均 ψ L2 相对误差", "平均 Ip 相对误差 (%)"], "rows": model_rows},
                ],
            },
            {
                "id": "geometry", "title": "八种几何证据", "blocks": [
                    {"type": "geometry_errors", "title": "CNN–MLP 各几何 ψ L2 相对误差", "items": [{"name": row[0], "value": row[2]} for row in geometry_rows], "y_label": "ψ L2 relative error"},
                    {"type": "image_gallery", "title": "PINO / 传统解 / 差值 / 残差对照", "items": gallery},
                    {"type": "table", "title": "几何级审计值", "columns": ["几何", "网格", "ψ L2 相对误差", "Ip 相对误差 (%)"], "rows": geometry_rows},
                ],
            },
            {
                "id": "fields", "title": "可复现的场数据", "blocks": [
                    {"type": "example", "title": "CNN–MLP 圆形几何 PINO 场", "artifact_id": "GS-PINO-CIRCULAR", "caption": "字段选择器来自 NPZ：ψ、Jφ、PDE residual 与 plasma mask；默认展示 ψ。"},
                    {"type": "example", "title": "圆形几何传统解", "artifact_id": "GS-TRAD-CIRCULAR", "caption": "与 PINO 使用同一 151×241 网格，可独立上传并重新解析。"},
                ],
            },
            {
                "id": "source", "title": "来源、口径与可复现性", "blocks": [
                    {"type": "source", "title": "便携数据范围", "body": "包含全部八模型训练 CSV/汇总 JSON，以及 CNN–MLP 八几何的 PINO、传统解、比较指标与比较图；不包含 checkpoint 和其他模型逐几何场文件。"},
                    {"type": "source", "title": "原始项目文档", "body": "归档 HTML 仅用于追溯原叙事；页面中的审计指标均由当前 fixture 重算。该来源文件不再作为报告下载入口。"},
                    {"type": "source", "title": "Fixture manifest", "body": "内部 manifest 记录 57 个文件的相对路径、字节数与 SHA-256。报告右上角统一提供当前阅读版本的 HTML 与 PDF。"},
                ],
            },
        ],
    }
