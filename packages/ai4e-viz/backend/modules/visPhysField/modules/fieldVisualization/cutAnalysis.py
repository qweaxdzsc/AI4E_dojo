"""切面、流线、等值面和等高线分析业务对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaneDefinition:
    """用原点和法向量定义切面，坐标单位继承数据集。"""

    origin: tuple[float, float, float]
    normal: tuple[float, float, float]


def validate_plane(plane: PlaneDefinition) -> PlaneDefinition:
    """禁止零法向量，因为它无法定义有效切面。"""

    if all(component == 0 for component in plane.normal):
        raise ValueError("切面法向量不能为零")
    return plane


def execute_analysis(mesh, node: dict, seed_mesh=None):
    """共享完整网格执行切面、流线及等值分析。"""
    from modules.visEngine import apply_filter
    if node['type'] == 'slice':
        params = node.get('parameters', {})
        validate_plane(PlaneDefinition(tuple(params.get('origin', [0,0,0])), tuple(params.get('normal', [1,0,0]))))
    return apply_filter(mesh, node, seed_mesh)
