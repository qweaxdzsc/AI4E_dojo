"""阶段用例：捕获配置、检查受控输入并编排 task 公开操作。"""

import json
import logging
from datetime import UTC, datetime
from functools import lru_cache
from pathlib import Path
from subprocess import TimeoutExpired
from uuid import uuid4

import ai4e_task as task
from omegaconf import OmegaConf

from ..visualization import asset, register, submit_model_inspection
from .domain import (
    ALLOWED_BINDINGS,
    CHECKPOINT_TAGS,
    OperationCommand,
    execution_stages,
    field_matching_catalog,
    is_settings_save,
    legacy_slice_patch,
    normalize_field_scales,
    published_slices,
    reject_statistics,
    required_inputs,
    selected_input_keys,
    settings_digest,
    split_catalog,
    validate_field_bindings,
    validate_field_scales,
    validate_split,
    validate_stage,
)


def _read_manifest(config):
    """读取已绑定物理清单 JSON，路径无效时退回配置声明。"""
    path = (config.get("inputs", {}).get("trainprep") or {}).get("dataset")
    if not isinstance(path, str) or not path:
        return None
    file = Path(path)
    if not file.is_file():
        return None
    try:
        return json.loads(file.read_text())
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None


@lru_cache(maxsize=16)
def _describe_case(project: str, identity: str, revision: str, output_root: str):
    """同一配置修订只起一次检查进程；切步骤不再重复描述案例。"""
    return task.inspect_task(
        project,
        identity,
        "describe_case",
        revision=revision,
        output_dir=str(Path(output_root) / "inspections" / uuid4().hex),
    )


def configuration(project: str, identity: str, service, stage: str | None = None):
    """读取任务 YAML 中的用户配置，不建立第二份配置。"""
    value = _migrate_legacy_slices(service, service.project(project), identity)
    if stage:
        validate_stage(stage)
        try:
            described = _describe_case(
                str(service.project(project)),
                identity,
                value["revision"],
                str(service.settings.root),
            )
        except (ValueError, OSError, TimeoutExpired, TypeError, AttributeError) as exc:
            logging.getLogger(__name__).warning("任务能力检查失败 task=%s", identity, exc_info=True)
            described = {
                "capabilities": {
                    "unavailable_reason": (
                        "当前配置或数据输入尚未就绪，请核对数据绑定后重新检查。"
                        if any(
                            marker in str(exc)
                            for marker in ("TypeError", "AttributeError", "NoneType", "Traceback")
                        )
                        else str(exc).splitlines()[-1][:600]
                    ),
                    "status": "unavailable",
                }
            }
        full_config = normalize_field_scales(described.get("configuration") or value["config"])
        capabilities = _capability_options(described)
        if stage == "trainprep":
            manifest = _read_manifest(full_config)
            capabilities["field_matching"] = field_matching_catalog(full_config, manifest)
            capabilities["split"] = split_catalog(manifest)
            try:
                from ..capabilities.model_cases import preparation_combos

                capabilities["preparation_combos"] = preparation_combos(full_config)
            except ValueError:
                capabilities["preparation_combos"] = {"current_id": None, "options": []}
        if stage in {"model", "train"}:
            try:
                from ..capabilities.model_cases import official_combos

                capabilities["official_combos"] = official_combos(full_config)
            except ValueError:
                capabilities["official_combos"] = {"current_model_id": None, "options": []}
        return {
            "task_id": identity,
            "revision": value["revision"],
            "stage": stage,
            "values": full_config.get(stage, {}),
            "capabilities": capabilities,
            "readiness": {"status": "unchecked"},
        }
    return dict(task_id=identity, **value)


