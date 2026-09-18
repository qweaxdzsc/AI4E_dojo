"""导出当前任务正式 AB-UPT，供 Netron / Model Explorer 本地查看。"""

from __future__ import annotations

import json
import traceback
from pathlib import Path

import torch

from ai4e_core.applications.aero_cfd.inspection import _components, normalize_config

OUT = Path("/Users/zonghui/work/project_simulation/dojo_train/model-viewers")
CFG = Path("/tmp/abupt-task-config.json")


class ForwardAdapter(torch.nn.Module):
    def __init__(self, network, predict):
        super().__init__()
        self.network = network
        self.predict = predict

    def forward(
        self,
        geometry_position,
        geometry_supernode_idx,
        geometry_batch_idx,
        surface_anchor,
        volume_anchor,
        surface_query,
        volume_query,
    ):
        return self.predict(
            self.network,
            {
                "geometry_position": geometry_position,
                "geometry_supernode_idx": geometry_supernode_idx,
                "geometry_batch_idx": geometry_batch_idx,
                "domain_anchor_positions": {
                    "surface": surface_anchor,
                    "volume": volume_anchor,
                },
                "domain_query_positions": {
                    "surface": surface_query,
                    "volume": volume_query,
                },
            },
        )


def describe(value, prefix="inputs"):
    if torch.is_tensor(value):
        return {prefix: [list(value.shape), str(value.dtype)]}
    if isinstance(value, dict):
        out = {}
        for key, child in value.items():
            out.update(describe(child, f"{prefix}.{key}"))
        return out
    return {prefix: type(value).__name__}


def dummy_inputs():
    """保持正式网络结构，只用很小的真实形状输入，方便导出和浏览。"""
    return {
        "geometry_position": torch.rand(48, 3),
        "geometry_supernode_idx": torch.arange(12, dtype=torch.long),
        "geometry_batch_idx": torch.zeros(48, dtype=torch.long),
        "domain_anchor_positions": {
            "surface": torch.rand(1, 16, 3),
            "volume": torch.rand(1, 16, 3),
        },
        "domain_query_positions": {
            "surface": torch.rand(1, 8, 3),
            "volume": torch.rand(1, 8, 3),
        },
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    captured = json.loads(CFG.read_text())
    config = normalize_config(captured["config"])
    _, model = _components(config)
    network = model.construct(**model.training_parameters(config)).cpu().eval()
    adapter = ForwardAdapter(network, model.predict).eval()
    packed = dummy_inputs()
    inputs = (
        packed["geometry_position"],
        packed["geometry_supernode_idx"],
        packed["geometry_batch_idx"],
        packed["domain_anchor_positions"]["surface"],
        packed["domain_anchor_positions"]["volume"],
        packed["domain_query_positions"]["surface"],
        packed["domain_query_positions"]["volume"],
    )
    params = sum(p.numel() for p in network.parameters())
    print("MODEL", type(network).__name__, "params", params)
    print("INPUTS", describe(packed))
    with torch.no_grad():
        preview = adapter(*inputs)
    print("FORWARD", describe(preview, "output"))

    report = {
        "params": params,
        "model_type": type(network).__module__ + "." + type(network).__name__,
        "revision": captured.get("revision"),
        "parameters": config["model"]["parameters"],
        "inputs": describe(packed),
        "exports": {},
    }

    try:
        exported = torch.export.export(adapter, inputs, strict=False)
        pt2 = OUT / "abupt.pt2"
        torch.export.save(exported, pt2)
        report["exports"]["pt2"] = str(pt2)
        print("EXPORT_PT2", pt2, pt2.stat().st_size)
    except Exception as exc:
        report["exports"]["pt2_error"] = f"{type(exc).__name__}: {exc}"
        print("EXPORT_PT2_FAIL", type(exc).__name__, exc)
        traceback.print_exc()

    try:
        traced = torch.jit.trace(adapter, inputs, strict=False, check_trace=False)
        pt = OUT / "abupt.torchscript.pt"
        traced.save(str(pt))
        report["exports"]["torchscript"] = str(pt)
        print("EXPORT_TS", pt, pt.stat().st_size)
    except Exception as exc:
        report["exports"]["torchscript_error"] = f"{type(exc).__name__}: {exc}"
        print("EXPORT_TS_FAIL", type(exc).__name__, exc)
        traceback.print_exc()

    try:
        onnx_path = OUT / "abupt.onnx"
        torch.onnx.export(
            adapter,
            inputs,
            onnx_path,
            dynamo=False,
            opset_version=17,
            input_names=[
                "geometry_position",
                "geometry_supernode_idx",
                "geometry_batch_idx",
                "surface_anchor",
                "volume_anchor",
                "surface_query",
                "volume_query",
            ],
        )
        report["exports"]["onnx"] = str(onnx_path)
        print("EXPORT_ONNX", onnx_path, onnx_path.stat().st_size)
    except Exception as exc:
        report["exports"]["onnx_error"] = f"{type(exc).__name__}: {exc}"
        print("EXPORT_ONNX_FAIL", type(exc).__name__, exc)
        traceback.print_exc()

    (OUT / "export-report.json").write_text(json.dumps(report, indent=2, default=str))
    tree = []
    for name, module in network.named_modules():
        children = list(module._modules)
        params = sum(p.numel() for p in module.parameters(recurse=False))
        tree.append(
            {
                "name": name or type(module).__name__,
                "type": type(module).__name__,
                "own_params": params,
                "children": children,
            }
        )
    (OUT / "modules.json").write_text(json.dumps(tree, indent=2))
    print("REPORT", OUT / "export-report.json")
    print("MODULES", len(tree))


if __name__ == "__main__":
    main()
