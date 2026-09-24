"""消费应用给出的复制清单；校验内容与目标路径，不解释科学引用。"""

from pathlib import Path

from .files import copy_content, write_json
from .layout import inside
from .snapshots import digest, inventory


def copy_declared_dataset(manifest: Path, target: Path, *, context: dict) -> dict:
    """复制声明成员并写新副本描述，调用方负责目标目录的提交或回退。"""
    from ..tasks.operation_sources import invoke_source, with_operation

    revision = digest(inventory(manifest))
    plan = invoke_source(
        with_operation(context["source"], "inspect"),
        context["recipe"],
        {"operation": "dataset_copy_plan", "manifest": str(manifest)},
    )
    target.mkdir(parents=True, exist_ok=True)
    occupied = set()
    for item in plan["copies"]:
        source, destination = Path(item["source"]), inside(target, item["target"])
        if destination in occupied or destination.exists():
            raise ValueError("asset_copy_target_conflict")
        occupied.add(destination)
        before = digest(inventory(source))
        copy_content(source, destination)
        if before != digest(inventory(destination)) or before != digest(inventory(source)):
            raise ValueError("asset_copy_changed")
    for name, record in plan["documents"].items():
        destination = inside(target, name)
        if destination in occupied or destination.exists():
            raise ValueError("asset_copy_target_conflict")
        write_json(destination, record)
    if revision != digest(inventory(manifest)):
        raise ValueError("asset_copy_source_changed")
    return plan.get("summary", {})
