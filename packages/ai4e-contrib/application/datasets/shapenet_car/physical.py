"""现有汽车物理 PT 的逻辑布局适配；不改写原张量。"""

from ai4e_core.abilities.data.source.physical import PhysicalView

LAYOUT = {
    "domains": {
        "surface": {
            "position": "surface_position",
            "fields": {"pressure": "surface_pressure", "normals": "surface_normals"},
        },
        "volume": {
            "position": "volume_position",
            "fields": {
                "velocity": "volume_velocity",
                "distance": "volume_sdf",
                "normals": "volume_normals",
            },
        },
    },
    "conditions": {},
}


def open_physical(config: dict) -> PhysicalView:
    """按产物清单读取旧文件映射，行身份保持为 artifact 而非虚构原 ID。"""
    path = (config.get("train") or {}).get("manifest")
    if not path:
        raise ValueError("train.manifest: 需要已有物理数据清单")
    return PhysicalView(path, layout=LAYOUT)


def comparison_mesh(config: dict, sample: str, domain: str, points):
    """数据集解释原始表面和体积文件名；不承担切面或渲染。"""
    from pathlib import Path

    from ai4e_core.abilities.data.source.adapter.vtk import load

    filenames = {"surface": "quadpress_smpl.vtk", "volume": "hexvelo_smpl.vtk"}
    return load(Path(config["dataset"]["root"]) / sample / filenames[domain])


def comparison_metadata(config, sample, domain):
    """提供来源拓扑身份与已知物理单位，未知单位不猜测。"""
    from pathlib import Path

    from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint

    filename = "quadpress_smpl.vtk" if domain == "surface" else "hexvelo_smpl.vtk"
    path = Path(config["dataset"]["root"]) / sample["identity"]["sample"] / filename
    units = {}
    units.update(config["dataset"].get("field_units", {}))
    if not path.is_file():
        return {"topology": None, "entity_set": None, "units": units}
    topology = file_fingerprint(path)
    return {
        "topology": topology,
        "entity_set": fingerprint(
            {"path": str(path.resolve()), "sample": sample["identity"]["sample"], "domain": domain}
        ),
        "units": units,
    }


def inference_fields() -> dict:
    """返回本数据集真实物理量的显示和分量说明。"""
    return {'surface_pressure': {'label': 'Pressure', 'components': 1, 'category': '流体'}, 'volume_velocity': {'label': 'Velocity', 'components': 3, 'component_labels': ['U', 'V', 'W'], 'category': '流体'}}
