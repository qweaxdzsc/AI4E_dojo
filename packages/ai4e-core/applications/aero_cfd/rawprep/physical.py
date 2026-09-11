"""物理 PT 前处理装配；字段解释来自数据组件，提交复用数据能力。"""

from pathlib import Path

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.applications.aero_cfd.rawprep.pointfields import prepare


class SavePhysical:
    """单样本事务与完整清单分离，失败保留已提交样本。"""

    def __init__(self, raw, component, config):
        self.raw, self.component, self.config = raw, component, config

    def preflight(self, data, output, *, flags, settings):
        """提交前检查实际目录，禁止静默覆盖。"""
        root = Path(output["root"])
        if root.exists() and any(root.iterdir()) and not flags["overwrite"]:
            raise FileExistsError(f"物理数据目录非空: {root}")

    def begin(self, data, output, *, flags):
        """覆盖开始撤下旧完整标记，失败不冒充完整交付。"""
        if not flags["dry_run"]:
            (Path(output["root"]) / "manifest.json").unlink(missing_ok=True)

    def __call__(self, ctx, *, output):
        """写出物理张量与可追踪来源，保留逐样本身份。"""
        split, name = ctx["partition"], ctx["sample_id"]
        dest = Path(output["root"]) / split / name
        record = {"sample": name, "partition": split, "path": str(dest), "written": False}
        if ctx["dry_run"]:
            return record
        fields = self.component.physical_fields(ctx["arrays"])
        format = self.config.get("format", "pt")
        if format not in {"pt", "zarr"}:
            raise ValueError("rawprep.format 必须为 pt 或 zarr")
        aliases = {}
        if self.config.get("extraction"):
            from .extraction import compile_extraction

            output = compile_extraction(self.config["extraction"], format=format)
            grouped = {}
            for output_name, members in output["members"].items():
                grouped[output_name] = {}
                for member, source_field in members.items():
                    source_name = source_field["field"].removeprefix("fields.")
                    if source_name == "points":
                        source_name = "surface_position"
                    if source_name in fields:
                        aliases.setdefault(source_name, output_name + "/" + member)
                    if source_name not in fields:
                        grouped[output_name][member] = self.component.read_physical_field(
                            self.raw, split, ctx["sample_id"], source_name
                        )
                    else:
                        grouped[output_name][member] = fields[source_name]
            fields = grouped
        filemap = {k: k + "." + format for k in fields}
        write_named_tensors(dest, fields, filemap, overwrite=ctx.get("overwrite", False))
        source = self.raw.sources["test" if split == "test" else "training"]["path"]

        def descriptor(value):
            if isinstance(value, dict):
                return {
                    "state": "physical",
                    "members": {k: descriptor(v) for k, v in value.items()},
                }
            return {"shape": list(value.shape), "dtype": str(value.dtype), "state": "physical"}

        return {
            **record,
            "written": True,
            "filemap": filemap,
            "field_aliases": aliases,
            "source": {"path": source, "sample": name},
            "fields": {k: descriptor(v) for k, v in fields.items()},
        }


def execute(config, component, executor, session):
    """由唯一运行器循环样本，只发布本次完整成功清单。"""
    data, raw = prepare(config, component)
    result = executor(
        data, save=SavePhysical(raw, component, config), output=config["paths"]["datasets"]
    )
    if result["failed"] or result["success"] != result["total"]:
        raise ValueError("物理数据部分失败，禁止发布完整清单")
    if result["dry_run"]:
        return {"mode": "rawprep_check"}
    path = Path(result["output"]["root"]) / "manifest.json"
    manifest = {
        "version": 1,
        "state": "physical",
        "partitions": raw.partitions,
        "samples": result["results"],
        "physical_layout": component.LAYOUT,
    }
    save_json(path, manifest)
    report = {"manifest": str(path), "split_counts": {k: len(v) for k, v in raw.partitions.items()}}
    session.report(report, stage="rawprep")
    return report
