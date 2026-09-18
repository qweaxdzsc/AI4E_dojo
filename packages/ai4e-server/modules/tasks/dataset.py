"""任务数据绑定：公开数据集与本机副本一次接入处理方式，不接受手写绝对路径。"""

from fnmatch import fnmatch
from hashlib import sha256
from json import dumps
from pathlib import Path

import ai4e_task as task
from omegaconf import OmegaConf

from ...infrastructure.content_access import resolve, roots
from ..capabilities.model_cases import CASES, case_configuration, current_variant, dataset_id, model_id as official_model_id, resolve_case

NASA_KEYS = ("train_h5", "test_h5", "connectivity_h5")
DATASET_KEYS = ("root", *NASA_KEYS)
LABELS = {"shapenet_car": "ShapeNet-Car", "nasa_crm": "NASA CRM"}
_PROFILES: dict[str, dict] = {}


def dataset_kind(config):
    """从案例声明识别绑定方式；缺 components 的历史外流任务沿用模板默认目录绑定。"""
    component = (config.get("components") or {}).get("dataset") or ""
    if str(component).endswith("nasa_crm"):
        return "nasa_crm", "files"
    if str(component).endswith("shapenet_car"):
        return "shapenet_car", "directory"
    dataset = config.get("inputs", {}).get("rawprep") or {}
    if any(dataset.get("source" if key == "root" else key) for key in NASA_KEYS):
        return "nasa_crm", "files"
    if {"rawprep", "trainprep", "model", "train", "post"} <= set(config):
        return "shapenet_car", "directory"
    raise ValueError("unsupported_dataset_binding")


def controlled_reference(service, project, path):
    """把已解析路径还原为最具体的登记数据根引用。"""
    candidates = [
        (key, base.resolve())
        for key, base in roots(service, project).items()
        if key.startswith("data") and path.is_relative_to(base.resolve())
    ]
    if not candidates:
        raise ValueError("dataset_source_outside_registered_roots")
    key, base = max(candidates, key=lambda item: len(item[1].parts))
    ref = {"root": key, "path": str(path.relative_to(base)) if path != base else ""}
    resolve(service, project, root=key, relative=ref["path"])
    return ref


def _model_id(config):
    """按模型组件识别登记模型；历史缺声明视为 AB-UPT。"""
    return official_model_id(config)


def _compatible_case(dataset_key, model_key, variant=None):
    """只允许已登记的数据集与模型组合；多变体时按当前变体或官方默认表面。"""
    return resolve_case(dataset_key, model_key, variant)


def _profile(service, project, identity, dataset_key):
    """用候选案例配置描述公开数据集，不把当前任务路径带进识别规则。"""
    cached = _PROFILES.get(dataset_key)
    if cached:
        return cached
    case_id = next(key for key, item in CASES.items() if item["dataset_id"] == dataset_key)
    raw = case_configuration(service, case_id)
    captured = task.read_configuration(service.project(project), identity)
    described = task.inspect_task(
        service.project(project),
        identity,
        "describe_rawprep",
        revision=captured["revision"],
        configuration=raw,
        output_dir=str(service.settings.root / "inspections" / f"public-{dataset_key}"),
    )
    profile = described["profile"]
    value = {
        "dataset_id": dataset_key,
        "label": LABELS.get(dataset_key, dataset_key),
        "component": raw["components"]["dataset"],
        "binding": profile["binding"],
        "defaults": profile["defaults"],
        "description": profile["binding"]["description"],
    }
    _PROFILES[dataset_key] = value
    return value


def _instance_id(dataset_key, sources):
    """副本身份只由数据集与受控引用决定，避免把本机绝对路径交给页面。"""
    payload = dumps({"dataset_id": dataset_key, "sources": sources}, sort_keys=True, ensure_ascii=True)
    return sha256(payload.encode()).hexdigest()[:16]


def _label_sources(sources):
    """用受控根与相对路径描述本机地址。"""
    return "；".join(
        f"{key}：{ref['root']} / {ref['path'] or '数据根目录'}" for key, ref in sources.items()
    )


