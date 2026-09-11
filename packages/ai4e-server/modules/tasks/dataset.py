"""任务数据绑定：仅保存受控来源，数据内容校验仍由案例检查进程负责。"""

from pathlib import Path

import ai4e_task as task
from omegaconf import OmegaConf

from ...infrastructure.content_access import resolve, roots

NASA_KEYS = ("train_h5", "test_h5", "connectivity_h5")


def dataset_kind(config):
    """从案例声明识别绑定方式；缺 components 的历史外流任务沿用模板默认目录绑定。"""
    component = (config.get("components") or {}).get("dataset") or ""
    if str(component).endswith("nasa_crm"):
        return "nasa_crm", "files"
    if str(component).endswith("shapenet_car"):
        return "shapenet_car", "directory"
    dataset = config.get("dataset") or {}
    if any(key in dataset for key in NASA_KEYS):
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


def read_binding(service, project, identity):
    """动态核验来源的范围、存在和类型；不把文件存在冒充完整样本检查。"""
    value = task.read_configuration(service.project(project), identity)
    kind, mode = dataset_kind(value["config"])
    keys = NASA_KEYS if mode == "files" else ("root",)
    sources, errors = {}, []
    dataset = OmegaConf.create(value["config"]).get("dataset", {})
    supplied = False
    for key in keys:
        try:
            raw = dataset.get(key)
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
        "binding_mode": mode,
        "status": "invalid" if errors and supplied else "unbound" if errors else "valid",
        "sources": sources,
        "errors": errors,
    }


def save_binding(service, project, identity, sources, expected_revision):
    """原子保存目录或文件引用到任务 YAML，其他配置保持原样。"""
    value = task.read_configuration(service.project(project), identity)
    if value["revision"] != expected_revision:
        raise ValueError("configuration_revision_conflict")
    _, mode = dataset_kind(value["config"])
    allowed = set(NASA_KEYS) if mode == "files" else {"root"}
    if set(sources) != allowed:
        raise ValueError("dataset_sources_required: " + ", ".join(sorted(allowed)))
    paths = {}
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
        paths["root"] = str(Path(paths["train_h5"]).parent)
    task.save_configuration(
        service.project(project), identity, {"dataset": paths}, revision=expected_revision
    )
    return read_binding(service, project, identity)
