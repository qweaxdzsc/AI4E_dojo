"""三个经典研究案例的共享准备交接；统计只拟合本次训练分片。"""

import json
import shutil
from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_dataset
from ai4e_core.abilities.data.stats.masked_fields import masked_statistics
from ai4e_core.applications.parametric_pde.rawprep import prepare_named_fields


def dataset_binding(case):
    """选择来源语义模块，核心运行器不解释案例名称。"""
    from . import darcy, double_cylinder, shapenet_volume

    return {"darcy": darcy, "shapenet_volume": shapenet_volume, "double_cylinder": double_cylinder}[
        case
    ]


def physical_source(cfg, output, session):
    """保存真实输入并发布完整名单，源目录保持只读。"""
    case = cfg["dataset"]["case"]
    binding = dataset_binding(case)
    root = cfg["inputs"]["rawprep"]["source"]
    if root is None:
        raise ValueError("缺少inputs.rawprep.source")
    if case == "double_cylinder":
        splits = binding.prepare_source(root, output, cfg["dataset"], session)
        result = Path(output) / "manifest.json"
        save_json(
            result,
            {
                "kind": "classic-window-dataset-v1",
                "splits": {
                    split: str(Path(path).relative_to(output)) for split, path in splits.items()
                },
            },
        )
        return str(result)
    source = binding.source(root, cfg["dataset"])
    return prepare_named_fields(
        source.samples(), source.read, output, session=session, metadata={"case": case}
    )


def prepare(physical, output, dataset, session):
    """转换模型独立准备；网格尺寸和窗口为数据规格，不包含网络私有字段。"""
    binding = dataset_binding(dataset["case"])
    groups, ids = {}, {}
    if dataset["case"] == "double_cylinder":
        index = json.loads(Path(physical).read_text())
        if index["kind"] != "classic-window-dataset-v1":
            raise ValueError("窗口物理清单不匹配")
        for split, path in index["splits"].items():
            target = (Path(physical).parent / path).resolve()
            if not target.is_relative_to(Path(physical).parent.resolve()):
                raise ValueError("窗口路径越界")
            record, arrays = read_arrays(target, kind="classic-physical-windows-v1")
            groups[split], ids[split] = arrays, record["metadata"]["ids"]
    else:
        entries = read_mesh_dataset(physical)
        for split in ("train", "test"):
            selected = [item for item in entries if item["split"] == split]
            samples = session.execute_samples(
                selected, lambda item: binding.extract(item["path"], dataset), stage="trainprep"
            )
            groups[split] = {
                key: np.stack([sample[key] for sample in samples]) for key in samples[0]
            }
            ids[split] = [item["id"] for item in selected]
    train = groups["train"]
    feature_count = train["input"].shape[-1] - (dataset["case"] == "shapenet_volume")
    weights = train["valid"][..., None]
    if dataset["case"] == "double_cylinder":
        input_weights = np.expand_dims(weights, 1)
    else:
        input_weights = weights
    statistics = {
        "input": masked_statistics([(train["input"][..., :feature_count], input_weights)]),
        "target": masked_statistics([(train["target"], weights)]),
        "fit_ids": ids["train"],
        "feature_count": feature_count,
    }
    paths = {}
    for split, arrays in groups.items():
        raw = np.array(arrays["input"], dtype=np.float32, copy=True)
        x = raw.copy()
        x[..., :feature_count] = (
            x[..., :feature_count] - np.asarray(statistics["input"]["mean"], np.float32)
        ) / np.asarray(statistics["input"]["scale"], np.float32)
        y = (arrays["target"] - np.asarray(statistics["target"]["mean"], np.float32)) / np.asarray(
            statistics["target"]["scale"], np.float32
        )
        converted = {
            **arrays,
            "input": x,
            "target": np.asarray(y, np.float32),
            "physical_target": np.asarray(arrays["target"], np.float32),
            "physical_input": raw,
        }
        path = save_arrays(
            Path(output) / split,
            converted,
            kind="classic-inputs-v1",
            metadata={
                "ids": ids[split],
                "case": dataset["case"],
                "split": split,
                "statistics": statistics,
                "fields": list(binding.FIELDS),
                "units": binding.UNITS,
            },
        )
        paths[split] = str(Path(path).relative_to(output))
    physical_reference = {}
    if dataset["case"] == "shapenet_volume":
        # 保留准备自己的物理快照；搬移准备后不回读来源或另一任务目录。
        shutil.copytree(Path(physical).parent, Path(output) / "physical")
        physical_reference = {"physical": "physical/" + Path(physical).name}
    save_json(
        Path(output) / "manifest.json",
        {
            "kind": "classic-preparation-v1",
            "splits": paths,
            "statistics": statistics,
            "dataset": dataset,
            **physical_reference,
        },
    )
    return str(Path(output) / "manifest.json")


def read_prepared(path, split):
    """校验可搬移数组清单，不回读原始源或其他模型配置。"""
    path = Path(path).resolve()
    index = json.loads(path.read_text())
    if index["kind"] != "classic-preparation-v1":
        raise ValueError("准备版本不兼容")
    target = (path.parent / index["splits"][split]).resolve()
    if not target.is_relative_to(path.parent):
        raise ValueError("准备引用越界")
    return read_arrays(target, kind="classic-inputs-v1")


def original_samples(path, split, identities):
    """从准备内物理快照按显式样本身份读取回贴目标，不依赖原始源。"""
    path = Path(path).resolve()
    index = json.loads(path.read_text())
    target = (path.parent / index["physical"]).resolve()
    if not target.is_relative_to(path.parent):
        raise ValueError("原网格引用越界")
    entries = [item for item in read_mesh_dataset(target) if item["split"] == split]
    lookup = {item["id"]: item["path"] for item in entries}
    if len(lookup) != len(entries) or set(identities) != set(lookup):
        raise ValueError("规则格与原网格样本身份不一致")
    return [lookup[identity] for identity in identities]
