"""真实模型结构跟踪；仅成功前向的完整 HTML 可以原子发布。"""

import sys
from contextlib import contextmanager, redirect_stdout
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.inference.randomness import preserve_randomness

_FIT_ENTIRE_GRAPH = "const scale = Math.min(width / graphWidth, height / graphHeight) * 0.9;"
_FIT_WIDTH = "const scale = Math.min(1, (width * 0.92) / Math.max(graphWidth, 1));"
_CENTER_VERTICAL = "height / 2 - (minY + graphHeight / 2) * scale"
_TOP_ALIGN = "24 - minY * scale"
# 根适配器之下一层模块收成盒，避免正式网络展开成整图算子。
_MODULE_TRACE_DEPTH = 1


@contextmanager
def preserve_model_state(model):
    """跟踪成功或失败都恢复参数、缓冲区、逐模块模式及随机流。"""
    modes = [(module, module.training) for module in model.modules()]
    registrations = [
        (
            module,
            dict(module._parameters),
            dict(module._buffers),
            dict(module._modules),
            set(module._non_persistent_buffers_set),
        )
        for module, _ in modes
    ]
    # 包括非持久缓冲区；逐张量恢复以保留优化器持有的参数身份。
    tensors = [(value, value.detach().clone()) for value in [*model.parameters(), *model.buffers()]]
    with preserve_randomness():
        try:
            yield
        finally:
            for module, parameters, buffers, children, nonpersistent in registrations:
                module._parameters = parameters
                module._buffers = buffers
                module._modules = children
                module._non_persistent_buffers_set = nonpersistent
            with torch.no_grad():
                for value, saved in tensors:
                    value.copy_(saved)
            for module, training in modes:
                module.training = training


def _export_one(model, inputs, target: Path, options: dict) -> str:
    """跟踪一个显式视图，空页或缺少视口脚本视为失败。"""
    from torchvista import trace_model

    with redirect_stdout(sys.stderr):
        trace_model(model, inputs, export_format="html", export_path=str(target), **options)
    if not target.is_file() or target.stat().st_size == 0:
        raise RuntimeError("TorchVista 未生成结构资产")
    html = fit_graph_viewport(target.read_text(encoding="utf-8"))
    target.write_text(html, encoding="utf-8")
    return html


def trace_views(
    model,
    inputs,
    output_dir: Path,
    *,
    revision: str,
    input_source: dict,
    views,
    default_view: str,
    predict=None,
    model_type: str | None = None,
) -> dict:
    """按调用方显示参数生成固定页面；任一失败回退全部旧文件与来源记录。"""
    import json
    import shutil
    import tempfile

    output_dir = Path(output_dir)
    specs = list(views)
    ids = [spec["id"] for spec in specs]
    members = [spec["member"] for spec in specs]
    if len(ids) != len(set(ids)) or default_view not in ids or len(members) != len(set(members)):
        raise ValueError("invalid_graph_views")
    if any(Path(name).name != name or not name.endswith(".html") for name in members):
        raise ValueError("graph_member_escape")
    output_dir.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix=".model-graph-", dir=output_dir))
    committed, previous = [], []
    try:
        with preserve_model_state(model):
            if predict:

                class ForwardAdapter(torch.nn.Module):
                    def __init__(self, network):
                        super().__init__()
                        self.network = network

                    def forward(self, values):
                        return predict(self.network, values)

                target = ForwardAdapter(model)
            else:
                target = model
            target.eval()
            descriptions = {}
            for spec in specs:
                html = _export_one(target, inputs, staging / spec["member"], spec["options"])
                descriptions[spec["id"]] = {
                    "id": spec["id"],
                    "label": spec["label"],
                    "member": spec["member"],
                    "path": str(output_dir / spec["member"]),
                    "graph_nodes": html.count('"node_type"'),
                }
        default = descriptions[default_view]
        record = {
            "schema_version": 1,
            "status": "succeeded",
            "path": default["path"],
            "configuration_revision": revision,
            "input_source": input_source,
            "parameter_count": sum(p.numel() for p in model.parameters()),
            "model_type": model_type or type(model).__module__ + "." + type(model).__name__,
            "graph_nodes": default["graph_nodes"],
            "graph_view": default_view,
            "default_view": default_view,
            "views": descriptions,
        }
        (staging / "model-inspection.json").write_text(
            json.dumps(record, ensure_ascii=False, allow_nan=False), encoding="utf-8"
        )
        for name in [*members, "model-inspection.json"]:
            destination = output_dir / name
            if destination.is_symlink():
                raise ValueError("graph_output_symlink")
            if destination.exists():
                destination.replace(staging / (name + ".previous"))
                previous.append(name)
            (staging / name).replace(destination)
            committed.append(name)
        return record
    except BaseException:
        for name in reversed(committed):
            (output_dir / name).unlink(missing_ok=True)
        for name in previous:
            (staging / (name + ".previous")).replace(output_dir / name)
        raise
    finally:
        shutil.rmtree(staging)


def fit_graph_viewport(html: str) -> str:
    """把 TorchVista 默认的整图塞进视口改成按宽度适配，避免深网络缩成看不见的细线。"""
    if _FIT_ENTIRE_GRAPH not in html:
        raise RuntimeError("TorchVista 结构页缺少整图缩放语句，无法改成按宽度显示")
    return html.replace(_FIT_ENTIRE_GRAPH, _FIT_WIDTH, 1).replace(_CENTER_VERTICAL, _TOP_ALIGN, 1)


def trace(
    model: torch.nn.Module,
    inputs,
    output_dir: Path,
    *,
    revision: str,
    input_source: dict,
    predict=None,
) -> dict:
    """保持正式模型参数，以真实输入执行中等体量 TorchVista 模块图并记录来源。"""
    from torchvista import trace_model

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "model.html"

    class ForwardAdapter(torch.nn.Module):
        def __init__(self, network):
            super().__init__()
            self.network = network

        def forward(self, values):
            return predict(self.network, values)

    html = ""
    with preserve_model_state(model), atomic_path(target) as temporary, redirect_stdout(sys.stderr):
        target_model = ForwardAdapter(model).eval() if predict else model.eval()
        trace_model(
            target_model,
            inputs,
            export_format="html",
            export_path=str(temporary),
            show_compressed_view=True,
            collapse_modules_after_depth=_MODULE_TRACE_DEPTH,
            forced_module_tracing_depth=_MODULE_TRACE_DEPTH,
        )
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("TorchVista 未生成结构资产")
        html = fit_graph_viewport(temporary.read_text())
        temporary.write_text(html, encoding="utf-8")
    record = {
        "schema_version": 1,
        "status": "succeeded",
        "path": str(target),
        "configuration_revision": revision,
        "input_source": input_source,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_type": type(model).__module__ + "." + type(model).__name__,
        "graph_nodes": html.count('"node_type"'),
        "graph_view": "compressed_modules",
    }
    save_json(output_dir / "model-inspection.json", record)
    return record
