"""点、线、面和体空间提取业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SpatialExtraction:
    """统一描述点线面体提取；几何参数由kind对应的调用配置解释。"""

    kind: str
    field_names: tuple[str, ...]
    geometry: dict


def validate_spatial_extraction(request: SpatialExtraction) -> SpatialExtraction:
    """校验空间提取类型和字段，不在二级模块访问数据集Repository。"""

    if request.kind not in {"point", "line", "surface", "volume"}:
        raise ValueError("空间提取仅支持点、线、面和体")
    if not request.field_names:
        raise ValueError("空间提取至少选择一个字段")
    return request


def sample_positions(mesh, positions: list) -> list[dict]:
    """空间提取使用真实 VTK 单元插值，保留域外有效性。"""
    from modules.visEngine import probe
    if not positions or len(positions) > 10000 or any(len(p) != 3 for p in positions):
        raise ValueError('invalid_probe_positions')
    return probe(mesh, positions)
