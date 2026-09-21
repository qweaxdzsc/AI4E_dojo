"""完整结构在固定输入下逐层、梯度及更新对照，容差不可调宽。"""

from __future__ import annotations

import json
from pathlib import Path

import torch

from .reference import load_reference


def compare(config, inputs):
    """同一初态的独立原定义与移植模型对照，返回最大偏差。"""
    from ai4e_contrib.ability.model.geotransolver import GeoTransolver

    reference = load_reference().GeoTransolver(**config)
    migrated = GeoTransolver(**config)
    migrated.load_state_dict(reference.state_dict(), strict=True)
    observed = [{}, {}]
    handles = []
    for i, model in enumerate((reference, migrated)):
        for name, block in model.named_modules():
            if name.startswith("blocks.") and name.count(".") == 1:

                def capture(_m, _x, y, *, key=name, index=i):
                    observed[index][key] = y[0].detach().clone()

                handles.append(block.register_forward_hook(capture))
    a, b = reference(**inputs), migrated(**inputs)
    differences = {"prediction": float((a - b).abs().max().detach())}
    torch.testing.assert_close(a, b, atol=1e-6, rtol=1e-5)
    for key in observed[0]:
        torch.testing.assert_close(observed[0][key], observed[1][key], atol=1e-6, rtol=1e-5)
    a.square().mean().backward()
    b.square().mean().backward()
    differences["gradient"] = 0.0
    for (name, p), (other, q) in zip(
        reference.named_parameters(), migrated.named_parameters(), strict=True
    ):
        assert name == other
        assert (p.grad is None) == (q.grad is None), name
        if p.grad is not None:
            torch.testing.assert_close(p.grad, q.grad, atol=1e-6, rtol=1e-5, msg=name)
            differences["gradient"] = max(
                differences["gradient"], float((p.grad - q.grad).abs().max())
            )
    for model in (reference, migrated):
        matrix = [p for p in model.parameters() if p.ndim == 2]
        other = [p for p in model.parameters() if p.ndim != 2]
        torch.optim.Muon(matrix, lr=1e-3, adjust_lr_fn="match_rms_adamw").step()
        torch.optim.AdamW(other, lr=1e-3).step()
    differences["updated_weight"] = 0.0
    for name, value in reference.state_dict().items():
        actual = migrated.state_dict()[name]
        torch.testing.assert_close(value, actual, atol=1e-6, rtol=1e-5, msg=name)
        differences["updated_weight"] = max(
            differences["updated_weight"], float((value - actual).abs().max())
        )
    for handle in handles:
        handle.remove()
    return differences


if __name__ == "__main__":
    torch.set_num_threads(4)
    torch.manual_seed(42)
    x = torch.randn(1, 81, 3)
    result = {
        "darcy": compare(
            {
                "functional_dim": 3,
                "out_dim": 1,
                "geometry_dim": 3,
                "n_layers": 4,
                "n_hidden": 128,
                "n_head": 4,
                "slice_num": 64,
                "structured_shape": (9, 9),
            },
            {"local_embedding": x, "geometry": x},
        )
    }
    x = torch.randn(1, 64, 3)
    result["bumper"] = compare(
        {
            "functional_dim": 3,
            "out_dim": 50,
            "geometry_dim": 3,
            "global_dim": 3,
            "n_layers": 6,
            "n_hidden": 256,
            "n_head": 8,
            "slice_num": 128,
            "include_local_features": True,
        },
        {
            "local_embedding": x,
            "local_positions": x,
            "geometry": x,
            "global_embedding": torch.randn(1, 1, 3),
        },
    )
    path = Path(
        "/Users/zonghui/work/project_simulation/dojo_train/geotransolver/implementation/operator-comparison.json"
    )
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))
