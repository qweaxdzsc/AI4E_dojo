"""训练样本、统计字段和缺失策略的业务装配，消费本次提交结果。"""

import time
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save import load_named_tensor
from ai4e_core.abilities.data.stats import fit_statistics, load_statistics, write_statistics
from ai4e_core.base.events import event


def _train_samples(items, spec):
    """显式样本或参数分片选择训练集；空列表不退回默认值。"""
    if "train_samples" in spec:
        selected = list(spec["train_samples"])
        unknown = set(selected) - set(items)
        if unknown:
            raise ValueError(f"训练样本不在本次选择中: {sorted(unknown)}")
    elif "train_params" in spec:
        parts = {f"param{p}" for p in spec["train_params"]}
        selected = [s for s in items if Path(s).parts[0] in parts]
    else:
        selected = list(items)
    if not selected or len(selected) != len(set(selected)):
        raise ValueError("训练样本为空或重复")
    return selected


def resolve_statistics(ctx: dict, *, stats: dict) -> dict:
    """默认校验随包统计量；重算只读取本次结果，dry-run 不读旧张量、不写统计量。"""
    if not stats.get("recalculate", False):
        path = Path(stats["shipped"])
        if not path.is_absolute():
            if ctx.get("recipe_dir") is None:
                raise ValueError("相对统计量路径需要 recipe_dir")
            path = Path(ctx["recipe_dir"]) / path
        load_statistics(path)
        ctx["statistics"] = str(path)
        ctx.setdefault("reports", {})["statistics"] = str(path)
        return ctx
    selected = _train_samples(ctx["items"], stats)
    fields = stats.get("fields")
    positions = stats.get("position_fields", [])
    missing = stats.get("missing", "error")
    if not isinstance(fields, list) or not fields or len(fields) != len(set(fields)):
        raise ValueError("统计 fields 必须显式声明为非空且不重复的列表")
    if set(positions) - set(fields):
        raise ValueError("position_fields 必须属于统计 fields")
    if missing not in ("error", "skip"):
        raise ValueError("统计 missing 必须为 error 或 skip")
    config = ctx["config"]
    output = config["pre"]["output"]
    target = Path(
        stats.get(
            "output", Path(output["dir"]) / output.get("root_subdir", ".") / "statistics.yaml"
        )
    )
    if target.suffix.lower() not in (".yaml", ".yml", ".json"):
        raise ValueError("统计量输出必须为 YAML 或 JSON")
    if target.exists() and not ctx.get("overwrite", False):
        raise FileExistsError(f"统计量输出已存在: {target}")
    results = {r["sample"]: r for r in ctx["batch"]["results"]}
    excluded = []
    usable = []
    for sample in selected:
        result = results.get(sample)
        if result is None or (not ctx.get("dry_run") and not result["written"]):
            reason = f"训练样本未成功提交: {sample}"
            if missing == "error":
                raise ValueError(reason)
            excluded.append({"sample": sample, "reason": reason})
            continue
        usable.append(result)
    if not usable:
        raise ValueError("没有可统计的训练样本")
    # 先验证完整选择，避免部分字段已累计后才发现配置遗漏。
    sources = {}
    for field in fields:
        logical, separator, member = field.partition("/")
        refs = []
        for result in usable:
            filename = result["filemap"].get(logical)
            if filename is None or field not in result["available_fields"]:
                reason = f"样本 {result['sample']} 缺少统计字段 {field}"
                if missing == "error":
                    raise ValueError(reason)
                excluded.append({"sample": result["sample"], "field": field, "reason": reason})
                continue
            refs.append(
                (result["sample"], Path(result["path"]) / filename, member if separator else None)
            )
        if not refs:
            raise ValueError(f"统计字段无可用样本: {field}")
        sources[field] = refs
    if ctx.get("dry_run"):
        ctx.setdefault("reports", {})["statistics"] = {
            "status": "planned",
            "path": str(target),
            "samples": selected,
            "fields": fields,
        }
        return ctx

    def arrays(field, refs):
        last = time.monotonic()
        entities = 0
        for index, (sample, path, member) in enumerate(refs, 1):
            try:
                value = load_named_tensor(path)
                if member is not None:
                    value = value[member]
            except (FileNotFoundError, KeyError) as exc:
                if missing == "error":
                    raise ValueError(f"样本 {sample} 缺少统计字段 {field}: {path}") from exc
                excluded.append({"sample": sample, "field": field, "reason": str(exc)})
                continue
            if not isinstance(value, torch.Tensor):
                raise TypeError(f"统计字段须为张量，打包字段需明确成员: {field}")
            entities += len(value)
            if time.monotonic() - last >= 10 or index == len(refs):
                event(
                    "统计",
                    "进度",
                    字段=field,
                    已读样本=index,
                    总样本=len(refs),
                    已累计实体数=entities,
                )
                last = time.monotonic()
            yield value.detach().cpu().numpy()

    moments = fit_statistics({f: arrays(f, refs) for f, refs in sources.items()})
    result = {}
    for name, values in moments.items():
        for key, value in values.items():
            result[f"{name}_{key}"] = value if key == "count" else np.asarray(value).tolist()
    if positions:
        result["raw_pos_min"] = [float(min(np.min(moments[p]["min"]) for p in positions))]
        result["raw_pos_max"] = [float(max(np.max(moments[p]["max"]) for p in positions))]
    result["metadata"] = {
        "samples": selected,
        "fields": fields,
        "position_fields": positions,
        "missing": missing,
        "excluded": excluded,
        "filters": {r["sample"]: r["filters"] for r in usable},
        "counts": {f: m["count"] for f, m in moments.items()},
    }
    write_statistics(target, result)
    ctx["statistics"] = str(target)
    ctx.setdefault("reports", {})["statistics"] = str(target)
    return ctx
