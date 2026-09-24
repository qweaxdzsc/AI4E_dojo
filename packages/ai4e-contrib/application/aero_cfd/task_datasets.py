"""外流处理数据身份和物理清单解释；通用发布事务由 Task 持有。"""

import hashlib
import json
from pathlib import Path


def processed_claim(config: dict) -> dict:
    """用源数据与处理产物语义识别同名是否同一意图；并行线程与列表顺序不进入声明。"""
    identity = _canonical_identity(config)
    return {"fingerprint": _fingerprint({"identity": identity}), "identity": identity}


def conflict_detail(existing: dict, incoming: dict) -> str:
    """应用解释处理身份差异；历史缺身份不根据当前配置补写。"""
    old, new = existing.get("identity", {}), incoming.get("identity", {})
    if not old or not new:
        return "名称已存在且声明缺失。确认后将覆盖原登记。"
    if old.get("vtkhdf") != new.get("vtkhdf"):
        before, after = ("开" if old.get("vtkhdf") else "关"), ("开" if new.get("vtkhdf") else "关")
        return f"已有登记 VTKHDF={before}，当前配置 VTKHDF={after}。确认后将覆盖原登记。"
    return "名称已存在且处理声明不同。确认后将覆盖原登记。"


def _canonical_identity(config: dict) -> dict:
    """只保留改变产物身份的字段；几何与格式按集合比较。"""
    dataset = config.get("dataset") or {}
    raw = config.get("rawprep") or {}
    return {
        "source_dataset": (config.get("components") or {}).get("dataset"),
        "root": dataset.get("root"),
        "train_h5": dataset.get("train_h5"),
        "test_h5": dataset.get("test_h5"),
        "connectivity_h5": dataset.get("connectivity_h5"),
        "sources": sorted(raw.get("sources") or []),
        "fields": _fields_identity(raw.get("fields") or {}),
        "geometry": _geometry_identity(raw.get("geometry")),
        "save_fields": sorted(raw.get("save_fields") or []),
        "filters": {
            domain: sorted(names)
            for domain, names in sorted((raw.get("filters") or {}).items())
            if isinstance(names, list)
        },
        "statistics": _statistics_identity(raw.get("statistics") or {}),
        "formats": _formats_identity(raw),
        "vtkhdf": bool(raw.get("vtkhdf")),
        "extraction": raw.get("extraction") or None,
    }


def _fields_identity(fields) -> dict:
    """只比较提取了哪些场和分量；展开默认值时多出的来源元数据不另占名称。"""
    if not isinstance(fields, dict):
        return {}
    result = {}
    for domain, items in fields.items():
        if not isinstance(items, dict):
            continue
        result[domain] = {
            name: ({"components": spec.get("components")} if isinstance(spec, dict) else spec)
            for name, spec in items.items()
        }
    return result


def _geometry_identity(value) -> dict:
    if isinstance(value, dict):
        parameters = {
            name: options
            for name, options in value.items()
            if isinstance(options, dict)
            and any(item is not None and item != {} for item in options.values())
        }
        return {"names": sorted(value), "parameters": parameters}
    if isinstance(value, list):
        return {"names": sorted(item for item in value if isinstance(item, str)), "parameters": {}}
    return {"names": [], "parameters": {}}


def _statistics_identity(value: dict) -> dict:
    return {
        "mode": value.get("mode"),
        "fields": sorted(value.get("fields") or []),
        "position_fields": sorted(value.get("position_fields") or []),
    }


def _formats_identity(raw: dict) -> list[str]:
    if raw.get("formats") is not None:
        values = list(raw.get("formats") or [])
    elif "format" in raw:
        values = [raw.get("format")]
    else:
        values = ["pt"]
    return sorted({item for item in values if isinstance(item, str)})


def _fingerprint(payload: dict) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()


