"""旧WDNO用户配置的显式转换；历史数组、权重与源码快照不改写。"""

from copy import deepcopy
from pathlib import Path

from ai4e_core.base.config.conventions import normalize_recipe_config

from .configuration import STAGES, validate


def migrate_legacy(value: dict, *, base: str | Path) -> dict:
    """返回新配置副本；正常加载不接受旧树，也不隐式修补混合配置。"""
    value = deepcopy(value)
    if "inputs" in value or "data_root" in value:
        raise ValueError("不能混用新旧配置；转换仅接受完整旧配置")
    data = value.pop("data")
    if set(data) != {"protocol", "indices", "output", "physical", "prepared"}:
        raise ValueError("旧data配置字段不完整或未知")

    def splits(refs, first):
        if refs is not None and set(refs) != {"train", "validation", "test"}:
            raise ValueError("旧分片引用不完整或未知")
        return {
            first: refs["train"] if refs else None,
            "validation": refs["validation"] if refs else None,
            "test": refs["test"] if refs else None,
        }

    results = value.pop("post")
    if set(results) != {"results"} or (
        results["results"] is not None and set(results["results"]) != {"validation", "test"}
    ):
        raise ValueError("旧post配置字段不完整或未知")
    value["inputs"] = {
        "rawprep": {"source": data["protocol"], "indices": data["indices"]},
        "trainprep": splits(data["physical"], "dataset"),
        "train": {
            **splits(data["prepared"], "preparation"),
            "resume": value["train"].pop("resume"),
        },
        "infer": {
            **splits(data["prepared"], "preparation"),
            "checkpoint": value["infer"].pop("checkpoint"),
        },
        "post": {
            key: results["results"][key] if results["results"] else None
            for key in ("validation", "test")
        },
    }
    value["data_root"] = data["output"]
    if value.get("pipeline") == {"stages": ["pipeline"]}:
        value["pipeline"] = {"stages": STAGES.copy()}
    return validate(normalize_recipe_config(value, base=base))
