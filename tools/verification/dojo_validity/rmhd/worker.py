"""无真值推理工作进程；仅载入冻结提交，通信使用固定数值共享数组。"""

import argparse
import importlib.util
import json
import sys
import types
from pathlib import Path

import numpy as np
import torch


def loaded_models(predict):
    """在隔离worker内遍历预测闭包中的模块；不在可信评分器载入候选。"""
    seen, modules, parameters = set(), [], {}

    def visit(value, depth=0):
        if id(value) in seen or depth > 30:
            return
        seen.add(id(value))
        if isinstance(value, torch.nn.Module):
            modules.append(type(value).__module__ + "." + type(value).__qualname__)
            for p in value.parameters():
                parameters[id(p)] = (p.numel(), p.requires_grad)
        elif isinstance(value, types.FunctionType):
            for cell in value.__closure__ or ():
                try:
                    visit(cell.cell_contents, depth + 1)
                except ValueError:
                    pass
        elif isinstance(value, dict):
            for item in value.values():
                visit(item, depth + 1)
        elif isinstance(value, (list, tuple)):
            for item in value:
                visit(item, depth + 1)

    visit(predict)
    return {
        "module_classes": modules,
        "total_parameter_count": sum(n for n, _ in parameters.values()) if modules else None,
        "trainable_parameter_count_at_inference": sum(n for n, flag in parameters.values() if flag)
        if modules
        else None,
        "scope": "reachable nn.Modules in frozen prediction function closures; custom opaque callables may be unobserved",
    }


def main():
    """load(assets)->predict(history)；父进程计时，候选无法改写可信时钟。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--exchange", type=Path, required=True)
    args = parser.parse_args()
    torch.set_num_threads(6)
    torch.manual_seed(42)
    if not torch.backends.mps.is_available():
        raise RuntimeError("隔离工作进程 MPS 不可用")
    manifest = json.loads((args.candidate / "submission.json").read_text())
    entry = (args.candidate / manifest["entrypoint"]).resolve()
    if not entry.is_relative_to(args.candidate.resolve()):
        raise ValueError("提交入口越界")
    sys.path.insert(0, str(args.candidate))
    spec = importlib.util.spec_from_file_location("candidate", entry)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    predict = module.load(args.candidate)
    model_info = loaded_models(predict)
    inputs = np.load(args.exchange / "input.npy", mmap_mode="r", allow_pickle=False)
    output = np.load(args.exchange / "output.npy", mmap_mode="r+", allow_pickle=False)
    (args.exchange / "tmp/model-info.json").write_text(json.dumps(model_info))
    print("RMHD_READY", flush=True)
    for line in sys.stdin:
        request = json.loads(line)["request"]
        torch.mps.synchronize()
        prediction = np.asarray(predict(np.array(inputs, copy=True)))
        torch.mps.synchronize()
        if (
            prediction.shape != output.shape
            or prediction.dtype.kind != "f"
            or not np.isfinite(prediction).all()
        ):
            raise ValueError("非法预测形状、类型或非有限值")
        output[:] = prediction
        print("RMHD_DONE " + str(request), flush=True)


if __name__ == "__main__":
    main()