def save(
    project: str,
    identity: str,
    stage: str,
    values: dict,
    revision: str,
    service,
    bindings: dict | None = None,
    target_case_id: str | None = None,
    target_model: str | None = None,
    target_variant: str | None = None,
    target_preset: str | None = None,
    edited_paths: list[list[str]] | None = None,
    removed_paths: list[list[str]] | None = None,
):
    """核对修订保存阶段草稿；显式换模同时替换关联默认值并解除旧输入。换模后的完整稿补上缺的训练切片键，避免随后打开配置再改修订。"""
    validate_stage(stage)
    if edited_paths is None:
        reject_statistics(values)
    else:
        for path in edited_paths:
            value = values
            for key in path:
                if not isinstance(value, dict) or key not in value:
                    raise ValueError("configuration_edit_value_missing")
                value = value[key]
            if path:
                reject_statistics({path[-1]: value})
    from copy import deepcopy

    from .configuration import compose_configuration

    current = task.read_configuration(service.project(project), identity)
    if current["revision"] != revision:
        raise ValueError("configuration_revision_conflict")
    patch = compose_configuration(
        current["config"],
        stage,
        values,
        edited_paths=edited_paths,
        removed_paths=removed_paths,
    )
    loading_prep_combo = stage == "trainprep" and target_case_id is not None
    loading_page_combo = (
        stage in {"model", "train"}
        and target_case_id is not None
        and target_model is None
        and target_preset is None
    )
    switching = (not loading_prep_combo and not loading_page_combo) and any(
        item is not None for item in (target_case_id, target_model, target_preset)
    )
    clear_model_inputs = False
    if loading_page_combo:
        from ..capabilities.model_cases import CASES, model_id, official_page_values

        if target_case_id not in CASES:
            raise ValueError("unknown_registered_case")
        if model_id(current["config"]) != CASES[target_case_id]["model_id"]:
            raise ValueError("official_combo_model_mismatch")
        official = official_page_values(service, target_case_id, stage)
        if stage == "model":
            next_model = deepcopy(official)
            patch["model"] = next_model
        else:
            current_train = current["config"].get("train") or {}
            next_train = deepcopy(current_train)
            next_train.update(official)
            for key in ("manifest", "preparation", "resume"):
                if key in current_train:
                    next_train[key] = current_train.get(key)
                else:
                    next_train.pop(key, None)
            patch["train"] = next_train
    elif loading_prep_combo:
        if target_model is not None or target_preset is not None:
            raise ValueError("preparation_combo_requires_case")
        from ..capabilities.model_cases import CASES, dataset_id, describe_model_case, model_id

        if target_case_id not in CASES:
            raise ValueError("unknown_registered_case")
        if CASES[target_case_id]["dataset_id"] != dataset_id(current["config"]):
            raise ValueError("model_case_dataset_mismatch")
        target = describe_model_case(service, project, identity, target_case_id, current)
        next_prep = deepcopy(target["trainprep"])
        current_split = current["config"].get("trainprep", {}).get("split")
        if current_split:
            next_prep["split"] = deepcopy(current_split)
        if model_id(current["config"]) == CASES[target_case_id]["model_id"]:
            patch["trainprep"] = next_prep
        else:
            clear_model_inputs = True
            train = deepcopy(target["train"])
            patch.update(
                {"train": train, "trainprep": next_prep, "model": deepcopy(target["model"])}
            )
            patch["components"] = {
                **current["config"].get("components", {}),
                "model": target["component"],
            }
            patch["model"].pop("initial_weights", None)
    elif switching:
        if stage != "model":
            raise ValueError("model_case_requires_model_stage")
        current = task.read_configuration(service.project(project), identity)
        if current["revision"] != revision:
            raise ValueError("configuration_revision_conflict")
        target = _switch_target(
            service,
            project,
            identity,
            current,
            target_case_id,
            target_model,
            target_variant,
            target_preset,
        )
        train = deepcopy(target["train"])
        # 不把案例默认物理清单路径带入用户任务；即便未绑定也明确保持空引用。
        patch.update(
            {
                "train": train,
                "trainprep": deepcopy(target["trainprep"]),
                "components": {"model": target["component"]},
            }
        )
        patch["model"] = deepcopy(values)
        patch["components"] = {
            **current["config"].get("components", {}),
            "model": target["component"],
        }
        patch["model"].pop("initial_weights", None)
        clear_model_inputs = True
    if clear_model_inputs:
        inputs = patch.setdefault("inputs", {})
        inputs.setdefault("train", {}).update(preparation=None, resume=None, initial_weights=None)
        inputs.setdefault("infer", {}).update(preparation=None, checkpoint=None)
        inputs.setdefault("post", {})["results"] = None
    for key, reference in (bindings or {}).items():
        if key not in ALLOWED_BINDINGS:
            raise ValueError("unsupported_stage_binding")
        if clear_model_inputs and key != "inputs.trainprep.dataset":
            # 换模不能在同一命令中把刚解除的旧准备或权重重新写回。
            if reference is not None:
                raise ValueError("model_switch_requires_new_preparation")
            continue
        resolved = None if reference is None else str(asset(service, project, reference))
        section = patch
        parts = key.split(".")
        for part in parts[:-1]:
            section = section.setdefault(part, {})
            if not isinstance(section, dict):
                raise ValueError("invalid_stage_binding_structure: " + key)  # noqa: TRY004 - 统一配置业务错误
        section[parts[-1]] = resolved
    patch = normalize_field_scales(patch)
    extra = legacy_slice_patch(patch)
    if extra:
        patch = OmegaConf.to_container(
            OmegaConf.merge(OmegaConf.create(patch), OmegaConf.create(extra)),
            resolve=False,
        )
    if stage == "trainprep":
        manifest = _read_manifest(patch)
        matching = field_matching_catalog(patch, manifest)
        validate_field_bindings(patch[stage], matching["model_roles"], matching["dataset_fields"])
        validate_field_scales(patch[stage])
        validate_split(patch[stage], manifest)
    saved = task.replace_configuration(
        service.project(project),
        identity,
        patch,
        revision=revision,
    )
    if stage in {"model", "train"}:
        _record_settings_completion(service, project, identity, stage, saved)
    return saved


