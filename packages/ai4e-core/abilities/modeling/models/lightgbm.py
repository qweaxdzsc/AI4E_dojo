"""官方LightGBM普通预测对象：有序多响应组合与原生状态读取。"""

from __future__ import annotations

import importlib
from copy import deepcopy
from typing import Any

import numpy as np


def _backend():
    try:
        return importlib.import_module("lightgbm")
    except ImportError as error:
        raise ImportError("显式使用LightGBM需要安装ai4e-core[boosting]可选依赖") from error


def _names(values, count: int, label: str) -> list[str]:
    result = list(values)
    if (
        len(result) != count
        or len(set(result)) != count
        or any(not isinstance(v, str) or not v.strip() for v in result)
    ):
        raise ValueError(f"{label}须为{count}个唯一非空名称")
    return result


class LightGBMPredictor:
    """每个目标一个官方回归Booster；预测输出始终为[N,Q]。

    输入只接有限连续数值特征，列次序由调用方按feature_names显式保持。
    不继承nn.Module，不提供梯度或概率方差。构造/读取不建树。
    """

    def __init__(
        self,
        *,
        model_strings,
        feature_names,
        target_names,
        params: dict,
        training_digest: str,
        backend_version: str,
    ) -> None:
        texts = list(model_strings)
        if not texts or any(not isinstance(s, str) or not s.strip() for s in texts):
            raise ValueError("须提供每个目标的完整原生模型文本")
        features = list(feature_names)
        if not features:
            raise ValueError("特征次序不得为空")
        self.feature_names = tuple(_names(features, len(features), "特征名"))
        self.target_names = tuple(_names(target_names, len(texts), "目标名"))
        if (
            not isinstance(training_digest, str)
            or len(training_digest) != 64
            or any(c not in "0123456789abcdef" for c in training_digest)
        ):
            raise ValueError("训练数组身份须为sha256摘要")
        if not isinstance(params, dict):
            raise TypeError("有效训练参数须为字典")
        backend = _backend()
        if backend.__version__ != backend_version:
            raise ValueError("读取或接续必须使用保存模型相同的LightGBM版本")
        models = [backend.Booster(model_str=value) for value in texts]
        for model in models:
            if model.num_feature() != len(features) or model.feature_name() != features:
                raise ValueError("原生模型特征数或次序与状态不一致")
            if model.num_model_per_iteration() != 1 or model.current_iteration() <= 0:
                raise ValueError("只接收已建树的单输出回归模型")
            objective = str(model.dump_model().get("objective", "")).split()
            if not objective or objective[0] != "regression":
                raise ValueError("原生模型的实际目标须为平方误差回归，不能仅凭元信息改名")
        self._models = models
        self._params = deepcopy(params)
        self.training_digest, self.backend_version = training_digest, backend_version

    @property
    def params(self) -> dict:
        """返回冻结有效参数的副本。"""
        return deepcopy(self._params)

    @property
    def iterations(self) -> tuple[int, ...]:
        """返回每个目标实际完成的原生轮次，不用请求轮次代替。"""
        return tuple(model.current_iteration() for model in self._models)

    def predict(self, x: Any) -> np.ndarray:
        """按冻结特征次序输入[N,D]，返回冻结目标次序的[N,Q]预测。"""
        raw = np.asarray(x)
        if (
            raw.dtype.kind not in "fiu"
            or raw.ndim != 2
            or not len(raw)
            or raw.shape[1] != len(self.feature_names)
        ):
            raise ValueError("预测特征须为非空[N,D]有限实数数组且维数匹配")
        points = np.asarray(raw, dtype=np.float64)
        if not np.isfinite(points).all():
            raise ValueError("预测特征非有限；未启用隐式缺失值处理")
        prediction = np.column_stack(
            [
                model.predict(
                    points,
                    num_iteration=model.current_iteration(),
                    num_threads=int(self._params.get("num_threads", 1)),
                )
                for model in self._models
            ]
        )
        if not np.isfinite(prediction).all():
            raise FloatingPointError("提升树预测非有限")
        return prediction

    def get_state(self) -> dict:
        """交付模型文本、字段次序和接续元信息，不写文件或使用pickle。"""
        return {
            "kind": "lightgbm",
            "version": 1,
            "feature_names": list(self.feature_names),
            "target_names": list(self.target_names),
            "params": self.params,
            "training_digest": self.training_digest,
            "backend_version": self.backend_version,
            "iterations": list(self.iterations),
            "model_strings": [
                m.model_to_string(num_iteration=m.current_iteration()) for m in self._models
            ],
        }

    @classmethod
    def from_state(cls, state: dict) -> LightGBMPredictor:
        """严格版本/字段/模型次序读取；只恢复预测与原生轮次追加能力。"""
        keys = {
            "kind",
            "version",
            "feature_names",
            "target_names",
            "params",
            "training_digest",
            "backend_version",
            "iterations",
            "model_strings",
        }
        if (
            set(state) != keys
            or state["kind"] != "lightgbm"
            or type(state["version"]) is not int
            or state["version"] != 1
        ):
            raise ValueError("提升树状态字段或版本不符")
        model = cls(**{key: state[key] for key in keys - {"kind", "version", "iterations"}})
        if list(model.iterations) != state["iterations"]:
            raise ValueError("原生轮次与状态记录不一致")
        return model
