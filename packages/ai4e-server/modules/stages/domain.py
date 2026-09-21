"""阶段规则：允许阶段、只读统计、输入选择与试跑门禁，不依赖 HTTP 或存储。"""

import json
import math
from copy import deepcopy
from dataclasses import dataclass, field

STAGES = {"rawprep", "trainprep", "model", "train", "infer", "post"}
CHECKPOINT_TAGS = {"last", "best", "latest"}
MODEL_REPLACEMENT_SECTIONS = ("model", "train", "trainprep")
ALLOWED_BINDINGS = {
    "inputs.trainprep.dataset",
    "inputs.train.preparation",
    "inputs.train.resume",
    "inputs.infer.checkpoint",
    "inputs.infer.preparation",
    "inputs.post.results",
    "inputs.trainprep.statistics",
}


@dataclass
class OperationCommand:
    """固定修订和资产的业务操作命令。"""

    expected_revision: str
    mode: str
    inputs: list[dict] = field(default_factory=list)
    selection: dict = field(default_factory=dict)
    idempotency_key: str | None = None


def validate_stage(stage):
    """拒绝没有登记的阶段。"""
    if stage not in STAGES:
        raise ValueError("unknown_stage")


def reject_statistics(value, path=""):
    """定位并拒绝用户配置中手写的拟合统计量。"""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in {
                "mean",
                "std",
                "min",
                "max",
                "minimum",
                "maximum",
                "variance",
                "fitted_statistics",
            }:
                raise ValueError("readonly_statistics: " + path + key)
            reject_statistics(child, path + key + ".")
    elif isinstance(value, list):
        for child in value:
            reject_statistics(child, path)


def execution_stages(stage, mode, selection):
    """确定允许的已有阶段顺序，并校验试跑范围。"""
    validate_stage(stage)
    if stage == "infer":
        raise ValueError("inference_requires_fixed_batch: 请通过推理批次固定检查点后执行")
    if mode not in {"trial", "execute"} or stage == "model":
        raise ValueError("unsupported_stage_operation")
    if stage == "train" and selection.get("prepare_first"):
        raise ValueError("train_requires_preparation: 训练设置只消费已有准备完成的数据")
    if mode == "trial" and not selection.get("samples"):
        raise ValueError("trial_samples_required")
    if "samples" in selection and not selection["samples"]:
        raise ValueError("empty_sample_selection")
    return [stage]


def required_inputs(stage, stages):
    """阶段消费的上游业务产物。"""
    return (
        ["inputs.trainprep.dataset"]
        if "trainprep" in stages
        else ["inputs.train.preparation"]
        if stage == "train"
        else ["inputs.post.results"]
        if stage == "post"
        else []
    )


def selected_input_keys(stages, declared):
    """仅捕获当前执行链所需输入，未来阶段产物不提前索取。"""
    return sorted(
        key for key in declared if key.startswith("inputs.") and key.split(".")[1] in stages
    )


def settings_digest(config, stage):
    """模型/训练设置完成态只跟本页参数，不含清单、准备和续训引用。"""
    section = "train" if stage in {"train", "training"} else "model"
    values = dict(config.get(section) or {})
    if section == "train":
        for key in ("manifest", "preparation", "resume"):
            values.pop(key, None)
    return json.dumps(values, sort_keys=True, default=str)


def is_settings_save(operation):
    """模型/训练完成只认保存记录；检查或结构跟踪不能冒充已保存。"""
    if operation.get("source") == "save":
        return True
    return str(operation.get("operation_id") or "").startswith("settings-check:")


def model_roles(config):
    """从模型 data_specs 展开准备页左侧角色；形状按点场张量声明。"""
    specs = (config.get("model") or {}).get("data_specs") or {}
    bindings = (config.get("trainprep") or {}).get("domains") or {}
    use_features = bool((config.get("trainprep") or {}).get("use_physics_features"))
    position_shape = _tensor_shape(specs.get("position_dim", 3))
    roles = []
    domains = specs.get("domains") or {}
    if not domains:
        for domain, definition in bindings.items():
            if not isinstance(definition, dict):
                continue
            roles.append(_role(domain, "position", "position", None, True))
            for name in definition.get("features") or {}:
                roles.append(_role(domain, "features", name, None, use_features))
            for name in definition.get("targets") or {}:
                roles.append(_role(domain, "targets", name, None, True))
        return roles
    for domain, spec in domains.items():
        if not isinstance(spec, dict):
            continue
        roles.append(_role(domain, "position", "position", position_shape, True))
        for name, width in (spec.get("output_dims") or {}).items():
            roles.append(_role(domain, "targets", name, _tensor_shape(width), True))
        bound_features = (bindings.get(domain) or {}).get("features") or {}
        if use_features or bound_features:
            for name, width in (spec.get("feature_dim") or {}).items():
                roles.append(_role(domain, "features", name, _tensor_shape(width), use_features))
    return roles


