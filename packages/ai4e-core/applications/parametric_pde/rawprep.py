"""参数化物理数据的读取与校验；数据生成在独立入口完成。"""


def rawprep(cfg, *, dataset_component, session, **components):
    """逐个核验清单中的完整物理数据，报告来源而不改配置。"""
    dataset = dataset_component.Dataset(cfg["dataset"]["manifest"])

    def check(record):
        dataset.read(record)
        return {"id": record["id"]}

    session.execute_samples(dataset.manifest["samples"], check, stage="rawprep")
    result = {
        "manifest": str(dataset.path),
        "content_id": dataset.manifest["content_id"],
        "samples": len(dataset.manifest["samples"]),
    }
    session.report(result, stage="dataset")
    return result


def prepare_named_fields(samples, reader, output, *, session, metadata: dict):
    """按来源样本名单交付原网格、逐场 PT 和清单；任何失败不发布完整清单。"""
    from pathlib import Path

    from ai4e_core.abilities.data.save.array_manifest import digest
    from ai4e_core.abilities.data.save.arrays import save_json
    from ai4e_core.abilities.data.save.mesh_dataset import save_mesh_sample

    root = Path(output)
    root.mkdir(parents=True, exist_ok=True)
    if (root / "manifest.json").exists():
        raise FileExistsError(root / "manifest.json")
    seen = set()

    def process(sample):
        identity = (sample["split"], sample["id"])
        if identity in seen or any(Path(x).name != x or x in {".", ".."} for x in identity):
            raise ValueError("样本身份重复或非法")
        seen.add(identity)
        mesh, details = reader(sample)
        path = Path(
            save_mesh_sample(
                root / sample["split"] / sample["id"], mesh, metadata={**details, **sample}
            )
        )
        return {
            "id": sample["id"],
            "split": sample["split"],
            "path": str(path.relative_to(root)),
            "sha256": digest(path),
        }

    results = session.execute_samples(samples, process, stage="rawprep")
    save_json(
        root / "manifest.json",
        {"kind": "named-mesh-dataset-v1", "metadata": metadata, "samples": results},
    )
    return str(root / "manifest.json")