def _record_settings_completion(service, project, identity, stage, saved):
    """保存模型/训练设置后记下本页完成；只有再次保存才改写，检查不能冒充。"""
    mapped = "training" if stage == "train" else "model"
    key = "settings-check:" + project + ":" + identity + ":" + mapped
    service.store.put(
        "operation",
        key,
        {
            "operation_id": key,
            "project_id": project,
            "kind": "validate_configuration",
            "source": "save",
            "task_id": identity,
            "created_at": datetime.now(UTC).isoformat(),
            "revision": saved["revision"],
            "stage": mapped,
            "inputs": [],
            "status": "succeeded",
            "section_digest": settings_digest(saved["config"], mapped),
            "error": None,
            "result_refs": [],
            "event_cursor": 0,
            "fingerprint": key,
            "idempotency_key": key,
        },
    )


def _switch_target(
    service,
    project,
    identity,
    current,
    target_case_id,
    target_model,
    target_variant,
    target_preset,
):
    """按官方模型、变体或用户预设解析换模目标。"""
    from ..capabilities import describe_model_case, describe_official_model, load_preset
    from ..capabilities.model_cases import dataset_id

    if target_preset:
        return load_preset(service, project, identity, target_preset, current)
    if target_model:
        return describe_official_model(
            service, project, identity, target_model, current, target_variant
        )
    if target_case_id:
        from ..capabilities.model_cases import CASES, resolve_case

        if target_case_id in CASES:
            return describe_model_case(service, project, identity, target_case_id, current)
        kind = dataset_id(current["config"])
        resolved = resolve_case(kind, target_case_id)
        if resolved:
            return describe_model_case(service, project, identity, resolved, current)
        raise ValueError("unknown_registered_case")
    raise ValueError("model_switch_target_required")


def capabilities(project: str, identity: str, service):
    """在 task 检查进程查询实际案例能力。"""
    value = task.read_configuration(service.project(project), identity)
    described = task.inspect_task(
        service.project(project),
        identity,
        "describe_case",
        revision=value["revision"],
        output_dir=str(service.settings.root / "inspections" / uuid4().hex),
    )

    described["capabilities"] = _capability_options(described)
    return described


def _capability_options(described):
    """把生产者声明的枚举范围适配为前端选项；未知范围不擅自扩大。"""
    capabilities = dict(described.get("capabilities", {}))
    options = {}
    for key, descriptor in capabilities.get("parameter_descriptors", {}).items():
        allowed = descriptor.get("allowed")
        if allowed is not None:
            options[key] = allowed
    for key, constraint in capabilities.get("training_constraints", {}).items():
        if "allowed" in constraint:
            options[key] = constraint["allowed"]
    train = described.get("configuration", {}).get("train", {})
    for key in (
        "optimizer",
        "precision",
        "device",
        "scheduler",
        "scheduler_unit",
        "parameter_group_policy",
        "evaluation_split",
    ):
        if key not in options and key in train:
            options[key] = [train[key]]
    capabilities["training_options"] = options
    return capabilities


def model_inspection(project: str, identity: str, body: OperationCommand, service):
    """跟踪任务真实模型；来源由后台解析，不回写任务绑定。"""
    captured = task.read_configuration(service.project(project), identity)
    if captured["revision"] != body.expected_revision:
        raise ValueError("configuration_revision_conflict")
    _migrate_official_scripts(service, service.project(project), identity)
    captured = _migrate_legacy_slices(service, service.project(project), identity)
    selection, inputs = _trace_selection(service, project, identity)
    return submit_model_inspection(
        service,
        project,
        identity,
        captured["revision"],
        selection,
        inputs,
        body.idempotency_key,
    )


def _trace_selection(service, project, identity):
    """把最近可用物理来源登记为当次检查输入。"""
    from ...infrastructure.content_access import roots
    from ..capabilities.trace_source import latest_trace_source

    source = latest_trace_source(service, project, identity)
    bindings = {}
    inputs = []
    visible = {name: path.resolve() for name, path in roots(service, project, identity).items()}
    for key, location in source.items():
        path = Path(location).resolve()
        root_id = next(
            (name for name, root in visible.items() if path.is_relative_to(root)),
            None,
        )
        if root_id is None:
            raise ValueError("请先完成原始处理后再生成真实模型结构")
        ref = register(service, project, root_id, str(path.relative_to(visible[root_id])), identity)
        bindings[key] = str(path)
        inputs.append(ref)
    return {"stage": "model", "bindings": bindings}, inputs


def _inspect(project, identity, body, service, operation):
    selection = _inspection_selection(service, project, body)
    digest = None
    if operation == "validate_configuration":
        captured = task.read_configuration(service.project(project), identity)
        digest = settings_digest(
            captured["config"], selection.get("stage") or body.selection.get("stage")
        )
    return submit_model_inspection(
        service,
        project,
        identity,
        body.expected_revision,
        selection,
        body.inputs,
        body.idempotency_key,
        operation=operation,
        section_digest=digest,
    )


def _inspection_selection(service, project, body):
    selection = dict(body.selection)
    binding_paths = {}
    for key, source in selection.get("bindings", {}).items():
        if (
            key
            not in {
                "inputs.trainprep.dataset",
                "inputs.train.preparation",
                "inputs.infer.checkpoint",
                "inputs.trainprep.statistics",
            }
            or source not in body.inputs
        ):
            raise ValueError("invalid_inspection_binding")
        binding_paths[key] = str(asset(service, project, source))
    selection["bindings"] = binding_paths
    return selection


