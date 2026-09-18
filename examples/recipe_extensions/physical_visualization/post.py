"""独立可复制扩展：读取固定物理结果、替换绘图并保存新增字段。"""

from pathlib import Path

import numpy as np
from custom_render import render_with_edges

from ai4e_core.applications.aero_cfd import post as analysis


def post(reference, *, output):
    """输入固定样本清单；原始网格需已由推理交付。"""
    fields = analysis.read_fields(reference)
    mesh = analysis.bind_mesh(fields, domain="volume")
    # 研究者显式加入新字段；保存后独立读回，验证下游能消费。
    mesh.point_data["speed_squared"] = np.sum(
        mesh.point_data["volume.velocity.prediction"] ** 2, axis=1
    )
    image = analysis.render_field(
        mesh, field="speed_squared", operation=render_with_edges, size=(640, 480)
    )
    report = analysis.save_sample(
        fields, meshes={"custom_volume": mesh}, images={"custom_speed": image}, output=output
    )
    import pyvista as pv

    restored = pv.read(Path(report["manifest"]).parent / "fields/custom_volume.vtu")
    np.testing.assert_array_equal(restored["speed_squared"], mesh["speed_squared"])
    return report


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("manifest")
    parser.add_argument("output")
    arguments = parser.parse_args()
    print(post(arguments.manifest, output=arguments.output)["manifest"])
