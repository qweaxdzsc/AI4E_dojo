"""真实模型结构跟踪；仅成功前向的完整 HTML 可以原子发布。"""

import sys
from contextlib import redirect_stdout
from pathlib import Path

import torch

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.inference.randomness import preserve_randomness


def trace(
    model: torch.nn.Module,
    inputs,
    output_dir: Path,
    *,
    revision: str,
    input_source: dict,
    predict=None,
) -> dict:
    """保持正式模型参数，以真实输入执行 TorchVista 并记录来源。"""
    from torchvista import trace_model

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "model.html"

    class ForwardAdapter(torch.nn.Module):
        def __init__(self, network):
            super().__init__()
            self.network = network

        def forward(self, values):
            return predict(self.network, values)

    target_model = ForwardAdapter(model).eval() if predict else model.eval()
    with preserve_randomness(), atomic_path(target) as temporary, redirect_stdout(sys.stderr):
        trace_model(target_model, inputs, export_format="html", export_path=str(temporary))
        if not temporary.is_file() or temporary.stat().st_size == 0:
            raise RuntimeError("TorchVista 未生成结构资产")
    record = {
        "schema_version": 1,
        "status": "succeeded",
        "path": str(target),
        "configuration_revision": revision,
        "input_source": input_source,
        "parameter_count": sum(p.numel() for p in model.parameters()),
        "model_type": type(model).__module__ + "." + type(model).__name__,
    }
    save_json(output_dir / "model-inspection.json", record)
    return record