def operation(project: str, identity: str, stage: str, body: OperationCommand, service):
    """检查不创建运行；每次正式提交按当次平台选择合成运行配置，不夹带其他页留下的输入。"""
    validate_stage(stage)
    base = service.project(project)
    captured = task.read_configuration(base, identity)
    if captured["revision"] != body.expected_revision:
        raise ValueError("configuration_revision_conflict")
    if task.get_task(base, identity).get("archived") or task.open_project(base).get("archived"):
        raise ValueError("archived")
    _migrate_official_scripts(service, base, identity)
    captured = _migrate_legacy_slices(service, base, identity)
    revision = captured["revision"]
    for source in body.inputs:
        asset(service, project, source)
    bindings = body.selection.get("bindings", {})
    if set(bindings) - ALLOWED_BINDINGS:
        raise ValueError("unsupported_stage_binding")
    resolved = {}
    for key, source in bindings.items():
        if source not in body.inputs:
            raise ValueError("binding_requires_fixed_input")
        resolved[key] = str(asset(service, project, source))
    if stage in {"train", "model"} or "inputs.train.preparation" in bindings:
        preparation = _selected_preparation(captured["config"], resolved)
        if preparation:
            _require_current_preparation(preparation)
    if body.mode == "check":
        body.selection["stage"] = stage
        body.expected_revision = revision
        return _inspect(project, identity, body, service, "validate_configuration")
    stages = execution_stages(stage, body.mode, body.selection)
    config = normalize_field_scales(captured["config"])
    overrides = ["pipeline.stages=" + json.dumps(stages)]
    # 研究参数取已保存配置并写成现行声明；平台输入由本次选择覆盖或按准备记录生成。
    overrides += [
        key + "=" + json.dumps(value) for key, value in config.items() if key != "pipeline"
    ]
    for key, path in resolved.items():
        overrides.append(key + "=" + json.dumps(path))
    if stage == "train" or "inputs.train.preparation" in bindings:
        _overlay_composed_train_inputs(overrides, config, bindings, resolved)
    if "samples" in body.selection:
        overrides.append("dataset.samples=" + json.dumps(body.selection["samples"]))
    required_bindings = required_inputs(stage, stages)
    if stage == "post" and (
        "inputs.post.results" in bindings
        or captured["config"].get("inputs", {}).get("post", {}).get("results")
    ):
        required_bindings = ["inputs.post.results"]
    for key in required_bindings:
        if key not in bindings and not OmegaConf.select(OmegaConf.create(captured["config"]), key):
            raise ValueError("stage_input_required: " + key)
    for source in body.inputs:
        asset(service, project, source)
    declared = task.recipe_entry(base, identity).get("inputs", {})
    result = task.submit_run(
        base,
        identity,
        overrides=overrides,
        idempotency_key=body.idempotency_key,
        expected_revision=revision,
        operation_mode=body.mode,
        input_keys=selected_input_keys(stages, declared),
        overwrite=bool(body.selection.get("overwrite", False)),
    )
    service.store.put(
        "run_mode",
        result["id"],
        {
            "project_id": project,
            "run_id": result["id"],
            "mode": body.mode,
            "stage": stage,
            "revision": revision,
            "inputs": body.inputs,
        },
    )
    return dict(**result, mode=body.mode, stage=stage)


def _migrate_official_scripts(service, project, identity):
    """只替换已核验摘要的旧官方包装；现行模板或用户改过的脚本保持不动。"""
    template = getattr(service.settings, "template", None)
    if template is None:
        return
    recipe = Path(task.get_task(project, identity)["directory"]) / "recipe"
    expected = task.verified_old_sources(recipe)
    if not expected:
        return
    from ..capabilities.model_cases import current_variant, dataset_id, model_id, resolve_case

    config = task.read_configuration(project, identity)["config"]
    case = resolve_case(dataset_id(config), model_id(config), current_variant(config))
    if case is None:
        raise ValueError("migration_registered_case_required")
    source = Path(template).parent.parent / "examples/aero_cfd" / case
    if not source.is_dir():
        raise ValueError("migration_registered_case_missing")
    task.migrate_official_aero_scripts(project, identity, source, expected_sources=expected)


def _migrate_legacy_slices(_service, project, identity):
    """缺的训练切片和旧 validation 写回配置，不新建研究版本。"""
    captured = task.read_configuration(project, identity)
    patch = legacy_slice_patch(captured["config"])
    if not patch:
        return captured
    return task.save_configuration(project, identity, patch, revision=captured["revision"])


def _selected_preparation(config, resolved) -> str | None:
    """当次绑定优先，否则读现行 inputs 或旧顶层 train.preparation。"""
    if resolved.get("inputs.train.preparation"):
        return resolved["inputs.train.preparation"]
    train_inputs = (config.get("inputs") or {}).get("train") or {}
    value = train_inputs.get("preparation") or (config.get("train") or {}).get("preparation")
    return value if isinstance(value, str) and value else None


