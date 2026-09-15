"""将已提交预测按原点身份回贴真实来源拓扑，单独记录网格交付。"""

import json
from pathlib import Path

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.data.save.store import load_named_tensor
from ai4e_core.abilities.postproc.comparison import attach_valid_mesh, surface
from ai4e_core.abilities.postproc.coordinate_space import coordinate_space


def export_prediction_meshes(config, dataset_component, manifest_path, *, committed=None):
    """逐域写真实 VTP/VTU；失效点单元不补零，成功路径才登记到清单。"""
    import vtk

    manifest_path = Path(manifest_path)
    metadata = json.loads(manifest_path.read_text())
    root = manifest_path.parent
    result = metadata.setdefault("meshes", {})

    def read(name):
        filename = Path(metadata["filemap"][name])
        if filename.name != str(filename):
            raise ValueError("预测成员路径越界")
        return load_named_tensor(root / filename).numpy()

    for domain, declaration in metadata["domains"].items():
        space = coordinate_space(declaration.get("coordinate_space"))
        points = read(declaration["position"])
        ids = read(declaration["ids"])
        fields = {
            key + suffix: read(key + suffix)
            for key in declaration["targets"].values()
            for suffix in (".prediction", ".truth")
        }
        fields.update({d["field"]: read(d["field"]) for d in declaration.get("derived_fields", {}).values()})
        original = dataset_component.comparison_mesh(
            config, metadata["identity"]["sample"], domain, points
        )
        mapped = attach_valid_mesh(
            original,
            points,
            fields,
            source_ids=ids if declaration["identity_basis"] == "source" else None,
        )
        output = surface(mapped) if domain == "surface" else mapped
        if space is not None:
            for key, value in space.items():
                array = vtk.vtkStringArray()
                array.SetName("coordinate_space_" + key)
                array.InsertNextValue(value)
                output.GetFieldData().AddArray(array)
        filename = domain + (".vtp" if domain == "surface" else ".vtu")
        destination = root / filename
        with atomic_path(destination) as temporary:
            writer = (
                vtk.vtkXMLPolyDataWriter()
                if domain == "surface"
                else vtk.vtkXMLUnstructuredGridWriter()
            )
            writer.SetFileName(str(temporary))
            writer.SetInputData(output)
            writer.SetDataModeToAppended()
            if writer.Write() != 1 or not temporary.stat().st_size:
                raise OSError(f"真实预测网格写出失败: {destination}")
        result[domain] = {
            "path": filename,
            "point_count": output.GetNumberOfPoints(),
            "cell_count": output.GetNumberOfCells(),
            "fields": list(fields),
            "point_ids": "original_point_id",
            "cell_ids": "original_cell_id",
            "association": "point",
            "coordinate_space": space,
            "entity_set": declaration.get("entity_set"),
            "topology": declaration.get("topology"),
            "units": {**declaration.get("units", {}), **{name: d["unit"] for name, d in declaration.get("derived_fields", {}).items()}},
        }
        save_json(manifest_path, metadata)
        if committed:
            committed(destination)
    return result
