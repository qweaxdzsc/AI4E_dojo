"""普通代理状态重建、POD 物理场解码与固定结果交付。"""

from copy import deepcopy
from functools import partial

import numpy as np

from ai4e_core.abilities.data.save.array_manifest import save_arrays
from ai4e_core.abilities.inference.callable_prediction import predict_batches

from .preparation import read_pod, read_prepared


class IndependentKriging:
    """局部多输出连接；每列独立后验，不构造虚假的目标间协方差。"""

    def __init__(self, state):
        from ai4e_core.abilities.modeling.models.kriging import Kriging

        if (
            state.get("kind") != "independent-kriging-v1"
            or state["output_dim"] < 1
            or len(state["models"]) != state["output_dim"]
        ):
            raise ValueError("多目标克里金状态不一致")
        self.state = deepcopy(state)
        self.models = [Kriging.from_state(part) for part in state["models"]]

    def predict(self, x, *, return_variance=False):
        """输出 [N,q] 均值，按需附 [N,q] 独立边际方差。"""
        if np.asarray(x).ndim != 2 or np.asarray(x).shape[1] != self.state["input_dim"]:
            raise ValueError("克里金输入维度不符")
        if return_variance:
            columns = [model.predict(x, return_variance=True) for model in self.models]
            return tuple(np.column_stack([part[i] for part in columns]) for i in (0, 1))
        return np.column_stack([model.predict(x) for model in self.models])

    def get_state(self):
        """返回独立的完整多目标状态。"""
        return deepcopy(self.state)


def rebuild(state):
    """按本应用明确支持的状态重建普通对象，不动态执行任意类路径。"""
    kind = state.get("kind")
    if kind == "rsm-v1":
        from ai4e_core.abilities.modeling.models.rsm import ResponseSurface

        return ResponseSurface.from_state(state)
    if kind == "rbf-v1":
        from ai4e_core.abilities.modeling.models.rbf import RBFInterpolator

        return RBFInterpolator.from_state(state)
    if kind == "independent-kriging-v1":
        return IndependentKriging(state)
    if kind == "lightgbm":
        from ai4e_core.abilities.modeling.models.lightgbm import LightGBMPredictor

        return LightGBMPredictor.from_state(state)
    raise ValueError(f"本应用不支持拟合状态: {kind}")


def predict_prepared(state, prepared, output, *, split="test", batch_size=256, predictor=None):
    """读取准备并预测，反变换后交付 classic-results-v1 供固定 post 评价。

    普通批量入口只沿真实样本轴切分。POD 解码只读取准备自身的固定基，不回读
    原 HDF5 或旧准备目录；本函数不拟合，也不调用神经模型 eval/to 等接口。
    predictor 可为调用方由普通状态重建的对象，无需添加框架注册条目。
    """
    record, arrays = read_prepared(prepared, split)
    metadata = deepcopy(record["metadata"])
    model = rebuild(state) if predictor is None else predictor
    variance = None
    if state.get("kind") == "independent-kriging-v1":
        fitted, variance = predict_batches(
            arrays["input"], partial(model.predict, return_variance=True), batch_size=batch_size
        )
        if variance.shape != arrays["target"].shape or (variance < 0).any():
            raise ValueError("克里金边际方差布局或符号非法")
    else:
        fitted = predict_batches(arrays["input"], model.predict, batch_size=batch_size)
    if fitted.shape != arrays["target"].shape:
        raise ValueError("代理输出与准备拟合目标维度不符")
    stats = metadata["statistics"]["target"]
    if metadata["case"] == "double_cylinder_pod":
        pod, context = read_pod(prepared)
        if (
            context["fields"] != metadata["fields"]
            or context["units"] != metadata["units"]
            or context["statistics"] != stats
            or context["field_shape"] != metadata["field_shape"]
        ):
            raise ValueError("冻结 POD 与准备场语义不一致")
        normalized = pod.decode(fitted).reshape(len(fitted), *metadata["field_shape"])
    elif metadata["case"] == "nasa_global":
        normalized = fitted[:, None, :]
    else:
        raise ValueError("未知代理准备案例")
    physical = normalized * np.asarray(stats["scale"]) + np.asarray(stats["mean"])
    if physical.shape != arrays["physical_target"].shape:
        raise ValueError("预测物理场布局不符")
    valid = np.asarray(arrays["valid"], dtype=bool)
    physical[~valid] = 0
    payload = {
        "prediction": physical,
        "target": arrays["physical_target"],
        "valid": valid,
        "entity_ids": arrays["entity_ids"],
        "physical_input": arrays["physical_input"],
    }
    if "times" in arrays:
        payload["times"] = arrays["times"]
    if variance is not None:
        if metadata["case"] == "nasa_global":
            payload["latent_variance"] = variance[:, None, :] * np.asarray(stats["scale"]) ** 2
            metadata["uncertainty"] = {
                "array": "latent_variance",
                "fields": metadata["fields"],
                "units": [f"({unit})^2" for unit in metadata["units"]],
                "space": "physical response",
                "scope": "independent target latent marginal variance; excludes observation noise",
            }
        else:
            payload["coefficient_latent_variance"] = variance
            metadata["uncertainty"] = {
                "array": "coefficient_latent_variance",
                "axes": ["sample", "pod_coefficient"],
                "units": "normalized POD coefficient squared",
                "scope": "independent coefficient latent variance; not joint physical field covariance",
            }
    metadata["derived"] = {}
    return save_arrays(output, payload, kind="classic-results-v1", metadata=metadata)