def _require_current_preparation(path):
    """平台只消费现行 version=2 准备，旧物理记录必须重新生成。"""
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("preparation_requires_regeneration") from exc
    if not isinstance(record, dict) or record.get("version") != 2:
        raise ValueError("preparation_requires_regeneration")


def _preparation_manifest(path) -> str | None:
    """从本次选中的准备记录取出冻结清单，没有就不写清单。"""
    if not path:
        return None
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return None
    value = record.get("manifest")
    return value if isinstance(value, str) and value else None


def _overlay_composed_train_inputs(overrides, config, bindings, resolved):
    """消费准备时按当次选择生成清单并清掉未再选的续训，不沿用其他页留下的路径。"""
    prep = _selected_preparation(config, resolved)
    if not prep:
        return
    if "inputs.trainprep.dataset" not in bindings:
        overrides.append("inputs.trainprep.dataset=" + json.dumps(_preparation_manifest(prep)))
    if "inputs.train.resume" not in bindings:
        overrides.append("inputs.train.resume=null")


def _name_for_manifest(base, path, names_by_manifest: dict[str, str] | None = None) -> str | None:
    """共享清单路径还原用户登记的数据集名称，不暴露绝对路径。"""
    try:
        resolved = Path(path).expanduser().resolve()
    except (OSError, TypeError, ValueError):
        return None
    key = str(resolved)
    if names_by_manifest and key in names_by_manifest:
        return names_by_manifest[key]
    try:
        for item in task.list_shared_datasets(base):
            if Path(item["manifest_path"]).resolve() == resolved:
                return item["name"]
    except (OSError, TypeError, ValueError, KeyError):
        pass
    parts = resolved.parts
    for index, part in enumerate(parts):
        if (
            part == "datasets"
            and index > 0
            and parts[index - 1] == "shared"
            and index + 1 < len(parts)
        ):
            return parts[index + 1]
    return None


def _preparation_run_config(item: dict, artifact_path: Path | None):
    """读这次准备运行当时的配置，不依赖 get_run 收据。"""
    from omegaconf import OmegaConf
    from omegaconf.errors import OmegaConfBaseException

    candidates = []
    if artifact_path is not None:
        candidates.append(artifact_path.parent.parent / "inputs/config.yaml")
    run_id = item.get("run_id")
    if run_id and artifact_path is not None:
        candidates.append(artifact_path.parents[1] / "inputs/config.yaml")
    for cfg_path in candidates:
        if not cfg_path.is_file():
            continue
        try:
            return OmegaConf.to_container(OmegaConf.load(cfg_path), resolve=True) or {}
        except (OSError, TypeError, ValueError, OmegaConfBaseException):
            continue
    return {}


def _preparation_record(path):
    """读一份准备记录；坏文件当空映射，不挡阶段输入列表。"""
    if path is None:
        return {}
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, TypeError, ValueError, json.JSONDecodeError):
        return {}
    return record if isinstance(record, dict) else {}


def _preparation_dataset_name(
    base,
    item: dict,
    artifact_path: Path | None,
    names_by_manifest: dict[str, str] | None = None,
) -> str | None:
    """准备产物展示数据准备时选中的平台数据集名称，不用运行短号或文件名。"""
    cfg = _preparation_run_config(item, artifact_path)
    candidates: list[Path] = []
    if artifact_path is not None and artifact_path.is_file():
        try:
            record = json.loads(artifact_path.read_text())
            if isinstance(record, dict) and record.get("manifest"):
                candidates.append(Path(record["manifest"]))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    manifest = (cfg.get("inputs", {}).get("trainprep") or {}).get("dataset")
    if manifest:
        candidates.append(Path(manifest))
    for path in candidates:
        name = _name_for_manifest(base, path, names_by_manifest)
        if name:
            return name
    name = (cfg.get("dataset") or {}).get("processed_name")
    if name:
        return str(name)
    return None


