"""物理场图片装配，颜色范围和相机作为显式产物信息返回。"""

from __future__ import annotations

import json
from typing import Any

from ai4e_core.abilities.postproc.visualization import render_field as render
from ai4e_core.abilities.postproc.visualization import render_profile as curve
from ai4e_core.abilities.postproc.visualization.fields import field_values

from .field_analysis import mesh_field


def render_field(
    mesh: Any,
    *,
    field: str,
    component: str | int = "scalar",
    operation: Any = None,
    **settings: Any,
) -> dict:
    """领域字段绘图；默认预测/真值共范围，误差另用非负或对称范围。"""
    name = mesh_field(mesh, field)
    metadata = {}
    if settings.get("camera") == "normal":
        transform = json.loads(str(mesh.field_data["post_transform"][0]))
        settings.setdefault("normal", transform["normal"])
    if "clim" not in settings and name.endswith((".prediction", ".truth")):
        key = name.rsplit(".", 1)[0]
        if key + ".truth" in mesh.point_data:
            p = field_values(mesh, key + ".prediction", component=component)
            t = field_values(mesh, key + ".truth", component=component)
            settings["clim"] = [float(min(p.min(), t.min())), float(max(p.max(), t.max()))]
    if name.endswith((".absolute_error", ".vector_error", ".difference", ".magnitude_difference")):
        settings.setdefault("cmap", "magma")
    if "post_units" in mesh.field_data and len(name.split(".")) >= 2:
        settings.setdefault(
            "unit", json.loads(str(mesh.field_data["post_units"][0])).get(name.split(".")[1])
        )
    pixels = (operation or render)(
        mesh, field=name, component=component, metadata=metadata, **settings
    )
    from ai4e_core.base.config import operation_record

    if operation is not None:
        metadata["operation"] = operation_record(operation)
    return {"pixels": pixels, "parameters": metadata}


def render_profile(profile: dict, *, field: str, operation: Any = None, **settings: Any) -> dict:
    """剖面曲线及其字段选择说明。"""
    pixels = (operation or curve)(profile, field=field, **settings)
    from omegaconf import OmegaConf

    return {
        "pixels": pixels,
        "parameters": {
            "field": field,
            **OmegaConf.to_container(OmegaConf.create(settings), resolve=True),
        },
    }
