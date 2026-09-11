"""NASA CRM 样本目录与字段检查；HDF5 来源文件和样本身份独立。"""

from pathlib import Path

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint

from .adapter import RawDataset
from .physical import physical_fields


def inspect_dataset(config: dict) -> dict:
    """校验适配器必需项，记录共享连接关系和所选样本完整依赖。"""
    raw = RawDataset(config["dataset"])
    topology = Path(config["dataset"]["connectivity_h5"])
    if not topology.is_file():
        raise ValueError("dataset.connectivity_h5: 缺少完整样本拓扑依赖")
    sources = [
        {"source_id": key, "path": item["path"], "revision": file_fingerprint(item["path"])}
        for key, item in raw.sources.items()
    ]
    sources.append(
        {"source_id": "connectivity", "path": str(topology), "revision": file_fingerprint(topology)}
    )
    values = physical_fields(raw.read("train", 0))
    fields = []
    for name, value in values.items():
        association = "global" if name in {"conditions", "global_targets"} else "point"
        fields.append(
            {
                "field_id": "surface/" + association + "/" + name,
                "name": name,
                "member": name,
                "association": association,
                "shape": list(value.shape),
                "dtype": str(value.dtype),
                "components": value.shape[-1] if value.ndim > 1 else 1,
                "unit": None,
                "entity_set": "surface:" + association,
                "semantic_key": name,
            }
        )
    import h5py

    with h5py.File(raw.sources["training"]["path"], "r") as stream:
        group = stream[raw.partitions["train"][0]]
        for name, array in group.items():
            fields.append(
                {
                    "field_id": "surface/point/" + name,
                    "name": name,
                    "member": name,
                    "association": "point",
                    "shape": list(array.shape),
                    "dtype": str(array.dtype),
                    "components": 1,
                    "unit": None,
                    "entity_set": "surface:point",
                    "semantic_key": None,
                }
            )
    samples = [
        {
            "sample_id": name,
            "partition": split,
            "dependencies": ["test" if split == "test" else "training", "connectivity"],
        }
        for split, names in raw.partitions.items()
        for name in names
    ]
    return {
        "dataset_id": "nasa_crm",
        "revision": fingerprint(sources),
        "samples": samples,
        "sources": sources,
        "fields": fields,
        "dependencies": sources,
        "capabilities": {"formats": ["pt", "zarr"], "domains": ["surface"]},
    }
