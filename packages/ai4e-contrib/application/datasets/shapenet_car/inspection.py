"""汽车样本检查：声明名单、代表字段与逐样本执行前检查。"""

import numpy as np

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.applications.aero_cfd.rawprep.catalog import (
    check_requested_fields,
    choose_samples,
    sample_key,
)

from .adapter import open_dataset
from .descriptor import describe_rawprep


def inspect_dataset(config: dict) -> dict:
    """检查所选样本依赖；目录预览容忍缺件，执行预检报告全部缺项。"""
    import vtk
    from vtk.util.numpy_support import vtk_to_numpy

    settings = config["dataset"]
    data = open_dataset(
        root=settings["root"],
        manifest=settings.get("manifest"),
        samples=settings.get("samples", "all"),
        partition=settings.get("partition", "official"),
        check_exists=False,
    )
    partitions = choose_samples(data.partitions, config.get("sample_scope"))
    selected = config.get("sources", list(data.metadata["sources"]))
    sources, fields, samples, errors, checked = [], {}, [], [], []
    full = config.get("inspection_scope") == "all"
    for split, names in partitions.items():
        inspected = False
        for name in names:
            dependencies, sample_fields = [], []
            for role in selected:
                path = data.root / name / data.metadata["sources"][role]["filename"]
                source_id = f"{split}/{name}/{role}"
                sources.append(
                    {
                        "source_id": source_id,
                        "path": str(path),
                        "revision": file_fingerprint(path) if path.is_file() else None,
                        "exists": path.is_file(),
                    }
                )
                dependencies.append(source_id)
                if not path.is_file():
                    errors.append(
                        {
                            "sample": sample_key(split, name),
                            "location": role,
                            "message": f"样本依赖缺失 {path}",
                        }
                    )
                    continue
                if full or not inspected:
                    reader = vtk.vtkGenericDataObjectReader()
                    reader.SetFileName(str(path))
                    reader.Update()
                    mesh = reader.GetOutput()
                    if not mesh or not mesh.GetPoints():
                        errors.append(
                            {
                                "sample": sample_key(split, name),
                                "location": role,
                                "message": "缺少网格坐标",
                            }
                        )
                        continue
                    arrays = [("geometry", "points", vtk_to_numpy(mesh.GetPoints().GetData()))]
                    for association, collection in [
                        ("point", mesh.GetPointData()),
                        ("cell", mesh.GetCellData()),
                    ]:
                        for i in range(collection.GetNumberOfArrays()):
                            array = collection.GetArray(i)
                            if array is not None:
                                arrays.append((association, array.GetName(), vtk_to_numpy(array)))
                    for association, member, array in arrays:
                        components = array.shape[-1] if array.ndim > 1 else 1
                        item = {
                            "field_id": f"{role}/{association}/{member}",
                            "name": member,
                            "member": member,
                            "association": association,
                            "shape": list(array.shape),
                            "dtype": str(array.dtype),
                            "components": components,
                            "unit": None,
                            "entity_set": f"{role}:{association}",
                            "semantic_key": role,
                            "supported": components in (1, 3)
                            and (
                                np.issubdtype(array.dtype, np.integer)
                                or np.issubdtype(array.dtype, np.floating)
                            ),
                        }
                        fields.setdefault(item["field_id"], item)
                        sample_fields.append(item)
            if full or not inspected:
                try:
                    check_requested_fields(
                        sample_fields,
                        config,
                        source_catalog=data.metadata["fields"],
                        declarations=data.metadata["outputs"],
                    )
                except ValueError as exc:
                    errors.append(
                        {
                            "sample": sample_key(split, name),
                            "location": "fields",
                            "message": str(exc),
                        }
                    )
                checked.append(sample_key(split, name))
                inspected = True
            samples.append(
                {
                    "key": sample_key(split, name),
                    "sample_id": name,
                    "partition": split,
                    "dependencies": dependencies,
                    "selection": name,
                }
            )
    return {
        "dataset_id": "shapenet_car",
        "revision": fingerprint(sources),
        "samples": samples,
        "sources": sources,
        "fields": list(fields.values()),
        "dependencies": sources,
        "errors": errors,
        "selection": [s["sample_id"] for s in samples],
        "inspection": {"scope": "all" if full else "representatives", "checked_samples": checked},
        "capabilities": {"formats": ["pt", "zarr"], "domains": list(selected)},
        "profile": describe_rawprep(config),
    }
