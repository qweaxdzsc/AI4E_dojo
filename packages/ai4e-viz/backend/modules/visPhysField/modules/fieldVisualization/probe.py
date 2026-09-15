"""Probe点选和采样业务规则。"""


def probe_position(x: float, y: float, z: float) -> tuple[float, float, float]:
    """生成三维Probe坐标；坐标系和单位继承当前数据集。"""

    return float(x), float(y), float(z)