def _has_directory_samples(directory, locate):
    """只看声明的样本父目录和标记文件，不把整库叶子走完。"""
    marker, parent_pat = locate["marker"], locate.get("sample_parent", "param*")
    for group in directory.glob(parent_pat):
        if not group.is_dir() or group.is_symlink() or group.name.startswith("."):
            continue
        if any(path.is_file() and not path.is_symlink() for path in group.glob("*/" + marker)):
            return True
    return False


def _scan_directory(service, project, locate):
    """按声明标记找出完整样本目录，缺标记不作为副本。"""
    found = []
    seen = set()

    def walk(directory, base, depth=0):
        if _has_directory_samples(directory, locate):
            key = str(directory.resolve())
            if key not in seen:
                seen.add(key)
                found.append({"root": controlled_reference(service, project, directory)})
            return
        if depth > 6:
            return
        for child in directory.iterdir():
            if (
                not child.is_dir()
                or child.is_symlink()
                or child.name.startswith(".")
                or fnmatch(child.name, locate.get("sample_parent", "param*"))
            ):
                continue
            walk(child, base, depth + 1)

    for root_id, base in roots(service, project).items():
        if not root_id.startswith("data") or not base.exists():
            continue
        walk(base, base)
    return found


def _scan_files(service, project, locate):
    """按声明文件名收集完整三件套；同名多份时优先同目录再同根。"""
    names = {name: set(values) for name, values in locate["filenames"].items()}
    found = {key: [] for key in names}
    for root_id, base in roots(service, project).items():
        if not root_id.startswith("data") or not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_symlink() or not path.is_file() or path.name.startswith("."):
                continue
            for key, aliases in names.items():
                if path.name in aliases:
                    found[key].append(controlled_reference(service, project, path))
    if any(not items for items in found.values()):
        return []

    def score(train, other):
        same_parent = 0 if Path(train["path"]).parent == Path(other["path"]).parent else 1
        same_root = 0 if train["root"] == other["root"] else 1
        return (same_parent, same_root, other["root"], other["path"])

    instances = []
    seen = set()
    for train in found["train_h5"]:
        sources = {
            "train_h5": train,
            "test_h5": min(found["test_h5"], key=lambda item: score(train, item)),
            "connectivity_h5": min(found["connectivity_h5"], key=lambda item: score(train, item)),
        }
        identity = _instance_id("nasa_crm", sources)
        if identity in seen:
            continue
        seen.add(identity)
        instances.append(sources)
    return instances


def _instances(service, project, profile):
    """只返回识别规则判定完整的本机副本。"""
    locate = profile["binding"].get("locate") or {}
    mode = locate.get("mode") or profile["binding"]["mode"]
    raw = (
        _scan_directory(service, project, locate)
        if mode == "directory"
        else _scan_files(service, project, locate)
        if mode == "files"
        else []
    )
    result = []
    for sources in raw:
        identity = _instance_id(profile["dataset_id"], sources)
        result.append(
            {
                "id": identity,
                "label": _label_sources(sources),
                "sources": sources,
            }
        )
    return result


def list_public_datasets(service, project, identity):
    """列出 contrib 公开数据集、处理说明和本机完整副本。"""
    task.get_task(service.project(project), identity)
    captured = task.read_configuration(service.project(project), identity)
    current = dataset_id(captured["config"])
    model_key = _model_id(captured["config"])
    datasets = []
    seen = []
    for item in CASES.values():
        key = item["dataset_id"]
        if key in seen:
            continue
        seen.append(key)
        profile = _profile(service, project, identity, key)
        datasets.append(
            {
                "dataset_id": key,
                "label": profile["label"],
                "description": profile["description"],
                "binding_mode": profile["binding"]["mode"],
                "compatible": _compatible_case(key, model_key) is not None,
                "instances": _instances(service, project, profile),
            }
        )
    return {
        "revision": captured["revision"],
        "current_dataset_id": current,
        "model_id": model_key,
        "datasets": datasets,
    }


