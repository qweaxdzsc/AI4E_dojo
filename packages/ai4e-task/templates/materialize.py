"""展开普通 recipe 文件及显式输入路径；不导入用户代码。"""

from pathlib import Path

from ..storage.files import read_json
from ..storage.layout import inside
from ..storage.snapshots import snapshot


def read_entry(recipe: Path) -> dict:
    """读取可选 task-entry.json，运行前必须存在有效声明。"""
    path = recipe / "task-entry.json"
    if not path.exists():
        return {}
    value = read_json(path)
    for key in ("script", "config"):
        inside(recipe, value[key])
    if not isinstance(value.get("outputs"), dict) or not isinstance(value.get("inputs", {}), dict):
        raise TypeError("invalid_entry_bindings")
    return value


def materialize(source: Path | None, target: Path) -> dict:
    """复制代码，展开声明输入的相对路径，保持输出绑定由运行时分配。"""
    if source is None:
        target.mkdir(parents=True)
        return {}
    captured = snapshot(source, target)
    entry = read_entry(target)
    if entry and (target / entry["config"]).exists():
        from omegaconf import OmegaConf

        cfg = OmegaConf.load(target / entry["config"])
        base = (source / entry["config"]).parent
        for key in entry.get("inputs", {}):
            value = OmegaConf.select(cfg, key)
            if isinstance(value, str) and value not in {"official", "last", "best", "latest"}:
                path = Path(value).expanduser()
                OmegaConf.update(
                    cfg,
                    key,
                    str((base / path).resolve() if not path.is_absolute() else path.resolve()),
                )
        OmegaConf.save(cfg, target / entry["config"])
    return captured
