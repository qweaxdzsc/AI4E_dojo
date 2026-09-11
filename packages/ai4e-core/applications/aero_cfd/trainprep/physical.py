"""跨模型训练准备：公共物理视图、冻结变换和模型输入绑定。"""

import json
from copy import deepcopy
from pathlib import Path

from ai4e_core.abilities.data.stats.physical import freeze
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.data.validate.physical import validate_bindings
from ai4e_core.abilities.inference.randomness import preserve_randomness
from ai4e_core.abilities.transform.normalization import Normalization


def open_preparation(
    config: dict, dataset_component, model_component, reference: str | Path | None = None
) -> tuple:
    """内容、布局和绑定一致才消费已冻结准备；检查不推进随机状态。"""
    old = json.loads(Path(reference).read_text()) if reference else None
    if old:
        config = deepcopy(config)
        if not isinstance(old.get("manifest"), str):
            raise ValueError("冻结准备缺少物理数据清单引用")
        requested = config.get("train", {}).get("manifest")
        if (
            requested
            and Path(requested).is_file()
            and Path(requested).resolve() != Path(old["manifest"]).resolve()
        ):
            raise ValueError("已选物理清单与冻结准备引用不一致")
        config.setdefault("train", {})["manifest"] = old["manifest"]
    view = dataset_component.open_physical(config)
    data_id = view.content_digest()
    declarations = deepcopy(
        {k: config[k] for k in ("model", "trainprep", "sampling", "normalization")}
    )
    declarations["component"] = model_component.SOURCE
    if old and (old["dataset"] != data_id or old["declarations"] != declarations):
        raise ValueError("数据、模型输入或准备声明已变化")
    normalization = Normalization(old["normalization"]) if old else freeze(view, config)
    record = {
        "version": 1,
        "dataset": data_id,
        "manifest": view.describe()["reference"],
        "declarations": declarations,
        "normalization": normalization.record,
        "split_counts": {k: len(v) for k, v in view.partitions.items()},
    }
    record["digest"] = fingerprint(record)
    if old and old != record:
        raise ValueError("冻结准备内容不一致")
    with preserve_randomness():
        sample = view.read("train", 0)
        validate_bindings(sample, config["trainprep"])
        model_component.prepare_sample(sample, config, normalization, evaluation=True)
    return view, normalization, record


def normalized_fields(sample: dict, normalization: Normalization) -> dict:
    """点字段保持物理来源，样本条件由模型绑定显式变换。"""
    return normalization.apply(sample["fields"])