def dataset_fields(config, manifest=None):
    """物理清单优先，否则用原始处理声明与已有绑定，不手造模型字段。"""
    catalog = {}
    layout = (manifest or {}).get("physical_layout") or {}
    sample_fields = ((manifest or {}).get("samples") or [{}])[0].get("fields") or {}
    for domain, declaration in (layout.get("domains") or {}).items():
        if not isinstance(declaration, dict):
            continue
        position = declaration.get("position")
        if position:
            _put_field(
                catalog,
                domain,
                position,
                _recorded_shape(sample_fields.get(position)) or _tensor_shape(3),
            )
        for physical in (declaration.get("fields") or {}).values():
            _put_field(catalog, domain, physical, _recorded_shape(sample_fields.get(physical)))
    rawprep = config.get("rawprep") or {}
    declared = rawprep.get("fields") or {}
    for logical in rawprep.get("save_fields") or []:
        domain = _domain_of(logical, declared, config)
        if domain:
            _put_field(catalog, domain, logical, _declared_shape(logical, domain, declared))
    for domain, items in declared.items():
        if not isinstance(items, dict):
            continue
        for name in items:
            _put_field(
                catalog,
                domain,
                f"{domain}_{name}",
                _declared_shape(f"{domain}_{name}", domain, declared),
            )
    for domain, definition in ((config.get("trainprep") or {}).get("domains") or {}).items():
        if not isinstance(definition, dict):
            continue
        for physical in (
            definition.get("position"),
            *(definition.get("features") or {}).values(),
            *(definition.get("targets") or {}).values(),
        ):
            if physical and _domain_of(physical, declared, config) == domain:
                _put_field(catalog, domain, physical, _declared_shape(physical, domain, declared))
    return [catalog[key] for key in sorted(catalog)]


def field_matching_catalog(config, manifest=None):
    """准备页匹配清单：左侧模型角色，右侧数据集场及张量形状。"""
    fields = dataset_fields(config, manifest)
    return {
        "model_roles": model_roles(config),
        "dataset_fields": fields,
        "source": "manifest" if (manifest or {}).get("physical_layout") else "configuration",
    }


SLICE_ROLES = ("train", "test", "eval")
SLICE_LABELS = {"train": "训练集", "test": "测试集", "eval": "评价集"}


def published_slices(record=None):
    """从准备记录读出固定三分片；缺的桶人数为 0，不改历史文件。"""
    payload = record if isinstance(record, dict) else {}
    partitions = payload.get("partitions") if isinstance(payload.get("partitions"), dict) else {}
    counts = (
        payload.get("split_counts") if isinstance(payload.get("split_counts"), dict) else {}
    )
    split = payload.get("split") if isinstance(payload.get("split"), dict) else {}
    completed = {name: [str(item) for item in partitions.get(name) or []] for name in SLICE_ROLES}
    if not completed["eval"] and partitions.get("validation"):
        completed["eval"] = [str(item) for item in partitions["validation"]]
    method = str(split.get("method") or "original")
    try:
        seed = int(split.get("seed") or 0)
    except (TypeError, ValueError):
        seed = 0
    slices = []
    for name in SLICE_ROLES:
        if name in partitions or (name == "eval" and "validation" in partitions):
            count = len(completed[name])
        elif name in counts:
            try:
                count = int(counts[name] or 0)
            except (TypeError, ValueError):
                count = 0
        else:
            count = 0
        slices.append(
            {
                "name": name,
                "role": name,
                "label": SLICE_LABELS[name],
                "count": count,
                "method": method,
                "seed": seed,
            }
        )
    return slices


def legacy_slice_patch(config):
    """旧任务缺训练切片或仍写 validation 时给出写回段；已有显式切片不改。"""
    if not isinstance(config, dict):
        return {}
    patch = {}
    train = config.get("train") if isinstance(config.get("train"), dict) else {}
    train_patch = {}
    if "training_split" not in train:
        train_patch["training_split"] = "train"
    for key in ("training_split", "evaluation_split", "export_split"):
        if key in train_patch:
            continue
        if train.get(key) == "validation":
            train_patch[key] = "eval"
    if train_patch:
        patch["train"] = train_patch
    post = config.get("post") if isinstance(config.get("post"), dict) else {}
    if post.get("split") == "validation":
        patch["post"] = {"split": "eval"}
    infer = config.get("infer") if isinstance(config.get("infer"), dict) else {}
    if infer.get("split") == "validation":
        patch["infer"] = {"split": "eval"}
    prep = config.get("trainprep") if isinstance(config.get("trainprep"), dict) else {}
    split = prep.get("split") if isinstance(prep.get("split"), dict) else {}
    counts = split.get("counts") if isinstance(split.get("counts"), dict) else None
    if counts is not None and "eval" not in counts:
        patch["trainprep"] = {"split": {"counts": {"eval": 0}}}
    return patch