def stage_inputs(project: str, identity: str, service):
    """列出正式产物与配置固定来源；失效来源保留位置，不泄露绝对路径。"""
    from pathlib import Path

    from omegaconf import OmegaConf
    from omegaconf.errors import OmegaConfBaseException

    from ...infrastructure.content_access import roots

    base = service.project(project)
    configuration = OmegaConf.create(task.read_configuration(base, identity)["config"])
    task_record = task.get_task(base, identity)
    recipe = Path(task_record["directory"]) / "recipe"
    config_dir = (recipe / task_record.get("entry", {}).get("config", "config.yaml")).parent
    declared = {}
    invalid = {}
    for binding in sorted(ALLOWED_BINDINGS):
        try:
            value = OmegaConf.select(configuration, binding)
            if value is None or value == "":
                continue
            if not isinstance(value, str):
                invalid[binding] = "invalid_binding_path"
                continue
            if binding in {"inputs.infer.checkpoint"} and value in CHECKPOINT_TAGS:
                continue
            declared[binding] = (config_dir / Path(value).expanduser()).resolve()
        except (ValueError, TypeError, OmegaConfBaseException):
            invalid[binding] = "binding_resolution_failed"
    visible = {name: root.resolve() for name, root in roots(service, project, identity).items()}
    result = []
    found = set()
    covered = set()
    from ..datasets.application import as_stage_inputs

    names_by_manifest: dict[str, str] = {}
    for item in as_stage_inputs(service, project, identity):
        path = None
        if item.get("ref"):
            try:
                from ..visualization.application import locate

                path = locate(service, project, item["ref"])
            except (ValueError, FileNotFoundError, KeyError):
                path = None
        if path and item.get("processed_name"):
            names_by_manifest[str(Path(path).resolve())] = item["processed_name"]
        selected = bool(path and declared.get("inputs.trainprep.dataset") == Path(path).resolve())
        if selected:
            found.add("inputs.trainprep.dataset")
        if item.get("ref"):
            covered.add(item["ref"]["asset_id"])
        result.append({**item, "selected": selected})
    for item in task.list_stage_artifacts(base, identity, visible):
        root_id = item.get("root", "project")
        root = visible.get(root_id, Path(base).resolve())
        ref = register(service, project, root_id, item["path"], identity, integrity="stat")
        if item["binding"] == "inputs.trainprep.dataset" and ref["asset_id"] in covered:
            if declared.get(item["binding"]) == (root / item["path"]).resolve():
                found.add(item["binding"])
            continue
        selected = declared.get(item["binding"]) == (root / item["path"]).resolve()
        if selected:
            found.add(item["binding"])
        if item["binding"] == "inputs.trainprep.dataset":
            covered.add(ref["asset_id"])
        row = {
            "binding": item["binding"],
            "run_id": item["run_id"],
            "name": item["name"],
            "selected": selected,
            "origin": "run",
            "compatibility": {"status": "unchecked", "reason": "requires_configuration_check"},
            "ref": ref,
        }
        if item["binding"] == "inputs.train.preparation":
            artifact = root / item["path"]
            name = _preparation_dataset_name(base, item, artifact, names_by_manifest)
            if name:
                row["processed_name"] = name
            row["slices"] = published_slices(_preparation_record(artifact))
        result.append(row)
    for binding, path in declared.items():
        if binding in found:
            continue
        locations = [(name, root) for name, root in visible.items() if path.is_relative_to(root)]
        if not locations:
            if not path.is_file():
                continue
            invalid[binding] = "path_outside_root"
            continue
        if not path.is_file():
            invalid[binding] = "binding_file_missing"
            continue
        root_id, root = locations[0]
        try:
            ref = register(
                service,
                project,
                root_id,
                str(path.relative_to(root)),
                identity,
                integrity="stat",
            )
        except (ValueError, FileNotFoundError):
            invalid[binding] = "binding_source_unavailable"
            continue
        if binding == "inputs.trainprep.dataset" and ref["asset_id"] in covered:
            found.add(binding)
            continue
        row = {
            "binding": binding,
            "run_id": None,
            "name": path.name,
            "selected": True,
            "origin": "configuration",
            "ref": ref,
            "compatibility": {"status": "unchecked", "reason": "requires_configuration_check"},
        }
        if binding == "inputs.train.preparation":
            name = _preparation_dataset_name(base, {"run_id": None}, path, names_by_manifest)
            if not name:
                name = (
                    OmegaConf.to_container(configuration, resolve=False).get("dataset") or {}
                ).get("processed_name")
            if name:
                row["processed_name"] = name
            row["slices"] = published_slices(_preparation_record(path))
        result.append(row)
    for binding, reason in invalid.items():
        result.append(
            {
                "binding": binding,
                "run_id": None,
                "name": "已绑定来源不可用",
                "selected": False,
                "origin": "configuration",
                "ref": None,
                "compatibility": {"status": "invalid", "reason": reason, "location": binding},
            }
        )
    return result


def stage_summary(project: str, identity: str, service):
    """将研究事实与辅助检查关联；过期检查不改写历史操作终态。"""
    value = task.read_configuration(service.project(project), identity)
    result = task.get_stage_summary(service.project(project), identity)
    result.update(
        {stage: {"status": "unchecked", "operation_id": None} for stage in ("model", "training")}
    )
    for operation in sorted(
        service.store.list("operation"), key=lambda item: item.get("created_at", "")
    ):
        if operation.get("project_id") != project or operation.get("task_id") != identity:
            continue
        if operation.get("kind") not in {"trace_model", "validate_configuration"}:
            continue
        stage = operation.get("stage")
        if stage == "train":
            stage = "training"
        if stage not in result:
            continue
        status = operation["status"]
        reason = None
        if stage in {"model", "training"}:
            if not is_settings_save(operation):
                result[stage]["check"] = {
                    "status": status,
                    "operation_id": operation["operation_id"],
                    "revision": operation.get("revision"),
                }
                continue
            digest = operation.get("section_digest")
            if digest and digest != settings_digest(value["config"], stage):
                reason = "configuration_revision_changed"
            result[stage] = {
                "status": status,
                "operation_id": operation["operation_id"],
                "reason": reason,
                "revision": operation.get("revision"),
            }
            continue
        if operation.get("revision") != value["revision"]:
            status, reason = "stale", "configuration_revision_changed"
        if reason is None:
            try:
                for ref in operation.get("inputs", []):
                    asset(service, project, ref)
            except (ValueError, KeyError, FileNotFoundError):
                status, reason = "stale", "input_revision_changed"
        result[stage]["check"] = {
            "status": status,
            "operation_id": operation["operation_id"],
            "reason": reason,
            "revision": operation.get("revision"),
        }
    return {"task_id": identity, "revision": value["revision"], "stages": result}


