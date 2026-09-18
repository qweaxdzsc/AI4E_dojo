"""把历史测试数据中的路径摆到公共输入位置；仅构造测试输入。"""

from copy import deepcopy


def public_patch(value):
    """转换局部测试配置，不注入默认值，不改变科学参数和断言。"""
    value = deepcopy(value)
    paths = {
        ("dataset", "root"): ("rawprep", "source"),
        ("train", "manifest"): ("trainprep", "dataset"),
        ("train", "preparation"): ("train", "preparation"),
        ("train", "resume"): ("train", "resume"),
        ("model", "initial_weights"): ("train", "initial_weights"),
        ("post", "checkpoint"): ("infer", "checkpoint"),
        ("post", "results"): ("post", "results"),
    }
    for (section, key), (stage, name) in paths.items():
        if key in value.get(section, {}):
            item = value[section].pop(key)
            target = value.setdefault("inputs", {}).setdefault(stage, {})
            if name in target and target[name] != item:
                raise ValueError("conflicting test input")
            target[name] = item
    normalization = value.get("trainprep", {}).get("normalization", {})
    if "statistics" in normalization:
        value.setdefault("inputs", {}).setdefault("trainprep", {})["statistics"] = normalization.pop("statistics")
    return value
