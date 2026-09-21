"""按公开模型组件准备点集与样条资产，冻结数据和组件来源。"""

from pathlib import Path

from ai4e_core.abilities.data.save.bundle import digest, file_digest, save_bundle, save_json
from ai4e_core.base.events import ATOMIC_LEVEL, event

from .contracts import preparation_contract


def trainprep(cfg, *, dataset_component, model_component, session):
    """显式执行准备；新目录逐样本提交，失败不发布完整准备清单。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])
    root = Path(cfg["trainprep"]["output"])
    if root.exists() and any(root.iterdir()):
        raise FileExistsError(f"准备输出必须为新目录: {root}")
    result = {"contract": preparation_contract(cfg, dataset, model_component), "samples": []}
    if session.dry_run or not cfg["trainprep"]["execute"]:
        session.report(
            {"status": "checked", "samples": len(dataset.manifest["samples"])}, stage="trainprep"
        )
        return None

    def prepare_one(record):
        prepared = model_component.prepare(dataset.read(record), cfg)
        relative = f"{record['split']}/{record['id']}.pt"
        save_bundle(root / relative, prepared)
        event("物理准备", "样本完成", level=ATOMIC_LEVEL, 样本=record["id"])
        return {
            "id": record["id"],
            "split": record["split"],
            "path": relative,
            "sha256": file_digest(root / relative),
        }

    result["samples"] = session.execute_samples(
        dataset.manifest["samples"], prepare_one, stage="trainprep"
    )
    result["content_id"] = digest(result)
    save_json(root / "preparation.json", result)
    report = {
        "path": str(root / "preparation.json"),
        "content_id": result["content_id"],
        "samples": len(result["samples"]),
    }
    session.artifact("preparation.json", report)
    session.record_asset(
        "preparation",
        root / "preparation.json",
        kind="preparation",
        stage="trainprep",
        dependencies=[root],
    )
    session.report(report, stage="trainprep")
    return report


def prepare_field_inputs(
    physical, output, *, extract, statistics, transform, declaration: dict, caches=None
):
    """读取物理样本后按显式抽取/统计/变换准备模型数组；统计只看训练分片。"""
    from pathlib import Path

    import numpy as np

    from ai4e_core.abilities.data.save.array_manifest import save_arrays
    from ai4e_core.abilities.data.save.arrays import save_json
    from ai4e_core.abilities.data.save.mesh_dataset import read_mesh_dataset

    entries = read_mesh_dataset(physical)
    grouped = {}
    for entry in entries:
        grouped.setdefault(entry["split"], []).append((entry, extract(entry["path"])))
    stacked = {
        split: {key: np.stack([item[key] for _, item in samples]) for key in samples[0][1]}
        for split, samples in grouped.items()
    }
    stats = statistics(stacked["train"])
    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    paths = {}
    for split, arrays in stacked.items():
        converted = transform(arrays, stats)
        if caches is not None:
            converted.update(caches(converted))
        paths[split] = str(
            Path(
                save_arrays(
                    root / split,
                    converted,
                    kind="named-field-inputs-v1",
                    metadata={
                        "ids": [e["id"] for e, _ in grouped[split]],
                        "declaration": declaration,
                        "statistics": stats,
                    },
                )
            ).relative_to(root)
        )
    save_json(
        root / "manifest.json",
        {
            "kind": "named-field-preparation-v1",
            "splits": paths,
            "declaration": declaration,
            "statistics": stats,
        },
    )
    return str(root / "manifest.json")


def read_field_inputs(path, split):
    """读回可搬移模型准备分片，不依赖原始数据目录。"""
    import json
    from pathlib import Path

    from ai4e_core.abilities.data.save.array_manifest import read_arrays

    path = Path(path).resolve()
    record = json.loads(path.read_text())
    if record["kind"] != "named-field-preparation-v1":
        raise ValueError("模型准备版本不兼容")
    target = (path.parent / record["splits"][split]).resolve()
    if not target.is_relative_to(path.parent):
        raise ValueError("准备路径越界")
    return read_arrays(target, kind="named-field-inputs-v1")
