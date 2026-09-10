"""AB-UPT 有序域、字段及 token 输入契约，不依赖框架配置系统。"""

import re
from copy import deepcopy


class DomainLayout:
    """冻结模型布局；域和字段顺序参与模型结构版本。"""

    def __init__(self, data_specs, geometry_conditioning_dims=None):
        self.spec = deepcopy(data_specs)
        if self.spec.get("position_dim") != 3 or not self.spec.get("domains"):
            raise ValueError("需要三维坐标和非空域声明")
        self.domains = tuple(self.spec["domains"])
        self.outputs, self.features = {}, {}
        names = set()
        for domain, spec in self.spec["domains"].items():
            self._name(domain)
            outputs = self._dims(spec.get("output_dims", {}))
            if not outputs:
                raise ValueError("每域必须声明预测字段")
            self.outputs[domain] = outputs
            self.features[domain] = self._dims(spec.get("feature_dim") or {})
            for field, _ in outputs:
                for name in (f"{domain}_{field}", f"query_{domain}_{field}"):
                    if name in names:
                        raise ValueError("域与字段生成的输出名称冲突")
                    names.add(name)
        self.conditions = self._dims(self.spec.get("conditioning_dims") or {})
        self.inherit_geometry = geometry_conditioning_dims is None
        self.geometry_conditions = (
            self.conditions if self.inherit_geometry else self._dims(geometry_conditioning_dims)
        )
        self.signature = (
            self.domains,
            tuple(self.outputs.items()),
            tuple(self.features.items()),
            self.conditions,
            self.geometry_conditions,
            self.inherit_geometry,
        )

    @staticmethod
    def _name(name):
        if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
            raise ValueError("域和字段名称必须为非空字母数字下划线标识")

    @classmethod
    def _dims(cls, values):
        if not isinstance(values, dict):
            raise TypeError("字段维数必须为有序映射")
        for name, width in values.items():
            cls._name(name)
            if type(width) is not int or width <= 0:
                raise ValueError("字段通道数必须为正整数")
        return tuple(values.items())

    def split(self, domain, tensor, *, query=False):
        """按冻结字段顺序切片为标准预测名称。"""
        result, offset = {}, 0
        for name, width in self.outputs[domain]:
            key = f"{'query_' if query else ''}{domain}_{name}"
            result[key] = tensor[..., offset : offset + width]
            offset += width
        return result
