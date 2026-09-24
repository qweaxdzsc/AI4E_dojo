"""按配置和应用来源修订读取可选任务声明；静态入口读取不执行用户代码。"""

from pathlib import Path

from ai4e_spec.artifacts.task_operations import validate_description

from ..storage.files import read_json, write_json
from ..storage.snapshots import digest
from .operation_sources import capture_source, invoke_source, verify_source


def describe_recipe(
    recipe: str | Path, *, config: dict | None = None, cache_dir: Path | None = None
) -> dict:
    """缺少应用声明返回空描述；已声明入口出错不伪装成无描述。"""
    from omegaconf import OmegaConf

    from ..templates.materialize import read_entry

    recipe = Path(recipe).resolve()
    if not read_entry(recipe).get("components", {}).get("application"):
        return {"description": None, "source": None}
    source = capture_source(recipe, "inspect")
    config = (
        config
        if config is not None
        else OmegaConf.to_container(OmegaConf.load(recipe / "config.yaml"), resolve=False)
    )
    key = digest({"config": config, "source": source["revision"]})
    cache = cache_dir / (key + ".json") if cache_dir else None
    if cache and cache.is_file():
        record = read_json(cache)
        verify_source(record["source"], recipe)
        return {**record, "description": validate_description(record["description"])}
    try:
        result = invoke_source(
            source,
            recipe,
            {"operation": "describe_task", "config": config, "config_dir": str(recipe)},
        )
    except ValueError as exc:
        if str(exc).startswith(
            ("operation_unavailable: describe_task", "operation_unavailable: inspect")
        ):
            return {"description": None, "source": source}
        raise
    # 历史自由检查函数可能原样返回未知请求；缺描述不会阻止脚本托管。
    if isinstance(result, dict) and "schema_version" not in result:
        return {"description": None, "source": source}
    record = {
        "description": validate_description(result),
        "source": source,
        "config_revision": digest(config),
    }
    if cache:
        write_json(cache, record)
    return record


def described_entry(
    recipe: str | Path, *, config: dict | None = None, cache_dir: Path | None = None
) -> dict:
    """合并可选管理声明，输入路径树保持原样；未声明输入按普通文件捕获。"""
    from ..templates.materialize import read_entry

    entry = read_entry(Path(recipe))
    record = describe_recipe(recipe, config=config, cache_dir=cache_dir)
    entry["task_description"] = record
    description = record["description"]
    if description is None:
        return entry
    entry["inputs"].update({key: req["kind"] for key, req in description["inputs"].items()})
    entry["stages"] = description["stages"]
    entry["shared_outputs"] = description.get("shared_outputs", {})
    entry["resume_inputs"] = description.get("resume_inputs", [])
    entry["stage_inputs"] = {
        stage: [
            {"key": key, **({"provided_by": req["provided_by"]} if "provided_by" in req else {})}
            for key, req in description["inputs"].items()
            if key.split(".")[1] == stage
        ]
        for stage in description["stages"]
    }
    return entry
