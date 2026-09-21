"""VTK 单元场转点场；不覆盖来源网格及原字段。"""

import numpy as np


def cell_fields_to_points(mesh, names: tuple[str, ...]):
    """按 VTK 相邻单元平均转点，返回值及原点/单元身份。"""
    work = mesh.copy(deep=True)
    point_ids = np.asarray(work.point_data.get("ai4e_point_id", np.arange(work.n_points))).copy()
    cell_ids = np.asarray(work.cell_data.get("ai4e_cell_id", np.arange(work.n_cells))).copy()
    values = {name: np.asarray(work.cell_data[name]).copy() for name in names}
    work.clear_data()
    for name, value in values.items():
        work.cell_data[name] = value
    converted = work.cell_data_to_point_data(pass_cell_data=True)
    if not np.array_equal(converted.points, mesh.points) or converted.n_cells != mesh.n_cells:
        raise ValueError("转换改变拓扑身份")
    return (
        {name: np.asarray(converted.point_data[name]).copy() for name in names},
        point_ids,
        cell_ids,
    )
