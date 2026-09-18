"""旧控制配置显式转换；只返回新副本，不改科学产物或历史文件。"""

import os
from copy import deepcopy
from pathlib import Path

from ai4e_core.base.config.conventions import normalize_recipe_config, require_current_keys


def migrate_legacy(config: dict, *, base: str | Path) -> dict:
    """按原配置目录解析路径，拒绝公共树与旧输入混用。"""
    value = deepcopy(config)
    if "inputs" in value:
        require_current_keys(
            value,
            {
                "data": "inputs",
                "train.resume": "inputs.train.resume",
                "posttrain.checkpoint": "inputs.posttrain.checkpoint",
                "infer.checkpoint": "inputs.infer.checkpoint",
                "post.results": "inputs.post.results",
            },
        )
    else:
        data = value.pop("data")
        value["data_root"] = data["output"]
        value["dataset"] = {"name": value["case"]}
        value["rawprep"] = {}
        value["trainprep"] = {}
        value["inputs"] = {"rawprep": {"source": data["root"]}}
        for stage in ("trainprep", "train", "posttrain", "infer"):
            refs = data["physical" if stage == "trainprep" else "prepared"]
            prefix = "dataset" if stage == "trainprep" else "preparation"
            value["inputs"][stage] = {
                f"{prefix}_{split}": refs[split] if refs else None
                for split in ("train", "cal", "test")
            }
        for stage, key in (
            ("train", "resume"),
            ("posttrain", "checkpoint"),
            ("infer", "checkpoint"),
        ):
            value["inputs"][stage][key] = value[stage].pop(key)
        value["inputs"]["post"] = {"results": value["post"].pop("results")}
    if "assets" in value["solver"]:
        if "solver_assets" in value["inputs"]["infer"]:
            raise ValueError("求解器资源新旧键混用")
        value["inputs"]["infer"]["solver_assets"] = value["solver"].pop("assets")
    value["inputs"]["infer"].setdefault("solver_assets", None)
    if value.get("pipeline", {}).get("stages", ["pipeline"]) == ["pipeline"]:
        value["pipeline"] = {
            "stages": ["rawprep", "trainprep", "train", "posttrain", "infer", "post"]
        }
    value = normalize_recipe_config(value, base=base)
    if value["solver"].get("python"):
        value["solver"]["python"] = os.path.abspath(
            Path(base) / Path(value["solver"]["python"]).expanduser()
        )
    from .configuration import validate

    return validate(value)
