"""平台两档结构图展示；只接收可前向网络和输入，不读案例配置。

公开子模块能收成阶段盒时，先按阶段组织再套两档官方参数，避免正式 forward 的校验算子进图。
"""

from __future__ import annotations

import json
import random
import shutil
import sys
import tempfile
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

import numpy as np
import torch
from ai4e_viz.inspect.stage_display import organize_for_display

_FIT_ENTIRE_GRAPH = "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;"
_FIT_WIDTH = "const scale = Math.min(1, (width * 0.92) / Math.max(graphWidth, 1));"
_CENTER_VERTICAL = "height / 2 - (minY + graphHeight / 2) * scale"
_TOP_ALIGN = "24 - minY * scale"
DEFAULT_VIEW = "stage_trunk"
PLATFORM_VIEWS = (
    {
        "id": "stage_trunk",
        "label": "阶段主干",
        "member": "model.stage-trunk.html",
        "options": {
            "collapse_modules_after_depth": 1,
            "forced_module_tracing_depth": 0,
            "show_compressed_view": True,
            "show_module_attr_names": True,
            "show_non_gradient_nodes": False,
        },
    },
    {
        "id": "stage_blocks",
        "label": "阶段压缩块",
        "member": "model.stage-blocks.html",
        "options": {
            "collapse_modules_after_depth": 1,
            "forced_module_tracing_depth": 1,
            "show_compressed_view": True,
            "show_module_attr_names": True,
            "show_non_gradient_nodes": False,
        },
    },
)


def fit_graph_viewport(html: str) -> str:
    """把 TorchVista 默认的整图塞进视口改成按宽度适配，避免深网络缩成看不见的细线。"""
    if _FIT_ENTIRE_GRAPH not in html:
        raise RuntimeError("TorchVista 结构页缺少整图缩放语句，无法改成按宽度显示")
    return html.replace(_FIT_ENTIRE_GRAPH, _FIT_WIDTH, 1).replace(_CENTER_VERTICAL, _TOP_ALIGN, 1)


@contextmanager
def _preserve_randomness():
    """跟踪不得改写调用方随机流；成功和失败都恢复。"""
    python_state, numpy_state = random.getstate(), np.random.get_state()
    mps_state = torch.mps.get_rng_state() if torch.backends.mps.is_available() else None
    try:
        with torch.random.fork_rng():
            yield
    finally:
        random.setstate(python_state)
        np.random.set_state(numpy_state)
        if mps_state is not None:
            torch.mps.set_rng_state(mps_state)


def _forwardable(network: torch.nn.Module, predict):
    """可选预测入口只作为通用 forward 适配，不认识具体模型。"""
    if predict is None:
        return network.eval()

    class ForwardAdapter(torch.nn.Module):
        def __init__(self, inner):
            super().__init__()
            self.network = inner

        def forward(self, values):
            return predict(self.network, values)

    return ForwardAdapter(network).eval()


def _export_one(model: torch.nn.Module, inputs, target: Path, options: dict) -> str:
    """按一套官方参数写出单页；空文件视为失败。"""
    from torchvista import trace_model

    with redirect_stdout(sys.stderr):
        trace_model(
            model,
            inputs,
            export_format="html",
            export_path=str(target),
            **options,
        )
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("TorchVista 未生成结构资产")
    html = fit_graph_viewport(target.read_text(encoding="utf-8"))
    target.write_text(html, encoding="utf-8")
    return html


def export_platform_views(
    network: torch.nn.Module,
    inputs,
    output_dir: Path,
    *,
    revision: str,
    input_source: dict,
    predict=None,
) -> dict:
    """一次按平台两档官方参数出页；任一档失败则两档都不发布。"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    record_path = output_dir / "model-inspection.json"
    members = [output_dir / spec["member"] for spec in PLATFORM_VIEWS]
    staging = Path(tempfile.mkdtemp(prefix="model-graph-", dir=str(output_dir)))
    published: list[Path] = []
    try:
        organized = organize_for_display(network, inputs)
        if organized is None:
            target_model = _forwardable(network, predict)
        else:
            target_model, inputs = organized
        views: dict[str, dict] = {}
        with _preserve_randomness():
            for spec in PLATFORM_VIEWS:
                html = _export_one(target_model, inputs, staging / spec["member"], spec["options"])
                views[spec["id"]] = {
                    "id": spec["id"],
                    "label": spec["label"],
                    "member": spec["member"],
                    "graph_nodes": html.count('"node_type"'),
                }
        for spec in PLATFORM_VIEWS:
            destination = output_dir / spec["member"]
            (staging / spec["member"]).replace(destination)
            published.append(destination)
            views[spec["id"]]["path"] = str(destination)
        default = views[DEFAULT_VIEW]
        record = {
            "schema_version": 1,
            "status": "succeeded",
            "path": default["path"],
            "configuration_revision": revision,
            "input_source": input_source,
            "parameter_count": sum(p.numel() for p in network.parameters()),
            "model_type": type(network).__module__ + "." + type(network).__name__,
            "graph_nodes": default["graph_nodes"],
            "graph_view": DEFAULT_VIEW,
            "default_view": DEFAULT_VIEW,
            "views": views,
        }
        record_path.write_text(
            json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        return record
    except Exception:
        for path in published:
            path.unlink(missing_ok=True)
        record_path.unlink(missing_ok=True)
        for path in members:
            path.unlink(missing_ok=True)
        raise
    finally:
        shutil.rmtree(staging, ignore_errors=True)
