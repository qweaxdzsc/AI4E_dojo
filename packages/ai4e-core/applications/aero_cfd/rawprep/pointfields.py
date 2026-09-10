"""点场前处理装配；样本循环由注入的运行器执行。"""

import json
import shutil
import tempfile
from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.arrays import save_json, save_npy
from ai4e_core.abilities.data.stats.population import PopulationMoments
from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint
from ai4e_core.applications.base.dataset import Dataset


def prepare(config, component):
    """来源组件发现样本；返回只登记读取步骤的数据集。"""
    raw = component.RawDataset(config["dataset"])
    lookup = {
        split + "/" + name: (split, i)
        for split, names in raw.partitions.items()
        for i, name in enumerate(names)
    }

    def read(ctx):
        split, index = lookup[ctx["sample"]]
        ctx["sample_id"] = raw.partitions[split][index]
        ctx["arrays"] = raw.read(split, index)
        return ctx

    data = Dataset(
        root=Path(config["dataset"]["root"]),
        samples=tuple(lookup),
        partitions={k: tuple(k + "/" + name for name in v) for k, v in raw.partitions.items()},
        metadata={
            "manifest_path": str(Path(config["dataset"]["root"])),
            "description": raw.describe(),
        },
        steps=(("读取点场", read),),
        options={"config": config},
    )
    return data, raw


class SaveSample:
    """逐样本目录事务；完整标记绑定源内容和所有已保存文件。"""

    def __init__(self, raw, component, *, resume=False):
        self.raw = raw
        self.component = component
        self.resume = resume
        self.source_id = None

    def preflight(self, data, output, *, flags, settings):
        """检查真实目标，干跑和提交使用同一覆盖门禁。"""
        root = Path(output["root"])
        if root.exists() and any(root.iterdir()) and not self.resume and not flags["overwrite"]:
            raise FileExistsError(f"数据目录非空: {root}；需要显式 resume 或 overwrite")

    def begin(self, data, output, *, flags):
        """提交前撤下完整清单；失败不能遗留本次完整成功标记。"""
        if flags["dry_run"]:
            return
        self.source_id = self.raw.content_digest()
        (Path(output["root"]) / "manifest.json").unlink(missing_ok=True)

    def __call__(self, ctx, *, output):
        """按参考布局保存物理字段，临时目录完整后才提升。"""
        split, name = ctx["partition"], ctx["sample_id"]
        dest = Path(output["root"]) / split / name
        if ctx["dry_run"]:
            return {"sample": name, "partition": split, "written": False, "path": str(dest)}
        marker = dest / ".commit.json"
        if self.resume and marker.is_file():
            try:
                record = json.loads(marker.read_text())
                expected = {"conditions.npy", "metadata.json"} | {
                    f"{field}_part{part}.npy"
                    for part in range(self.raw.chunk_count)
                    for field in ("points", "normals", "area", "labels")
                }
                if (
                    record["source"] == self.source_id
                    and set(record["files"]) == expected
                    and all(file_fingerprint(dest / f) == h for f, h in record["files"].items())
                ):
                    return {
                        "sample": name,
                        "partition": split,
                        "written": True,
                        "path": str(dest),
                        "reused": True,
                    }
            except (OSError, ValueError, KeyError):
                pass
        dest.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=f".{name}-", dir=dest.parent))
        backup = dest.with_name(f".{name}.previous")
        if backup.exists():
            if not dest.exists():
                backup.rename(dest)
            else:
                raise FileExistsError(f"遗留备份需要处理: {backup}")
        try:
            arrays = ctx["arrays"]
            save_npy(temporary / "conditions.npy", arrays["conditions"])
            for part in range(self.raw.chunk_count):
                for field in ("points", "normals", "area", "labels"):
                    save_npy(
                        temporary / f"{field}_part{part}.npy",
                        arrays[field][part :: self.raw.chunk_count],
                    )
            save_json(
                temporary / "metadata.json",
                {
                    "sample_id": name,
                    "split": split,
                    "point_count": self.raw.point_count,
                    "chunk_count": self.raw.chunk_count,
                    "global_targets": dict(
                        zip(
                            self.raw.global_target_fields,
                            arrays["global_targets"].tolist(),
                            strict=True,
                        )
                    ),
                },
            )
            files = {p.name: file_fingerprint(p) for p in temporary.iterdir()}
            save_json(temporary / ".commit.json", {"source": self.source_id, "files": files})
            if dest.exists():
                dest.rename(backup)
            try:
                temporary.rename(dest)
            except BaseException:
                if backup.exists():
                    backup.rename(dest)
                raise
            if backup.exists():
                shutil.rmtree(backup)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
        return {"sample": name, "partition": split, "written": True, "path": str(dest)}


def publish(results, raw, component):
    """只以本次完整成功结果计算训练统计和发布清单。"""
    if results["failed"] or results["success"] != results["total"]:
        raise ValueError("前处理部分失败，不能发布完整数据清单")
    root = Path(results["output"]["root"])
    if results["dry_run"]:
        return {"output": {"root": str(root)}, "mode": "datapre_check"}
    fields = raw.describe()["fields"]
    condition, label = (
        PopulationMoments(len(fields["conditions"])),
        PopulationMoments(len(fields["labels"])),
    )
    by_name = {(r["partition"], r["sample"]): Path(r["path"]) for r in results["results"]}
    for name in raw.partitions["train"]:
        directory = by_name[("train", name)]
        condition.update(np.load(directory / "conditions.npy", allow_pickle=False))
        for part in range(raw.chunk_count):
            label.update(np.load(directory / f"labels_part{part}.npy", allow_pickle=False))
    manifest = {
        **raw.describe(),
        "statistics": {"conditions": condition.finalize(), "labels": label.finalize()},
    }
    manifest["fingerprint"] = component.manifest_digest(manifest)
    save_json(root / "manifest.json", manifest)
    return {
        "output": {"root": str(root)},
        "manifest": str(root / "manifest.json"),
        "split_counts": {k: len(v) for k, v in raw.partitions.items()},
    }
