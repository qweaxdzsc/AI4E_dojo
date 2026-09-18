"""按入口声明分配共享输出与阶段输入；不解释领域算法或模型配置。"""

from pathlib import Path
from string import Formatter

from ..storage.layout import inside
from ..storage.processed_datasets import validate_processed_name


def validate_declarations(entry: dict) -> None:
    """校验可选声明及引用，旧入口不承担新的业务协议。"""
    outputs = entry.get("shared_outputs", {})
    stages = entry.get("stage_inputs", {})
    if not isinstance(outputs, dict) or not isinstance(stages, dict):
        raise TypeError("invalid_shared_declarations")
    for group, declaration in outputs.items():
        if (
            not isinstance(group, str)
            or not group.isidentifier()
            or not isinstance(declaration, dict)
        ):
            raise ValueError("invalid_shared_output")
        if declaration.get("kind") != "dataset":
            raise ValueError("unsupported_shared_output_kind")
        for key in ("stage", "name_key", "manifest", "consumer_binding"):
            if not isinstance(declaration.get(key), str) or not declaration[key]:
                raise ValueError(f"shared_output_missing: {key}")
        inside(Path("/declaration"), declaration["manifest"])
        if declaration["consumer_binding"] not in entry.get("inputs", {}):
            raise ValueError("shared_consumer_binding_not_declared")
    for stage, inputs in stages.items():
        if not isinstance(stage, str) or not isinstance(inputs, list):
            raise TypeError("invalid_stage_inputs")
        for item in inputs:
            if not isinstance(item, dict) or item.get("key") not in entry.get("inputs", {}):
                raise ValueError("unknown_stage_input_binding")
            if set(item) - {"key", "provided_by"}:
                raise ValueError("invalid_stage_input")


def selected_inputs(entry: dict, stages: list[str]) -> list[str] | None:
    """只捕获选定阶段的外部输入；同次前序生产的输入不提前索取。"""
    if entry.get("convention_version") == 1:
        return sorted(key for key in entry["inputs"] if key.split(".")[1] in stages)
    declarations = entry.get("stage_inputs")
    if not declarations or any(stage not in declarations for stage in stages):
        return None
    return sorted(
        {
            item["key"]
            for index, stage in enumerate(stages)
            for item in declarations[stage]
            if item.get("provided_by") not in stages[:index]
        }
    )


def allocate_outputs(
    project: Path,
    entry: dict,
    cfg,
    run_dir: Path,
    data_dir: Path,
    *,
    operation_mode: str,
    overwrite: bool,
) -> tuple[dict, list[dict]]:
    """生成本次受控路径；共享生产仅在正式非检查运行中启用。"""
    from omegaconf import OmegaConf

    stages = list(OmegaConf.select(cfg, "pipeline.stages", default=[]))
    dry_run = bool(OmegaConf.select(cfg, "execution.dry_run", default=False))
    bindings = {"run_root": str(run_dir.parent), "data_dir": str(data_dir)}
    plans = []
    for group, declaration in entry.get("shared_outputs", {}).items():
        path = data_dir / group
        if declaration["stage"] in stages and operation_mode == "execute" and not dry_run:
            name = validate_processed_name(OmegaConf.select(cfg, declaration["name_key"]))
            path = inside(project, f"shared/datasets/{name}/content")
            plans.append(
                {
                    **declaration,
                    "group": group,
                    "name": name,
                    "path": str(path.relative_to(project)),
                    "overwrite": overwrite,
                }
            )
        bindings[f"shared_{group}_dir"] = str(path)
    if len({plan["name"] for plan in plans}) != len(plans):
        raise ValueError("duplicate_shared_output_name")
    shared_roots = [project / plan["path"] for plan in plans]
    for key, pattern in entry["outputs"].items():
        if not isinstance(pattern, str):
            raise TypeError("invalid_output_pattern")
        fields = [field for _, field, _, _ in Formatter().parse(pattern) if field]
        if any(field not in bindings for field in fields):
            raise ValueError(f"unknown_output_placeholder: {key}")
        value = pattern.format(**bindings)
        output = Path(value).resolve()
        if key == "run_root":
            if output != run_dir.parent:
                raise ValueError("run_root_binding_mismatch")
        elif not any(output.is_relative_to(root) for root in [data_dir, *shared_roots]):
            raise ValueError(f"output_binding_escape: {key}")
        OmegaConf.update(cfg, key, value, force_add=True)
    if "run_root" not in entry["outputs"]:
        raise ValueError("run_root_binding_required")
    return bindings, plans
