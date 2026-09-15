"""项目内模型配置预设：只保存模型、训练和准备声明，不含权重或数据绑定。"""

import json
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import ai4e_task as task

from ai4e_task.tasks.assets import asset_path

from .model_cases import current_variant, dataset_id, describe_model_case, model_id, resolve_case

PRESET_KIND = "model_preset"
OFFICIAL_NAMES = {"abupt", "transolver3"}


def list_presets(service, project: str, dataset_key: str | None = None) -> list[dict]:
    """列出项目共享预设；可按当前数据集过滤。"""
    result = []
    for item in task.list_shared(service.project(project)):
        if item.get("kind") != PRESET_KIND:
            continue
        payload = _payload(service, project, item)
        if dataset_key and payload.get("dataset_id") != dataset_key:
            continue
        result.append({**item, "preset": payload})
    return result


def match_preset(config: dict, presets: list[dict]) -> str | None:
    """当前配置与某份预设的模型段一致时标出，不猜测。"""
    for item in presets:
        payload = item.get("preset") or {}
        if (
            payload.get("component") == (config.get("components") or {}).get("model")
            and payload.get("model") == config.get("model")
            and payload.get("trainprep") == config.get("trainprep")
        ):
            return item["id"]
    return None


def export_preset(service, project: str, identity: str, name: str, revision: str) -> dict:
    """把当前已保存配置导出为命名预设；同名拒绝覆盖。"""
    label = (name or "").strip()
    if not label:
        raise ValueError("model_preset_name_required")
    if label in OFFICIAL_NAMES:
        raise ValueError("model_preset_name_reserved")
    record = task.get_task(service.project(project), identity)
    if record.get("archived"):
        raise ValueError("task_archived")
    captured = task.read_configuration(service.project(project), identity)
    if captured["revision"] != revision:
        raise ValueError("configuration_revision_conflict")
    config = captured["config"]
    payload = {
        "kind": PRESET_KIND,
        "name": label,
        "model_id": model_id(config),
        "dataset_id": dataset_id(config),
        "variant": current_variant(config),
        "component": (config.get("components") or {}).get("model"),
        "model": deepcopy(config.get("model") or {}),
        "train": _train_snapshot(config.get("train") or {}),
        "trainprep": deepcopy(config.get("trainprep") or {}),
        "source_task": identity,
        "revision": revision,
    }
    if any(item["name"] == label for item in task.list_shared(service.project(project))):
        raise ValueError("model_preset_name_taken")
    with TemporaryDirectory() as folder:
        path = Path(folder) / "preset.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return task.register_shared(
            service.project(project),
            label,
            path,
            kind=PRESET_KIND,
            copy=True,
            provenance={"task_id": identity, "revision": revision},
        )


def describe_preset(service, project: str, identity: str, record: dict, captured: dict) -> dict:
    """把预设描述成与官方模型相同的可换模默认值。"""
    payload = record.get("preset") or _payload(service, project, record)
    if payload.get("dataset_id") != dataset_id(captured["config"]):
        raise ValueError("model_preset_dataset_mismatch")
    case_id = resolve_case(payload["dataset_id"], payload["model_id"], payload.get("variant"))
    described = (
        describe_model_case(service, project, identity, case_id, captured)
        if case_id
        else {"capabilities": {}}
    )
    train = deepcopy(payload.get("train") or described.get("train") or {})
    return {
        "id": record["id"],
        "name": payload.get("name") or record.get("name"),
        "model_id": payload["model_id"],
        "dataset_id": payload["dataset_id"],
        "variant": payload.get("variant"),
        "kind": PRESET_KIND,
        "structure_version": {"id": "preset", "name": payload.get("name") or record.get("name")},
        "component": payload.get("component") or described.get("component"),
        "model": payload.get("model") or described.get("model"),
        "train": train,
        "trainprep": payload.get("trainprep") or described.get("trainprep"),
        "capabilities": described.get("capabilities") or {},
    }


def load_preset(service, project: str, identity: str, preset_id: str, captured: dict) -> dict:
    """读取指定预设；跨数据集拒绝。"""
    record = next(
        (item for item in list_presets(service, project) if item["id"] == preset_id),
        None,
    )
    if record is None:
        raise ValueError("unknown_model_preset")
    return describe_preset(service, project, identity, record, captured)


def _payload(service, project: str, record: dict) -> dict:
    """从共享资产读回预设正文。"""
    asset = task.get_shared(service.project(project), record["id"])
    path = asset_path(service.project(project), asset)
    if path.is_dir():
        path = next(path.rglob("preset.json"), path)
    return json.loads(path.read_text())


def _train_snapshot(train: dict) -> dict:
    """导出训练默认值，去掉清单、准备和权重路径。"""
    value = deepcopy(train)
    value.pop("manifest", None)
    value.pop("preparation", None)
    value["resume"] = None
    return value

