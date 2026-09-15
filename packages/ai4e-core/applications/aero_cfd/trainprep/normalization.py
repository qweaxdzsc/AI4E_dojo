"""外流归一化装配：冻结字段绑定与共享坐标边界。"""

from __future__ import annotations

from pathlib import Path

from ai4e_core.abilities.data.stats.load import load_statistics
from ai4e_core.abilities.transform.normalization import Normalization


def bind_normalization(config: dict, manifest: dict, index=None) -> Normalization:
    """显式统计来源优先，随后使用清单统计；缺失或配置冲突立即失败。"""
    declaration = config["normalization"]
    if not declaration.get("execute"):
        raise ValueError("prepare/fit 物理数据需要 normalization.execute=true")
    source = declaration.get("statistics") or manifest.get("statistics", {}).get("path")
    stats = load_statistics(source) if source else {}
    fields = {}
    for name, item in declaration.get("fields", {}).items():
        method = item["method"]
        supplied = dict(item.get("parameters", {}))
        if method == "custom":
            if not item.get("target"):
                raise ValueError("自定义变换必须指定 target")
            parameters = supplied
        elif method == "identity":
            parameters = {}
        elif method == "minmax":
            if supplied or index is None:
                raise ValueError("Min-Max 必须从训练分片计算，不能手填参数")
            low = high = None
            for row in range(len(index.partitions.get("train", []))):
                values = index.read("train", row, fields=[name])[name]
                values = values.reshape(len(values), -1)
                lo, hi = values.amin(0), values.amax(0)
                low = lo if low is None else low.minimum(lo)
                high = hi if high is None else high.maximum(hi)
            if low is None:
                raise ValueError("Min-Max 需要非空训练分片")
            parameters = {
                "minimum": low.tolist(),
                "maximum": high.tolist(),
                "scale": item.get("scale", 1.0),
            }
        elif method == "coordinate":
            keys = item.get("statistics_keys", {"minimum": "raw_pos_min", "maximum": "raw_pos_max"})
            parameters = {k: stats[v] for k, v in keys.items() if k not in supplied}
            parameters.update(scale=1000.0, check_range=True, tolerance=1e-6)
        elif method == "zscore":
            keys = item.get("statistics_keys", {"mean": name + "_mean", "std": name + "_std"})
            parameters = {k: stats[v] for k, v in keys.items() if k not in supplied}
        else:
            raise ValueError("不支持的变换方法")
        parameters.update(supplied)
        fields[name] = {
            "method": method,
            "parameters": parameters,
            "scope": item.get("scope", "point"),
        }
        if method == "custom":
            fields[name]["target"] = item["target"]
    if not fields:
        raise ValueError("准备需要显式冻结变换声明")
    return Normalization(
        {
            "version": 2,
            "fields": fields,
            "source": str(Path(source).resolve()) if source else None,
            "statistics_provenance": {"mode": "explicit", "path": str(source)}
            if declaration.get("statistics")
            else manifest.get("statistics", {}),
            "training_samples": list(index.partitions.get("train", []))
            if index is not None
            else manifest["partitions"].get("train", []),
        }
    )


def validate_frozen(config: dict, normalization: Normalization) -> None:
    """核对显式方法与参数覆盖；读取冻结数据不要求原统计文件存在。"""
    for name, declaration in config.get("normalization", {}).get("fields", {}).items():
        frozen = normalization.record["fields"].get(name)
        if frozen is None or declaration["method"] != frozen["method"]:
            raise ValueError("配置与冻结变换方法冲突")
        if declaration["method"] == "custom" and declaration.get("target") != frozen.get("target"):
            raise ValueError("配置与冻结变换实现冲突")
        if declaration.get("scope", "point") != frozen.get("scope", "point"):
            raise ValueError("配置与冻结变换字段空间冲突")
        for key, value in declaration.get("parameters", {}).items():
            if value != frozen["parameters"].get(key):
                raise ValueError("配置与冻结变换参数冲突")
