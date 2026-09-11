"""JSON 传输缺失值规则：非有限统计显示为空，不改变运行事实。"""

import math

from fastapi.responses import JSONResponse


def finite_values(value):
    """递归保留普通数值，NaN/Infinity 作为未有有限结果传输。"""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: finite_values(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_values(child) for child in value]
    return value


class FiniteJSONResponse(JSONResponse):
    """兼容原始产物中的无最优值哨兵，不重写产物。"""

    def render(self, content):
        """将响应映射为标准 JSON。"""
        return super().render(finite_values(content))
