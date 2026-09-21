"""物理 PT 前处理装配；字段解释来自数据组件，提交复用数据能力。"""

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path

from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.store import write_named_tensors
from ai4e_core.applications.base.dataset import Dataset


@dataclass
class PhysicalSource:
    """物理来源句柄；不持有整个数据集的数组。"""

    raw: object
    component: object
    config: dict


def open_source(config, *, component):
    """发现来源分片，读取步骤另行登记。"""
    return PhysicalSource(component.RawDataset(config["dataset"]), component, deepcopy(config))


def read(source):
    """登记单样本读取，身份包含分片和原样本名。"""
    raw = source.raw
    lookup = {
        split + "/" + name: (split, index)
        for split, names in raw.partitions.items()
        for index, name in enumerate(names)
    }
    data = Dataset(
        root=Path(source.config["dataset"]["root"]),
        samples=tuple(lookup),
        partitions={
            key: tuple(key + "/" + name for name in names) for key, names in raw.partitions.items()
        },
        metadata={
            "manifest_path": str(Path(source.config["dataset"]["root"])),
            "description": raw.describe(),
        },
        options={"config": source.config},
    )

    def read_one(ctx):
        split, index = lookup[ctx["sample"]]
        return {**ctx, "sample_id": raw.partitions[split][index], "arrays": raw.read(split, index)}

    return data.then("读取点场", read_one)


def extract_fields(data, *, component):
    """登记来源数组到具名物理字段的映射。"""
    return data.then(
        "提取物理字段",
        lambda ctx: {**ctx, "physical_fields": component.physical_fields(ctx["arrays"])},
    )


def validate_fields(data):
    """登记点字段实体数量门禁，禁止错误字段进入物理清单。"""

    def check(ctx):
        fields = ctx["physical_fields"]
        count = len(fields["surface_position"])
        for name, value in fields.items():
            if name.startswith("surface_") and len(value) != count:
                raise ValueError(f"物理字段实体数不一致: {name}")
        return ctx

    return data.then("校验物理字段", check)


def select_fields(data, *, source, extraction=None, format="pt"):
    """登记可选字段容器编排；未配置时保留完整物理布局。"""
    if not extraction:
        names = source.config.get("save_fields")
        if names is None:
            return data

        def select_named(ctx):
            missing = set(names) - set(ctx["physical_fields"])
            if missing:
                raise ValueError(f"{ctx['sample']}: 缺少保存字段 {sorted(missing)}")
            return {
                **ctx,
                "physical_fields": {name: ctx["physical_fields"][name] for name in names},
            }

        return data.then("选择物理字段", select_named)
    from .extraction import compile_extraction

    declarations = (
        {
            item["name"]: {"domain": item["domain"], "field": "fields." + item["name"]}
            for item in source.component.describe_rawprep()["outputs"]
        }
        if extraction.get("layout") == "fields"
        else None
    )
    output = compile_extraction(dict(extraction), format=format, declarations=declarations)

    def select(ctx):
        fields, grouped, aliases = ctx["physical_fields"], {}, {}
        if extraction.get("layout") == "fields":
            for output_name, spec in output["fields"].items():
                name = spec["field"].removeprefix("fields.")
                name = "surface_position" if name == "points" else name
                if name in fields and name != output_name:
                    aliases[name] = output_name
                grouped[output_name] = (
                    fields[name]
                    if name in fields
                    else source.component.read_physical_field(
                        source.raw, ctx["partition"], ctx["sample_id"], name
                    )
                )
            return {**ctx, "physical_fields": grouped, "field_aliases": aliases}
        for output_name, members in output["members"].items():
            grouped[output_name] = {}
            for member, spec in members.items():
                name = spec["field"].removeprefix("fields.")
                name = "surface_position" if name == "points" else name
                if name in fields:
                    aliases.setdefault(name, output_name + "/" + member)
                grouped[output_name][member] = (
                    fields[name]
                    if name in fields
                    else source.component.read_physical_field(
                        source.raw, ctx["partition"], ctx["sample_id"], name
                    )
                )
        return {**ctx, "physical_fields": grouped, "field_aliases": aliases}

    return data.then("选择字段容器", select)


def save_strategy(source):
    """返回已有事务保存策略；字段提取和选择由显式步骤完成。"""
    return SavePhysical(source.raw, source.component, source.config)