def read_binding(service, project, identity):
    """动态核验来源的范围、存在和类型；不把文件存在冒充完整样本检查。"""
    value = task.read_configuration(service.project(project), identity)
    profile = task.describe_rawprep(service.project(project), identity)["profile"]
    kind, mode = profile["dataset_id"], profile["binding"]["mode"]
    slots = profile["binding"]["slots"]
    keys = [slot["key"] for slot in slots]
    sources, errors = {}, []
    dataset = OmegaConf.create(value["config"]).get("inputs", {}).get("rawprep", {})
    supplied = False
    for key in keys:
        try:
            raw = dataset.get("source" if key == "root" else key)
            if not raw:
                errors.append({"location": key, "code": "dataset_source_unbound"})
                continue
            supplied = True
            path = Path(raw).expanduser().resolve()
            ref = controlled_reference(service, project, path)
            if not (path.is_file() if mode == "files" else path.is_dir()):
                raise ValueError("dataset_source_type_mismatch")
            sources[key] = ref
        except (ValueError, OSError, KeyError, TypeError):
            errors.append({"location": key, "code": "dataset_source_invalid"})
    return {
        "revision": value["revision"],
        "dataset_id": kind,
        "label": LABELS.get(kind, kind),
        "binding_mode": mode,
        "binding_schema": profile["binding"],
        "status": "invalid" if errors and supplied else "unbound" if errors else "valid",
        "sources": sources,
        "location": _label_sources(sources) if sources else "",
        "errors": errors,
    }


def _write_sources(service, project, identity, sources, expected_revision, *, dataset_key=None):
    """原子保存目录或文件引用；换数据集时同时替换处理组件与默认。"""
    value = task.read_configuration(service.project(project), identity)
    if value["revision"] != expected_revision:
        raise ValueError("configuration_revision_conflict")
    current = dataset_id(value["config"])
    target = dataset_key or current
    if target != current:
        if _compatible_case(target, _model_id(value["config"]), current_variant(value["config"])) is None:
            raise ValueError("dataset_model_case_missing")
    profile = (
        _profile(service, project, identity, target)
        if target != current
        else {
            "dataset_id": current,
            "component": (value["config"].get("components") or {}).get("dataset"),
            "binding": task.describe_rawprep(service.project(project), identity)["profile"]["binding"],
            "defaults": None,
        }
    )
    mode = profile["binding"]["mode"]
    allowed = {slot["key"] for slot in profile["binding"]["slots"]}
    if set(sources) != allowed:
        raise ValueError("dataset_sources_required: " + ", ".join(sorted(allowed)))
    paths = {key: None for key in (*DATASET_KEYS, "manifest")} if target != current else {}
    for key, ref in sources.items():
        if (
            set(ref) != {"root", "path"}
            or not isinstance(ref["root"], str)
            or not ref["root"].startswith("data")
        ):
            raise ValueError("controlled_dataset_source_required: " + key)
        path = resolve(service, project, ref["root"], ref["path"])
        if not (path.is_file() if mode == "files" else path.is_dir()):
            raise ValueError("dataset_source_type_mismatch: " + key)
        paths[key] = str(path)
    if mode == "files":
        paths["root"] = str(Path(paths[profile["binding"]["root_key"]]).parent)
    paths["source"] = paths.pop("root", None)
    patch = {"inputs": {"rawprep": paths}}
    replace = ()
    if target != current:
        components = dict(value["config"].get("components") or {})
        components["dataset"] = profile["component"]
        patch["components"] = components
        patch["rawprep"] = profile["defaults"]
        replace = ("rawprep",)
    task.save_configuration(
        service.project(project), identity, patch, revision=expected_revision, replace_sections=replace
    )
    return read_binding(service, project, identity)


def save_binding(service, project, identity, sources, expected_revision, dataset_id=None, instance_id=None):
    """保存受控来源；公开副本一次写入处理方式与本机地址。"""
    if dataset_id and instance_id:
        catalog = list_public_datasets(service, project, identity)
        chosen = next((item for item in catalog["datasets"] if item["dataset_id"] == dataset_id), None)
        if chosen is None:
            raise ValueError("unknown_public_dataset")
        if not chosen["compatible"]:
            raise ValueError("dataset_model_case_missing")
        instance = next((item for item in chosen["instances"] if item["id"] == instance_id), None)
        if instance is None:
            raise ValueError("dataset_instance_unavailable")
        return _write_sources(
            service,
            project,
            identity,
            instance["sources"],
            expected_revision,
            dataset_key=dataset_id,
        )
    if not sources:
        raise ValueError("dataset_sources_required")
    return _write_sources(service, project, identity, sources, expected_revision)
