"""汽车样本业务检查：目录依赖与真实字段，不把文件数量当作样本数量。"""

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint

from .adapter import open_dataset


def inspect_dataset(config: dict) -> dict:
    """检查全部所选样本依赖，并从首个样本读取各域真实字段结构。"""
    from vtk.util.numpy_support import vtk_to_numpy

    settings = config["dataset"]
    data = open_dataset(
        root=settings["root"],
        manifest=settings.get("manifest"),
        samples=settings.get("samples", "all"),
        partition=settings.get("partition", "official"),
    )
    sources, fields, samples = [], [], []
    selected = config.get("sources", list(data.metadata["sources"]))
    for split, names in data.partitions.items():
        for name in names:
            dependencies = []
            for role in selected:
                path = data.root / name / data.metadata["sources"][role]["filename"]
                if not path.is_file():
                    raise ValueError(f"{split}/{name}/{role}: 样本依赖缺失 {path}")
                source_id = f"{split}/{name}/{role}"
                sources.append(
                    {"source_id": source_id, "path": str(path), "revision": file_fingerprint(path)}
                )
                dependencies.append(source_id)
                if len(samples) == 0:
                    import vtk

                    reader = vtk.vtkGenericDataObjectReader()
                    reader.SetFileName(str(path))
                    reader.Update()
                    mesh = reader.GetOutput()
                    arrays = [("geometry", "points", vtk_to_numpy(mesh.GetPoints().GetData()))]
                    for association, collection in (
                        ("point", mesh.GetPointData()),
                        ("cell", mesh.GetCellData()),
                    ):
                        for i in range(collection.GetNumberOfArrays()):
                            array = collection.GetArray(i)
                            arrays.append((association, array.GetName(), vtk_to_numpy(array)))
                    for association, member, array in arrays:
                        fields.append(
                            {
                                "field_id": f"{role}/{association}/{member}",
                                "name": member,
                                "member": member,
                                "association": association,
                                "shape": list(array.shape),
                                "dtype": str(array.dtype),
                                "components": array.shape[-1] if array.ndim > 1 else 1,
                                "unit": None,
                                "entity_set": f"{role}:{association}",
                                "semantic_key": role,
                            }
                        )
            samples.append({"sample_id": name, "partition": split, "dependencies": dependencies})
    return {
        "dataset_id": "shapenet_car",
        "revision": fingerprint(sources),
        "samples": samples,
        "sources": sources,
        "fields": fields,
        "dependencies": sources,
        "capabilities": {"formats": ["pt", "zarr"], "domains": list(selected)},
    }