def validate_manifest(manifest: Path) -> dict:
    """校验完整物理清单和声明成员；张量数值由下游公开读盘能力校验。"""
    value = json.loads(manifest.read_text())
    if value.get("version") != 1 or value.get("state") != "physical" or not value.get("samples"):
        raise ValueError("shared_dataset_invalid_manifest")
    root = manifest.parent.resolve()
    expected = [
        (str(part), str(name))
        for part, names in value.get("partitions", {}).items()
        for name in names
    ]
    actual = [
        (str(sample.get("partition")), str(sample.get("sample"))) for sample in value["samples"]
    ]
    if not expected or len(set(actual)) != len(actual) or sorted(actual) != sorted(expected):
        raise ValueError("shared_dataset_incomplete_partitions")
    stats = value.get("statistics")
    if isinstance(stats, dict) and stats.get("path"):
        statistics = Path(stats["path"])
        statistics = (
            statistics.resolve() if statistics.is_absolute() else (root / statistics).resolve()
        )
        if not statistics.is_relative_to(root):
            raise ValueError("shared_dataset_statistics_escape")
        if not statistics.is_file():
            raise FileNotFoundError(statistics)
    for sample in value["samples"]:
        if not sample.get("written"):
            raise ValueError("shared_dataset_incomplete_sample")
        path = Path(sample["path"])
        path = path.resolve() if path.is_absolute() else (root / path).resolve()
        if not path.is_relative_to(root):
            raise ValueError("shared_dataset_member_escape")
        names = set(sample.get("filemap", {}).values())
        for mapping in sample.get("format_filemaps", {}).values():
            names.update(mapping.values())
        names.update(sample.get("assets", []))
        names.update(sample.get("identity_assets", []))
        if not names:
            raise ValueError("shared_dataset_empty_sample")
        for name in names:
            target = (path / name).resolve()
            if not target.is_relative_to(root):
                raise ValueError("shared_dataset_member_escape")
            if not target.exists():
                raise FileNotFoundError(target)
    return value


def describe_dataset(manifest: str) -> dict:
    """校验科学清单，交付成员与可搬移身份，不承担发布或覆盖许可。"""
    path = Path(manifest).resolve()
    value = validate_manifest(path)
    members = [str(path)]
    stats = value.get("statistics") or {}
    if isinstance(stats, dict) and stats.get("path"):
        members.append(str((path.parent / stats["path"]).resolve()))
    for sample in value["samples"]:
        root = (path.parent / sample["path"]).resolve()
        names = set(sample.get("filemap", {}).values())
        for mapping in sample.get("format_filemaps", {}).values():
            names.update(mapping.values())
        names.update(sample.get("assets", []))
        names.update(sample.get("identity_assets", []))
        members.extend(str((root / name).resolve()) for name in sorted(names))

    def portable(item):
        if isinstance(item, dict):
            return {key: portable(child) for key, child in item.items()}
        if isinstance(item, list):
            return [portable(child) for child in item]
        if (
            isinstance(item, str)
            and Path(item).is_absolute()
            and Path(item).is_relative_to(path.parent)
        ):
            return str(Path(item).relative_to(path.parent))
        return item

    return {
        "identity": portable(value),
        "members": members,
        "semantics": {"type": "aero.physical", "format_version": 1},
    }


def dataset_copy_plan(manifest: str) -> dict:
    """描述物理数据复制及新副本的引用转换，不写原始清单。"""
    manifest = Path(manifest).resolve()
    source = manifest.parent
    value = json.loads(manifest.read_text())
    copies = [
        {"source": str(child), "target": child.name}
        for child in source.iterdir()
        if not child.name.startswith(".") and child != manifest
    ]
    dependencies = []
    for sample in value["samples"]:
        old = (source / sample["path"]).resolve()
        if not old.is_relative_to(source):
            raise ValueError("shared_dataset_member_escape")
        sample["path"] = str(old.relative_to(source))
    stats = value.get("statistics")
    if isinstance(stats, dict) and stats.get("path"):
        old = (source / stats["path"]).resolve()
        if old.is_relative_to(source):
            stats["path"] = str(old.relative_to(source))
        else:
            relative = "dependencies/statistics" + old.suffix
            copies.append({"source": str(old), "target": relative})
            stats["path"] = relative
            dependencies.append(str(old))
    original = value.get("source_manifest")
    if original and Path(original).is_file():
        relative = "dependencies/source-manifest" + Path(original).suffix
        copies.append({"source": original, "target": relative})
        value["source_manifest"] = relative
    return {
        "copies": copies,
        "documents": {manifest.name: value},
        "summary": {"samples": len(value["samples"]), "copied_dependencies": dependencies},
    }


def migration_candidates(runs: list[dict]) -> list[dict]:
    """显式旧数据迁移的领域识别；只读历史配置，返回可选择来源。"""
    from omegaconf import OmegaConf

    result = []
    for run in runs:
        if "rawprep" not in run.get("stages", []) or run.get("shared_outputs"):
            continue
        manifest = Path(run["data_dir"]) / "manifest.json"
        config = Path(run["run_dir"]) / "inputs/config.yaml"
        if not manifest.is_file() or not config.is_file():
            continue
        name = OmegaConf.select(OmegaConf.load(config), "dataset.processed_name")
        result.append(
            {
                "run_id": run["id"],
                "name": name,
                "manifest": str(manifest),
                "samples": len(json.loads(manifest.read_text()).get("samples", [])),
                "stage": "rawprep",
                "consumer_binding": "inputs.trainprep.dataset",
            }
        )
    return result
