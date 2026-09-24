"""具名验证窗口与物理量推理连接；固定结果保存和后处理相互独立。"""

import numpy as np
import torch

from ai4e_core.abilities.data.extract.time_windows import window_slices
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from ai4e_core.abilities.inference.execution import inference_execution
from ai4e_core.abilities.inference.timing import measure
from ai4e_core.abilities.transform.standardization import Standardization


class Predictor:
    """原始主机数组进出；正反归一化与完整预测均包含在调用边界内。"""

    def __init__(self, model, stats, advance, device):
        self.model, self.advance, self.device = model, advance, device
        self.transform = Standardization(
            tuple(stats["mean"]), tuple(stats["std"]), arithmetic="divide"
        )

    def __call__(self, values):
        if values.shape[1:] != (10, 6, 100, 100) or values.dtype != np.float32:
            raise ValueError("历史输入合同不符")
        with inference_execution(self.model, preserve_rng=False):
            x = torch.from_numpy(np.ascontiguousarray(values)).to(self.device)
            x = self.transform.apply(x.movedim(2, -1)).movedim(-1, 2)
            y = self.advance(self.model, x)
            y = self.transform.inverse(y.movedim(2, -1)).movedim(-1, 2)
            return y.cpu().numpy().copy()


class Validation:
    """训练回调与末轮评价共享完整45窗口口径，不读取隐藏测试。"""

    def __init__(self, records, stats, advance, device):
        self.records, self.stats, self.advance, self.device = records, stats, advance, device
        self.data = [
            read_arrays(r["manifest"], kind="rmhd-physical-v1")[1]["values"] for r in records
        ]
        self.curve = []

    def evaluate(self, model, *, output=None):
        """逐场 FP64 指标，保存预测时同步保存窗口身份。"""
        predict = Predictor(model, self.stats, self.advance, self.device)
        rows, predictions, targets, ids = [], [], [], []
        for record, array in zip(self.records, self.data, strict=True):
            for start in [0, 80, 161]:
                history, future = window_slices(start, 211, 10, 40)
                prediction = predict(np.array(array[history], dtype=np.float32)[None])
                target = np.array(array[future])[None]
                values = trajectory_metrics(
                    torch.from_numpy(prediction).double(),
                    torch.from_numpy(target),
                    axes=("B", "T", "C", "H", "W"),
                )["sample_component_relative_l2"][0]
                if any(v is None or not np.isfinite(v) for v in values):
                    raise ValueError("不能评价全部字段")
                rows.append(values)
                ids.append({"id": record["id"], "start": start})
                if output is not None:
                    predictions.append(prediction[0])
                    targets.append(target[0])
        result = {
            "mean_field_relative_l2": float(np.mean(rows)),
            "per_field": np.mean(rows, axis=0).tolist(),
            "rows": rows,
            "identities": ids,
        }
        if output is not None:
            result["arrays"] = save_arrays(
                output,
                {"prediction": np.stack(predictions), "target": np.stack(targets)},
                kind="rmhd-validation-predictions-v1",
                metadata={"identities": ids},
            )
        return result

    def __call__(self, index, model):
        result = self.evaluate(model)
        self.curve.append({"updates": index, **result})
        print("VALIDATION", index, result["mean_field_relative_l2"], flush=True)


def latency(predict, validation, device):
    """20次预热、3批各45窗口重复5次，返回P95中位数。"""
    inputs = [
        np.array(a[s : s + 10], dtype=np.float32)[None]
        for a in validation.data
        for s in [0, 80, 161]
    ]
    for i in range(20):
        predict(inputs[i % len(inputs)])
    batches = []
    for _ in range(3):
        times = []
        for value in inputs:
            for _ in range(5):
                with measure(device) as timing:
                    predict(value)
                times.append(timing["seconds"])
        batches.append(times)
    p95s = [float(np.percentile(times, 95)) for times in batches]
    return {
        "p95_seconds": float(np.median(p95s)),
        "batch_p95_seconds": p95s,
        "samples_seconds": batches,
        "warmup": 20,
    }