def _preparation_normalize_dir(base, run_id, artifacts: Path):
    """归一化 PT 写在运行 data_dir/trainprep/normalize；历史运行也可能在 data_dir/normalize。"""
    candidates = []
    if run_id:
        raw = task.get_run(base, run_id).get("data_dir") or ""
        if raw:
            data_dir = Path(raw)
            candidates.extend(
                (data_dir / "trainprep" / "normalize", data_dir / "normalize")
            )
    run_data = artifacts.parent.parent.parent / "data" / artifacts.parent.name
    candidates.extend((run_data / "trainprep" / "normalize", run_data / "normalize"))
    seen = set()
    for folder in candidates:
        key = str(folder)
        if key in seen:
            continue
        seen.add(key)
        if folder.is_dir():
            return folder
    return None


def _list_preparation_files(artifacts, normalize, path, query, root, root_id, run_id):
    """准备页同时列出 preparation.json 与归一化副本树，按层打开，不核验 PT 内容。"""
    current = (path or "").strip("/")
    query = (query or "").strip()

    def row(target, base, is_dir, rel=None):
        item = _stage_row(target, base, root, root_id, "preparation", run_id, is_dir)
        if rel is not None:
            item["path"] = rel
        return item

    def hidden(target, base):
        return target.is_symlink() or any(
            part.startswith(".") for part in target.relative_to(base).parts
        )

    def matches(name, rel):
        if not query:
            return True
        text = query.casefold()
        return text in name.casefold() or text in rel.casefold()

    if query:
        found = []
        prep = artifacts / "preparation.json"
        if prep.is_file() and matches("preparation.json", "preparation.json"):
            found.append(row(prep, artifacts, False))
        if normalize is not None:
            for target in normalize.rglob("*"):
                if hidden(target, normalize):
                    continue
                leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
                if not leaf:
                    continue
                rel = "normalize/" + str(target.relative_to(normalize))
                if matches(target.name, rel):
                    found.append(row(target, normalize.parent, False, rel))
        return sorted(found, key=lambda item: (not item["directory"], item["path"]))
    if not current:
        result = []
        prep = artifacts / "preparation.json"
        if prep.is_file():
            result.append(row(prep, artifacts, False))
        if normalize is not None:
            result.append(row(normalize, normalize.parent, True, "normalize"))
        return sorted(result, key=lambda item: (not item["directory"], item["path"]))
    if current == "normalize" or current.startswith("normalize/"):
        if normalize is None:
            return []
        rest = current[len("normalize") :].lstrip("/")
        current_dir = normalize.joinpath(rest) if rest else normalize
        if (
            not current_dir.is_dir()
            or not current_dir.resolve().is_relative_to(normalize.resolve())
            or current_dir.is_symlink()
        ):
            raise ValueError("path_outside_root")
        result = []
        for target in sorted(
            current_dir.iterdir(), key=lambda item: (not item.is_dir(), item.name)
        ):
            if hidden(target, normalize):
                continue
            is_dir = target.is_dir() and target.suffix != ".zarr"
            rel = "normalize/" + str(target.relative_to(normalize))
            result.append(row(target, normalize.parent, is_dir, rel))
        return result
    current_dir = artifacts / current
    if (
        not current_dir.resolve().is_relative_to(artifacts.resolve())
        or current_dir.is_symlink()
        or not current_dir.is_dir()
    ):
        raise ValueError("path_outside_root")
    result = []
    for target in sorted(current_dir.iterdir(), key=lambda item: (not item.is_dir(), item.name)):
        if hidden(target, artifacts) or (
            target.is_file() and target.name != "preparation.json" and "normaliz" not in target.name
        ):
            continue
        is_dir = target.is_dir() and target.suffix != ".zarr"
        result.append(row(target, artifacts, is_dir))
    return result


def _stage_allowed(directory: Path, role: str):
    """阶段允许出现的路径；输入只取清单声明，准备和后处理按层过滤。"""
    if role == "inputs":
        manifest = directory / "manifest.json"
        content = json.loads(manifest.read_text())
        paths = [manifest]
        for sample in content.get("samples", []):
            sample_dir = Path(sample["path"])
            if not sample_dir.is_absolute():
                sample_dir = directory / sample_dir
            if not sample_dir.resolve().is_relative_to(directory.resolve()):
                raise ValueError("path_outside_root")
            for member in [
                *sample.get("filemap", {}).values(),
                *sample.get("assets", []),
                *sample.get("identity_assets", []),
            ]:
                path = sample_dir / member
                if not path.resolve().is_relative_to(sample_dir.resolve()):
                    raise ValueError("path_outside_root")
                paths.append(path)
        return paths
    return None


