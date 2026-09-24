"""项目共享数据的查询与绑定；不依赖平台，也不建立训练任务版本。"""

from pathlib import Path

from ..storage.shared_datasets import directory, read_dataset


def list_shared_datasets(project: str | Path) -> list[dict]:
    """按最近发布时间列出项目共享数据及不可用原因，不扫描张量。"""
    root = Path(project) / "shared/datasets"
    if not root.is_dir():
        return []
    result = []
    for folder in root.iterdir():
        if not (folder / "asset.json").is_file():
            continue
        try:
            result.append(read_dataset(project, folder.name))
        except (ValueError, KeyError, OSError):
            continue
    return sorted(
        result,
        key=lambda value: (value.get("updated_at", value["created_at"]), value["name"]),
        reverse=True,
    )


def get_shared_dataset(project: str | Path, name: str) -> dict:
    """取得同名当前资源；不可用状态返回给调用方，不自动重做。"""
    return read_dataset(project, name)


def describe_shared_name(project: str | Path, name: str) -> dict:
    """名称门禁只检查本项目，同名无论配置是否相同均要求显式覆盖。"""
    if not name or not name.strip():
        return {"status": "empty", "message": "正式执行前需要填写共享数据集名称。"}
    folder = directory(project, name)
    if folder.exists() and any(folder.iterdir()):
        return {"status": "conflict", "message": "同名项目共享数据集已存在，继续将覆盖其物理数据。"}
    return {"status": "available", "message": ""}


def bind_shared_dataset(
    project: str | Path, task_id: str, name: str, *, revision: str, binding: str | None = None
) -> dict:
    """将当前共享清单绑定到入口声明的消费键，配置与资产在同一事务保存。"""
    from ..storage.layout import task_dir
    from ..tasks.configuration import save_configuration
    from ..tasks.descriptions import described_entry

    value = get_shared_dataset(project, name)
    if value["status"] != "available":
        raise ValueError(f"shared_dataset_unavailable: {name}")
    entry = described_entry(task_dir(project, task_id) / "recipe")
    from ..tasks.asset_matching import match_asset

    description = entry["task_description"]["description"] or {}
    bindings = [
        key
        for key, requirement in description.get("inputs", {}).items()
        if match_asset(value, requirement, status="succeeded")["matches"]
    ]
    if binding is None:
        if len(bindings) != 1:
            raise ValueError("shared_consumer_binding_ambiguous_or_missing")
        binding = bindings[0]
    if binding not in bindings:
        raise ValueError("shared_consumer_binding_not_declared")
    from omegaconf import OmegaConf

    patch = OmegaConf.create({})
    OmegaConf.update(patch, binding, value["manifest_path"], force_add=True)
    return save_configuration(project, task_id, OmegaConf.to_container(patch), revision=revision)


def run_physical_manifest(project: str | Path, run: dict) -> Path | None:
    """解析运行当时的物理输出；共享已覆盖时不冒充旧运行结果。"""
    plans = run.get("shared_outputs", [])
    if not plans:
        path = Path(run["data_dir"]) / "manifest.json"
        return path if path.is_file() else None
    for plan in plans:
        try:
            value = read_dataset(project, plan["name"])
        except (OSError, ValueError, KeyError):
            continue
        if value["status"] == "available" and value["source"].get("run_id") == run["id"]:
            return Path(value["manifest_path"])
    return None