def publish_dataset(results, *, source, session):
    """仅在完整成功后发布本次物理清单。"""
    if results["failed"] or results["success"] != results["total"]:
        raise ValueError("物理数据部分失败，禁止发布完整清单")
    if results["dry_run"]:
        return {"mode": "rawprep_check"}
    path = Path(results["output"]["root"]) / "manifest.json"
    save_json(
        path,
        {
            "version": 1,
            "state": "physical",
            "partitions": source.raw.partitions,
            "samples": results["results"],
            "physical_layout": actual_layout(source.component.LAYOUT, results["results"]),
        },
    )
    report = {
        "manifest": str(path),
        "split_counts": {key: len(values) for key, values in source.raw.partitions.items()},
    }
    session.record_asset(
        "dataset", path, kind="dataset", stage="rawprep", dependencies=[path.parent]
    )
    session.report(report, stage="rawprep")
    return report


def actual_layout(layout, records):
    """只声明本次全部样本实际保存的字段；别名仍保留稳定业务语义。"""
    if not records:
        raise ValueError("物理数据没有成功样本")
    available = set(records[0]["filemap"]) | set(records[0].get("field_aliases", {}))
    for record in records[1:]:
        available &= set(record["filemap"]) | set(record.get("field_aliases", {}))
    result = deepcopy(layout)
    for domain, spec in list(result["domains"].items()):
        if spec["position"] not in available:
            del result["domains"][domain]
            continue
        spec["fields"] = {
            key: name for key, name in spec.get("fields", {}).items() if name in available
        }
        if spec.get("ids") not in available:
            spec.pop("ids", None)
    result["conditions"] = {
        key: value for key, value in result.get("conditions", {}).items() if key in available
    }
    return result


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
        fields = (
            ctx["physical_fields"]
            if "physical_fields" in ctx
            else self.component.physical_fields(ctx["arrays"])
        )
        from .descriptor import primary_format, resolved_formats

        raw = (
            self.config["rawprep"] if isinstance(self.config.get("rawprep"), dict) else self.config
        )
        formats = resolved_formats(raw)
        format = primary_format(formats)
        aliases = ctx.get("field_aliases", {})
        if self.config.get("extraction") and "physical_fields" not in ctx:
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
        extra = {}
        format_filemaps = {format: filemap}
        if len(formats) > 1:
            from functools import partial

            from ai4e_core.abilities.data.save.store import write_tensor_file
            from ai4e_core.abilities.data.save.zarr import write_zarr

            for item in formats:
                if item == format:
                    continue
                secondary = {k: k + "." + item for k in fields}
                format_filemaps[item] = secondary
                for name, filename in secondary.items():
                    extra[filename] = (
                        partial(write_zarr, payload=fields[name])
                        if item == "zarr"
                        else partial(write_tensor_file, payload=fields[name], overwrite=True)
                    )
        meshes = {}
        if raw.get("vtkhdf", False):
            from functools import partial

            from ai4e_core.abilities.data.save.vtkhdf import write_vtkhdf

            for domain, declaration in self.component.LAYOUT["domains"].items():
                position = declaration["position"]
                if position not in fields:
                    continue
                if not hasattr(self.component, "comparison_mesh"):
                    raise ValueError(f"{domain}: 数据适配器未提供 VTKHDF 网格构造能力")
                mesh = self.component.comparison_mesh(
                    self.config, name, domain, fields[position].detach().cpu().numpy()
                )
                filename = domain + ".vtkhdf"
                extra[filename] = partial(write_vtkhdf, mesh=mesh)
                meshes[domain] = filename
        write_named_tensors(
            dest, fields, filemap, overwrite=ctx.get("overwrite", False), extra_writers=extra
        )
        source = self.raw.sources["test" if split == "test" else "training"]["path"]

        def descriptor(value):
            if isinstance(value, dict):
                return {
                    "state": "physical",
                    "members": {k: descriptor(v) for k, v in value.items()},
                }
            return {"shape": list(value.shape), "dtype": str(value.dtype), "state": "physical"}

        result = {
            **record,
            "written": True,
            "filemap": filemap,
            "formats": formats,
            "format_filemaps": format_filemaps,
            "field_aliases": aliases,
            "source": {"path": source, "sample": name},
            "fields": {k: descriptor(v) for k, v in fields.items()},
        }
        if extra:
            result["assets"] = sorted(extra)
        if meshes:
            result["meshes"] = meshes
        return result


def execute(config, component, executor, session):
    """兼容整段入口，与新模板共用公开步骤及事务保存。"""
    source = open_source(config, component=component)
    data = read(source)
    data = extract_fields(data, component=component)
    data = validate_fields(data)
    from .descriptor import primary_format, resolved_formats

    raw = config["rawprep"] if isinstance(config.get("rawprep"), dict) else config
    data = select_fields(
        data,
        source=source,
        extraction=raw.get("extraction"),
        format=primary_format(resolved_formats(raw)),
    )
    results = executor(data, save=save_strategy(source), output=config["paths"]["datasets"])
    return publish_dataset(results, source=source, session=session)
