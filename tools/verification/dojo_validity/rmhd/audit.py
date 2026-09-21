"""将组内补充证据复制到主控，核对来源；不把自报计时当唯一可信时钟。"""

import shutil
from pathlib import Path

from ..io import digest, inventory, read_json, write_json


def archive_group(comparison, group):
    """保留研究源码与日志，避免在主控反复复制大训练缓存或透露其他组材料。"""
    root = Path(comparison)
    config = read_json(root / "comparison-protocol.json")
    experiment = Path(config["experiments"][group]).resolve()
    target = root / "evidence/group-artifacts" / group
    allowed_suffixes = {".py", ".yaml", ".yml", ".json", ".jsonl", ".log", ".md", ".toml", ".txt"}
    files, rejected = {}, []
    for folder in ("workspace", "evidence/activities", *[f"round-{i:02d}" for i in range(6)]):
        for path in (experiment / folder).rglob("*"):
            if path.is_symlink() or not path.resolve().is_relative_to(experiment):
                rejected.append(str(path.relative_to(experiment)))
                continue
            if (
                not path.is_file()
                or path.suffix not in allowed_suffixes
                or "__pycache__" in path.parts
            ):
                continue
            relative = path.relative_to(experiment)
            destination = target / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, destination)
            files[str(relative)] = digest(destination)
    record = {
        "files": files,
        "rejected_links": rejected,
        "activity_helper_matches": digest(experiment / "activity.py")
        == read_json(root / f"evidence/{group}-initial-materials.json")["activity.py"],
        "source": "group artifacts, cross-check with controller original stream and process observations",
        "authoritative_clock": False,
    }
    write_json(target / "inventory.json", record)
    return record


def archive_harness(comparison):
    """冻结当前主控实现；与原始调用policy、私有baseline源码分别保留版本证据。"""
    root = Path(comparison)
    source = Path(__file__).parent
    target = root / "evidence/harness-source"
    if target.exists():
        raise FileExistsError("已冻结主控源码不能覆盖")
    shutil.copytree(source, target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    files = inventory(target)
    write_json(root / "evidence/harness-source.json", files)
    return files
