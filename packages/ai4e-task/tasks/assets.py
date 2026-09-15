"""任务输入资产的登记、核验及按类型复制。"""

from pathlib import Path
from uuid import uuid4

from ..storage.files import copy_content, write_json
from ..storage.layout import inside
from ..storage.snapshots import digest, inventory

KINDS = {"dataset", "preparation", "checkpoint", "model_preset", "other"}


def asset_path(project: str | Path, record: dict) -> Path:
    """项目内引用随项目移动，外部引用保持显式绝对路径。"""
    value = record["path"]
    return Path(value) if record.get("external") else inside(project, value)


def validate_asset(project: str | Path, record: dict) -> Path:
    """核对实际内容摘要，缺失或改变时拒绝继续。"""
    path = asset_path(project, record)
    if digest(inventory(path)) != record["digest"]:
        raise ValueError(f"asset_changed: {record['id']}")
    for dependency in record.get("dependencies", []):
        validate_asset(project, dependency)
    return path


def describe_asset(path: Path, *, kind: str, source: dict | None = None) -> dict:
    """记录已存在输入，使用流式内容摘要而不加载训练数据。"""
    if kind not in KINDS:
        raise ValueError(f"invalid_asset_kind: {kind}")
    return {
        "id": uuid4().hex,
        "kind": kind,
        "path": str(path.resolve()),
        "external": True,
        "digest": digest(inventory(path)),
        "source": source or {},
        "dependencies": [],
    }


def capture_inputs(
    recipe: Path,
    entry: dict,
    *,
    project,
    inherited: dict | None = None,
    shared: list[dict] | None = None,
    allow_unbound: bool = False,
) -> dict:
    """只登记入口声明且有实际文件的输入；官方分片等非路径值不作为资产。"""
    if not entry:
        return {}
    from omegaconf import OmegaConf

    cfg = OmegaConf.load(recipe / entry["config"])
    result = {}
    for key, kind in entry.get("inputs", {}).items():
        value = OmegaConf.select(cfg, key)
        if not isinstance(value, str) or value in {"official", "last", "best", "latest"}:
            continue
        path = Path(value).expanduser()
        if not path.is_absolute():
            path = (recipe / entry["config"]).parent / path
        old = (inherited or {}).get(key)
        if old is None:
            old = next(
                (a for a in (shared or []) if asset_path(project, a).resolve() == path.resolve()),
                None,
            )
        if old and asset_path(project, old).resolve() == path.resolve():
            validate_asset(project, old)
            result[key] = old
        else:
            # 创建时允许模板保留待绑定路径；执行捕获仍要求实际文件。
            if allow_unbound and not path.exists():
                continue
            result[key] = describe_asset(path, kind=kind)
    return result


def copy_assets(
    project: str | Path, assets: dict, stage: Path, final: Path, kinds: set[str]
) -> dict:
    """按类别复制到子任务，来源身份保留；未选资产继续引用。"""
    if not kinds <= KINDS:
        raise ValueError("invalid_copy_kind")
    result = {}
    for key, original in assets.items():
        source = validate_asset(project, original)
        if original["kind"] not in kinds:
            result[key] = original
            continue
        folder = inside(stage / "assets", key)
        folder.mkdir(parents=True)
        target = folder / "content" / source.name if source.is_file() else folder / "content"
        copy_content(source, target)
        if digest(inventory(target)) != original["digest"]:
            raise ValueError("asset_copy_changed")
        relative = target.relative_to(stage)
        value = {
            **original,
            "id": uuid4().hex,
            "external": False,
            "path": str((final / relative).relative_to(Path(project).resolve())),
            "source": {"asset_id": original["id"], **original.get("source", {})},
        }
        write_json(folder / "asset.json", value)
        result[key] = value
    return result


def collect_run_assets(project: str | Path, run: dict, kinds: set[str]) -> dict:
    """依据捕获入口的产物声明收集父运行输出；复制不自动绑定训练输入。"""
    from ..templates.materialize import read_entry

    root = Path(project).resolve()
    entry = read_entry(root / run["code_path"])
    directory = root / run["run_path"]
    result = {}
    provenance = {"run_id": run["id"], "task_id": run["task_id"], "version_id": run["version_id"]}
    for kind, patterns in entry.get("produced_assets", {}).items():
        if kind not in kinds:
            continue
        for pattern in patterns:
            inside(directory, pattern)
            for file in sorted(directory.glob(pattern)):
                if not file.resolve().is_relative_to(directory.resolve()):
                    raise ValueError("asset_output_escape")
                record = describe_asset(file, kind=kind, source=provenance)
                # 准备记录引用原运行的数据；复制准备 JSON 不意味着迁移了这些依赖。
                data = root / run["data_path"]
                if kind == "preparation" and data.exists():
                    record["dependencies"] = [
                        describe_asset(data, kind="dataset", source=provenance)
                    ]
                result[f"run-{run['id']}-{kind}-{file.name}"] = record
    return result