def _stage_row(path, directory, root, root_id, role, run_id, is_dir):
    stat = path.stat()
    return {
        "name": path.name,
        "path": "" if path == directory else str(path.relative_to(directory)),
        "root": root_id,
        "source_path": str(path.relative_to(root)),
        "directory": is_dir,
        "run_id": run_id,
        "role": role,
        "size": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
    }


def _hidden(path, directory):
    return path.is_symlink() or any(
        part.startswith(".") for part in path.relative_to(directory).parts
    )


def stage_files(
    project: str,
    identity: str,
    service,
    role: str,
    run_id: str | None = None,
    asset_id: str | None = None,
    revision: str | None = None,
    path: str = "",
    query: str = "",
):
    """按层列出指定正式运行交付范围；无选择返回空，不回退项目目录，不登记资产。"""
    from pathlib import Path

    from ...infrastructure.content_access import roots

    if role not in {"inputs", "preparation", "post"}:
        raise ValueError("unsupported_stage_file_role")
    base = service.project(project)
    task.get_task(base, identity)
    root = Path(base).resolve()
    if asset_id:
        if role not in {"inputs", "preparation"} or not revision:
            raise ValueError("fixed_stage_asset_required")
        source = asset(
            service, project, {"project_id": project, "asset_id": asset_id, "revision": revision}
        )
        expected = "manifest.json" if role == "inputs" else "preparation.json"
        if source.name != expected or not source.is_file():
            raise ValueError("stage_asset_kind_mismatch")
        directory = source.parent
    else:
        if not run_id:
            return []
        run = task.get_run(base, run_id)
        if run.get("task_id") != identity:
            raise ValueError("run_task_mismatch")
        if run.get("operation_mode", "execute") != "execute":
            raise ValueError("formal_run_required")
        if role == "inputs":
            manifest = task.run_physical_manifest(base, run)
            if manifest is None:
                return []
            directory = manifest.parent
        elif role == "preparation":
            directory = Path(run["run_dir"]) / "artifacts"
            if not (directory / "preparation.json").is_file():
                return []
        else:
            if "post" not in run.get("stages", []):
                return []
            directory = Path(run["run_dir"])
    root_id = "project"
    if not directory.resolve().is_relative_to(root):
        matches = [
            (name, location)
            for name, location in roots(service, project, identity).items()
            if directory.resolve().is_relative_to(location.resolve())
        ]
        if not matches:
            raise ValueError("path_outside_root")
        root_id, root = matches[0]
        root = root.resolve()
    if role == "preparation":
        normalize = _preparation_normalize_dir(base, run_id, directory)
        if normalize is not None and not normalize.resolve().is_relative_to(root):
            matches = [
                (name, location)
                for name, location in roots(service, project, identity).items()
                if normalize.resolve().is_relative_to(location.resolve())
            ]
            if not matches:
                raise ValueError("path_outside_root")
        return _list_preparation_files(directory, normalize, path, query, root, root_id, run_id)
    current = (path or "").strip("/")
    current_dir = directory / current if current else directory
    if current and (
        not current_dir.resolve().is_relative_to(directory.resolve()) or current_dir.is_symlink()
    ):
        raise ValueError("path_outside_root")
    if current and current_dir.suffix == ".zarr":
        return []
    allowed = _stage_allowed(directory, role)
    result = {}
    query = (query or "").strip()

    def accept(target, is_dir):
        if _hidden(target, directory) or (
            any(part.endswith(".zarr") for part in target.relative_to(directory).parts[:-1])
        ):
            return
        if role == "post":
            parts = target.relative_to(directory).parts
            if parts and parts[0] not in {"artifacts", "predictions", "meshes", "post"}:
                return
        rel = "" if target == directory else str(target.relative_to(directory))
        if query and (
            is_dir
            or (
                query.casefold() not in target.name.casefold()
                and query.casefold() not in rel.casefold()
            )
        ):
            return
        result[str(target)] = _stage_row(target, directory, root, root_id, role, run_id, is_dir)

    if allowed is not None:
        for target in sorted(set(allowed), key=lambda item: str(item)):
            if not target.exists():
                continue
            is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
            if query:
                if is_leaf:
                    accept(target, False)
                continue
            try:
                rest = target.relative_to(current_dir)
            except ValueError:
                continue
            parts = rest.parts
            if not parts:
                continue
            if len(parts) == 1:
                accept(target, not is_leaf)
            else:
                child = current_dir / parts[0]
                accept(child, child.is_dir() and child.suffix != ".zarr")
        return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))

    if query:
        for target in current_dir.rglob("*"):
            is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
            if is_leaf:
                accept(target, False)
        return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))
    if not current_dir.is_dir():
        return []
    for target in sorted(current_dir.iterdir(), key=lambda item: (not item.is_dir(), item.name)):
        is_leaf = target.is_file() or (target.is_dir() and target.suffix == ".zarr")
        accept(target, not is_leaf)
    return sorted(result.values(), key=lambda row: (not row["directory"], row["path"]))
