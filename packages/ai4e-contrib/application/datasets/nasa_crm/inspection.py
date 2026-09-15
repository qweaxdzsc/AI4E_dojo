"""NASA 样本与字段检查；源文件共享，样本身份和选择由数据集解释。"""

from pathlib import Path

import h5py
import numpy as np

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.applications.aero_cfd.rawprep.catalog import (
    check_requested_fields,
    choose_samples,
    sample_key,
)

from .adapter import RawDataset
from .descriptor import describe_rawprep
from .physical import physical_fields


def inspect_dataset(config: dict) -> dict:
    """检查真实 HDF5 字段与样本依赖，不读取整库数组。"""
    raw = RawDataset(config["dataset"])
    partitions = choose_samples(raw.partitions, config.get("sample_scope"))
    topology = Path(config["dataset"]["connectivity_h5"])
    sources = [
        {
            "source_id": key,
            "path": item["path"],
            "revision": file_fingerprint(item["path"]),
            "exists": True,
        }
        for key, item in raw.sources.items()
    ]
    sources.append(
        {
            "source_id": "connectivity",
            "path": str(topology),
            "exists": topology.is_file(),
            "revision": file_fingerprint(topology) if topology.is_file() else None,
        }
    )
    errors = (
        []
        if topology.is_file()
        else [{"location": "connectivity", "message": "缺少完整样本拓扑依赖"}]
    )
    fields, samples, checked = {}, [], []
    full = config.get("inspection_scope") == "all"
    profile = describe_rawprep(config)
    for split, names in partitions.items():
        representative = physical_fields(raw.read(split, raw.partitions[split].index(names[0])))
        with h5py.File(
            raw.sources["test" if split == "test" else "training"]["path"], "r"
        ) as stream:
            for index, name in enumerate(names):
                samples.append(
                    {
                        "key": sample_key(split, name),
                        "sample_id": name,
                        "partition": split,
                        "dependencies": ["test" if split == "test" else "training", "connectivity"],
                        "selection": {split: [name]},
                    }
                )
                if not full and index:
                    continue
                actual = []
                for member, array in stream[name].items():
                    supported = (
                        len(array.shape) == 1
                        and array.shape[0] == raw.point_count
                        and (
                            np.issubdtype(array.dtype, np.integer)
                            or np.issubdtype(array.dtype, np.floating)
                        )
                    )
                    item = {
                        "field_id": f"surface/point/{member}",
                        "name": member,
                        "member": member,
                        "association": "point",
                        "shape": list(array.shape),
                        "dtype": str(array.dtype),
                        "components": 1,
                        "unit": None,
                        "entity_set": "surface:point",
                        "semantic_key": None,
                        "supported": supported,
                    }
                    actual.append(item)
                    fields.setdefault(item["field_id"], item)
                for item in profile["outputs"]:
                    desc = {
                        "field_id": f"surface/{item['association']}/{item['name']}",
                        "name": item["name"],
                        "member": item["name"],
                        "association": item["association"],
                        "shape": list(representative[item["name"]].shape),
                        "dtype": str(representative[item["name"]].numpy().dtype),
                        "components": item["components"],
                        "unit": item.get("unit"),
                        "entity_set": "surface:" + item["association"],
                        "semantic_key": item["name"],
                        "supported": True,
                    }
                    actual.append(desc)
                    fields.setdefault(desc["field_id"], desc)
                try:
                    check_requested_fields(
                        actual, config, declarations={x["name"]: x for x in profile["outputs"]}
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
    return {
        "dataset_id": "nasa_crm",
        "revision": fingerprint(sources),
        "samples": samples,
        "sources": sources,
        "fields": list(fields.values()),
        "dependencies": sources,
        "errors": errors,
        "selection": partitions,
        "inspection": {"scope": "all" if full else "representatives", "checked_samples": checked},
        "capabilities": {"formats": ["pt", "zarr"], "domains": ["surface"]},
        "profile": profile,
    }
