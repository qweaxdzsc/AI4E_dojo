"""按具名物理视图拟合训练变换，点和样本使用不同统计单位。"""

from ai4e_core.abilities.data.stats.population import PopulationMoments
from ai4e_core.abilities.transform.normalization import Normalization
from ai4e_core.abilities.transform.scale import resolve_scale


def freeze(view, config: dict) -> Normalization:
    """按声明冻结训练统计，条件按样本累计，坐标可共用来源统计。"""
    declaration = config["normalization"]
    if not declaration.get("execute"):
        raise ValueError("物理训练准备要求 normalization.execute=true")
    specs = declaration["fields"]
    for name, spec in specs.items():
        if spec["method"] == "minmax" and spec.get("parameters"):
            raise ValueError(f"normalization.fields.{name}: Min-Max 统计参数必须从训练数据获得")
    from ai4e_core.abilities.data.stats.load import load_statistics

    source = declaration.get("statistics")
    if not source and isinstance(view.describe().get("statistics"), dict):
        source = view.describe()["statistics"].get("path")
    stats = load_statistics(source) if source else {}
    fitted, bounds = {}, {}
    need = {
        name: spec
        for name, spec in specs.items()
        if spec["method"] not in {"identity", "custom"} and not spec.get("parameters") and not stats
    }
    if need:
        for index in range(len(view.partitions["train"])):
            sample = view.read("train", index)
            for name, spec in need.items():
                values = (
                    sample["conditions"][name]
                    if spec.get("scope") == "condition"
                    else sample["fields"][name]
                )
                values = values.numpy().reshape(len(values), -1)
                if spec["method"] == "minmax":
                    lo, hi = values.min(axis=0), values.max(axis=0)
                    if name in bounds:
                        import numpy as np

                        lo, hi = np.minimum(lo, bounds[name][0]), np.maximum(hi, bounds[name][1])
                    bounds[name] = lo, hi
                elif spec["method"] == "coordinate":
                    lo, hi = float(values.min()), float(values.max())
                    previous = bounds.get(name, (lo, hi))
                    bounds[name] = min(lo, previous[0]), max(hi, previous[1])
                else:
                    fitted.setdefault(name, PopulationMoments(values.shape[1])).update(values)
    fields = {}
    for name, spec in specs.items():
        method = spec["method"]
        parameters = dict(spec.get("parameters", {}))
        if method == "zscore" and not parameters:
            if stats:
                keys = spec.get("statistics_keys", {"mean": name + "_mean", "std": name + "_std"})
                parameters = {key: stats[value] for key, value in keys.items()}
            else:
                result = fitted[name].finalize()
                parameters = {k: result[k] for k in ("mean", "std")}
        elif method == "minmax" and not parameters:
            if name not in bounds:
                # Min-Max 不消费无来源的用户边界；始终从训练分片拟合。
                for index in range(len(view.partitions["train"])):
                    sample = view.read("train", index)
                    values = sample["conditions" if spec.get("scope") == "condition" else "fields"][
                        name
                    ].numpy()
                    lo, hi = values.min(axis=0), values.max(axis=0)
                    if name in bounds:
                        import numpy as np

                        lo, hi = np.minimum(lo, bounds[name][0]), np.maximum(hi, bounds[name][1])
                    bounds[name] = lo, hi
            lo, hi = bounds[name]
            parameters = {
                "minimum": lo.tolist(),
                "maximum": hi.tolist(),
                "scale": 1.0,
            }
        elif method == "coordinate" and not parameters:
            if stats:
                parameters = {"minimum": stats["raw_pos_min"], "maximum": stats["raw_pos_max"]}
            else:
                lo, hi = bounds[name]
                parameters = {"minimum": [lo], "maximum": [hi]}
            parameters.update(scale=1.0, check_range=False)
        fields[name] = {
            "method": method,
            "parameters": parameters,
            "scope": spec.get("scope", "point"),
            "scale": resolve_scale(spec),
        }
        if method == "custom":
            fields[name]["target"] = spec["target"]
    # 同一物理空间的多个域必须使用相同坐标映射；旧声明不受影响。
    coordinate_groups = {}
    for name, spec in specs.items():
        group = spec.get("coordinate_group")
        if group is not None:
            if spec["method"] != "coordinate" or not isinstance(group, str) or not group:
                raise ValueError("coordinate_group 仅用于具名坐标变换组")
            coordinate_groups.setdefault(group, []).append(name)
    for names in coordinate_groups.values():
        if len({fields[name]["scale"] for name in names}) != 1:
            raise ValueError("同一坐标组的 scale 必须相同")
        low = min(min(fields[name]["parameters"]["minimum"]) for name in names)
        high = max(max(fields[name]["parameters"]["maximum"]) for name in names)
        for name in names:
            fields[name]["parameters"].update(minimum=[low], maximum=[high])
            fields[name]["coordinate_group"] = specs[name]["coordinate_group"]
    return Normalization(
        {"version": 2, "fields": fields, "training_samples": view.partitions["train"]}
    )
