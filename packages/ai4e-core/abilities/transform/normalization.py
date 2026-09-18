"""具名场的冻结变换组合与可序列化重建，不感知领域、数据集或运行目录。"""

from __future__ import annotations

import hashlib
import json

import torch

from ai4e_core.base.config import operation_record, resolve_operation

from .coordinate_normalization import CoordinateNormalization
from .minmax import MinMax
from .scale import Scale, resolve_scale
from .standardization import Standardization


class Identity:
    """显式恒等变换，不猜测字段是否需要归一化。"""

    def apply(self, value):
        return value.clone()

    def inverse(self, value):
        return value.clone()


class CheckedTransform:
    """自定义变换不能改变字段形状、实体数量或返回非有限结果。"""

    def __init__(self, transform):
        self.transform = transform

    def _call(self, method, value):
        result = getattr(self.transform, method)(value)
        if (
            not isinstance(result, torch.Tensor)
            or result.shape != value.shape
            or not torch.isfinite(result).all()
        ):
            raise ValueError(f"自定义变换 {method} 返回形状或数值非法")
        return result

    def apply(self, value):
        """保序变换同一字段。"""
        return self._call("apply", value)

    def inverse(self, value):
        """恢复同形状物理字段。"""
        return self._call("inverse", value)


class ComposedTransform:
    """先执行归一化方法，再乘场上 scale；反变换相反。"""

    def __init__(self, method, scale: Scale):
        self.method = method
        self.scale = scale

    def apply(self, value, **kwargs):
        result = self.method.apply(value, **kwargs) if kwargs else self.method.apply(value)
        return self.scale.apply(result)

    def inverse(self, value):
        return self.method.inverse(self.scale.inverse(value))


class Normalization:
    """由可序列化记录重建变换，不在反变换时访问原统计文件。"""

    def __init__(self, record: dict):
        """验证记录版本与方法，建立冻结的场变换。"""
        self._record = json.loads(json.dumps(record))
        if self.record.get("version") not in (1, 2):
            raise ValueError("不支持的归一化记录版本")
        arithmetic = "divide" if self.record["version"] == 1 else "shift_scale"
        self.transforms = {}
        for name, declaration in self.record["fields"].items():
            parameters = declaration["parameters"]
            if declaration["method"] == "custom":
                factory = resolve_operation(
                    {"target": declaration["target"], "parameters": parameters}
                )
                implementation = operation_record(factory)
                if declaration.get("implementation", implementation) != implementation:
                    raise ValueError(f"冻结变换实现已变化: {name}")
                transform = factory()
                if not callable(getattr(transform, "apply", None)) or not callable(
                    getattr(transform, "inverse", None)
                ):
                    raise TypeError("自定义变换必须实现 apply 和 inverse")
                transform = CheckedTransform(transform)
                self._record["fields"][name]["implementation"] = implementation
            elif declaration["method"] == "identity":
                transform = Identity()
            elif declaration["method"] == "zscore":
                transform = Standardization(
                    tuple(parameters["mean"]), tuple(parameters["std"]), arithmetic=arithmetic
                )
            elif declaration["method"] == "minmax":
                transform = MinMax(**parameters, arithmetic=arithmetic)
            elif declaration["method"] == "coordinate":
                transform = CoordinateNormalization(**parameters, arithmetic=arithmetic)
            else:
                raise ValueError(f"不支持的归一化方法: {declaration['method']}")
            factor = resolve_scale(declaration)
            self._record["fields"][name]["scale"] = factor
            self.transforms[name] = ComposedTransform(transform, Scale(factor))

    @property
    def record(self) -> dict:
        """返回独立副本，避免外部修改冻结参数与摘要。"""
        return json.loads(json.dumps(self._record))

    @property
    def digest(self) -> str:
        """实际参数与来源共同决定不可变准备版本。"""
        return hashlib.sha256(json.dumps(self.record, sort_keys=True).encode()).hexdigest()

    def apply(self, fields: dict[str, torch.Tensor]) -> dict[str, torch.Tensor]:
        """保留未变换字段，为声明字段创建归一化结果。"""
        result = dict(fields)
        for name, transform in self.transforms.items():
            if self._record["fields"][name].get("scope") == "condition":
                continue
            if name not in result:
                raise ValueError(f"归一化缺字段: {name}")
            result[name] = transform.apply(result[name])
        return result

    def inverse(self, name: str, value: torch.Tensor) -> torch.Tensor:
        """恢复指定场的物理值。"""
        return self.transforms[name].inverse(value)