def split_catalog(manifest=None):
    """准备页分片默认值：全部已处理样本，原分片人数，缺的桶为 0。"""
    partitions = (manifest or {}).get("partitions") or {}
    items = []
    names: set[str] = set()
    for key, samples in partitions.items():
        for sample in samples or []:
            identity = str(sample)
            if identity in names:
                continue
            names.add(identity)
            items.append({"id": identity, "partition": str(key)})
    defaults = {name: len(partitions.get(name) or []) for name in ("train", "test", "eval")}
    leftovers: list[str] = []
    leftover_names: set[str] = set()
    for key, samples in partitions.items():
        if key in defaults:
            continue
        for sample in samples or []:
            identity = str(sample)
            if identity in leftover_names:
                continue
            leftover_names.add(identity)
            leftovers.append(identity)
    defaults["train"] += len(leftovers)
    return {
        "total": len(items),
        "defaults": defaults,
        "methods": ["original", "random"],
        "samples": items,
    }


def validate_split(values, manifest=None):
    """随机重划时数量之和必须等于执行范围内的样本，且训练分片至少一个。"""
    split = (values or {}).get("split")
    if not split:
        return
    method = str(split.get("method") or "original")
    if method not in {"original", "random"}:
        raise ValueError("unsupported_split_method")
    catalog = split_catalog(manifest)
    selected = split.get("samples")
    if selected is not None:
        if not isinstance(selected, list) or not selected:
            raise ValueError("split_samples_required")
        known = {item["id"] for item in catalog["samples"]}
        if any(str(item) not in known for item in selected):
            raise ValueError("split_sample_unknown")
        total = len({str(item) for item in selected})
    else:
        total = catalog["total"]
    counts = split.get("counts") or {}
    train = int(counts.get("train") or 0)
    test = int(counts.get("test") or 0)
    evaluation = int(counts.get("eval") or 0)
    if min(train, test, evaluation) < 0:
        raise ValueError("split_count_negative")
    if method == "original":
        return
    if total and train + test + evaluation != total:
        raise ValueError("split_count_sum_mismatch")
    if train < 1:
        raise ValueError("split_train_required")


def abupt_model(config) -> bool:
    """现行官方 AB-UPT 组件才预填坐标 scale=1000，不猜其它模型。"""
    model = str((config or {}).get("components", {}).get("model") or "")
    return "abupt" in model.lower()


def default_field_scale(declaration, *, abupt: bool):
    """缺键时按现行写法补 scale：AB-UPT 统一空间为 1000，其余为 1。"""
    if isinstance(declaration, dict) and declaration.get("scale") is not None:
        return declaration["scale"]
    if isinstance(declaration, dict) and declaration.get("method") == "coordinate" and abupt:
        return 1000.0
    return 1.0


def normalize_field_scales(config: dict) -> dict:
    """为 trainprep.normalization 每场写入显式 scale，不猜统计量。"""
    result = deepcopy(config or {})
    fields = ((result.get("trainprep") or {}).get("normalization") or {}).get("fields")
    if not isinstance(fields, dict):
        return result
    abupt = abupt_model(result)
    for declaration in fields.values():
        if not isinstance(declaration, dict):
            continue
        if declaration.get("scale") is None:
            declaration["scale"] = default_field_scale(declaration, abupt=abupt)
    return result


def validate_field_scales(trainprep):
    """场上 scale 必须为正有限数；保存前应已写成显式值。"""
    fields = ((trainprep or {}).get("normalization") or {}).get("fields") or {}
    for name, declaration in fields.items():
        if not isinstance(declaration, dict):
            continue
        raw = declaration.get("scale", 1)
        if raw is None:
            raw = 1
        try:
            factor = float(raw)
        except (TypeError, ValueError) as exc:
            raise ValueError("invalid_field_scale:" + name) from exc
        if factor <= 0 or not math.isfinite(factor):
            raise ValueError("invalid_field_scale:" + name)


def validate_field_bindings(trainprep, roles, fields):
    """已选物理场必须属于同一域，已知张量形状必须与模型角色相容。"""
    catalog = {(item["domain"], item["name"]): item for item in fields}
    by_name = {}
    for item in fields:
        by_name.setdefault(item["name"], []).append(item)
    bindings = (trainprep or {}).get("domains") or {}
    for role in roles:
        selected = _selected_field(bindings.get(role["domain"]) or {}, role)
        if not selected:
            continue
        item = catalog.get((role["domain"], selected))
        if item is None:
            if selected in by_name:
                raise ValueError(f"field_domain_mismatch: {role['id']} {selected}")
            raise ValueError(f"unknown_dataset_field: {role['id']} {selected}")
        if shapes_compatible(role.get("shape"), item.get("shape")) is False:
            raise ValueError(
                "field_dimension_mismatch: "
                f"{role['id']} {selected} {role.get('shape')}!={item.get('shape')}"
            )


def shapes_compatible(model_shape, data_shape):
    """点数字符号轴可不同；其余特征轴必须逐维相同。缺形状则无法判定。"""
    if not model_shape or not data_shape:
        return None
    want = list(model_shape)
    got = list(data_shape)
    if want and want[0] in {"N", "n"}:
        tail = want[1:]
        if got == tail:
            return True
        return len(got) == len(tail) + 1 and got[1:] == tail
    return want == got


def _role(domain, role, name, shape, required):
    return {
        "id": f"{domain}/{role}" if role == "position" else f"{domain}/{role}/{name}",
        "domain": domain,
        "role": role,
        "name": name,
        "shape": shape,
        "dim": _last_axis(shape),
        "required": required,
    }


def _put_field(catalog, domain, name, shape):
    if not name:
        return
    key = (domain, name)
    current = catalog.get(key)
    chosen = _prefer_shape(current.get("shape") if current else None, shape)
    record = {"domain": domain, "name": name, "shape": chosen, "dim": _last_axis(chosen)}
    if current is None:
        catalog[key] = record
        return
    catalog[key] = record


def _selected_field(definition, role):
    if role["role"] == "position":
        return definition.get("position") or ""
    return ((definition.get(role["role"]) or {}).get(role["name"])) or ""


def _tensor_shape(value):
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int | list | tuple):
        return None
    if isinstance(value, int):
        return ["N", value] if value > 0 else None
    axes = list(value)
    if not axes:
        return None
    if axes[0] in {"N", "n"}:
        return ["N", *axes[1:]]
    if all(isinstance(item, int) and item > 0 for item in axes):
        return ["N", *axes]
    return None


def _recorded_shape(spec):
    if not isinstance(spec, dict):
        return None
    shape = spec.get("shape")
    if not isinstance(shape, list) or not shape:
        return None
    return [int(item) for item in shape]


def _declared_shape(name, domain, declared):
    short = name[len(domain) + 1 :] if name.startswith(domain + "_") else name
    spec = (declared.get(domain) or {}).get(short)
    if isinstance(spec, dict):
        if isinstance(spec.get("shape"), list) and spec["shape"]:
            return ["N", *spec["shape"]] if spec["shape"][0] != "N" else list(spec["shape"])
        if spec.get("components"):
            return _tensor_shape(spec["components"])
    return _tensor_shape(_declared_dim(name, domain, declared))


def _last_axis(shape):
    if not shape:
        return None
    tail = shape[-1]
    return int(tail) if isinstance(tail, int) else None


def _prefer_shape(old, new):
    if new is None:
        return old
    if old is None:
        return new
    old_n = sum(isinstance(item, int) for item in old)
    new_n = sum(isinstance(item, int) for item in new)
    if new_n != old_n:
        return new if new_n > old_n else old
    return new if len(new) > len(old) else old


def _domain_of(name, declared, config):
    for domain in declared:
        if name.startswith(f"{domain}_"):
            return domain
    for domain in (config.get("trainprep") or {}).get("domains") or {}:
        if name.startswith(f"{domain}_"):
            return domain
    return None


def _declared_dim(name, domain, declared):
    short = name[len(domain) + 1 :] if name.startswith(domain + "_") else name
    spec = (declared.get(domain) or {}).get(short)
    if isinstance(spec, dict) and spec.get("components"):
        return int(spec["components"])
    if short in {"position", "points"} or name.endswith("_position"):
        return 3
    if short == "normals" or name.endswith("_normals"):
        return 3
    if short in {"sdf", "distance"} or name.endswith("_sdf"):
        return 1
    if short in {"velocity", "cf"} or name.endswith(("_velocity", "_cf")):
        return 3
    if short in {"pressure", "cp", "area"} or name.endswith(("_pressure", "_cp", "_area")):
        return 1
    return None
