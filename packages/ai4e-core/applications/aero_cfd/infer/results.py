"""固定推理结果的只读入口；不恢复模型、不计算预测、不修改源清单。"""

import json
from copy import deepcopy
from pathlib import Path

from ai4e_core.abilities.data.save.store import load_named_tensor
from ai4e_core.abilities.data.validate.fingerprint import fingerprint


def open_results(reference, *, session=None) -> dict:
    """读取已提交结果并核对协议与成员；只消费固定成功结果。"""
    result = (
        deepcopy(reference)
        if isinstance(reference, dict)
        else json.loads(Path(reference).read_text())
    )
    if result.get("version") not in {1, 2} or result.get("status") != "succeeded":
        raise ValueError("后处理需要已成功交付的固定推理结果")
    protocol = result.get("protocol", {})
    if not protocol or fingerprint(
        {k: v for k, v in protocol.items() if k != "digest"}
    ) != protocol.get("digest"):
        raise ValueError("推理结果协议摘要不匹配")
    for item in result.get("results", []):
        path = item.get("manifest")
        if path:
            metadata = json.loads(Path(path).read_text())
            if metadata.get("protocol") != protocol["digest"]:
                raise ValueError("样本结果与推理协议不一致")
            for value in metadata["filemap"].values():
                member = Path(value)
                if member.name != str(member) or not (Path(path).parent / member).is_file():
                    raise ValueError("推理成员缺失或路径越界")
    if session is not None:
        session.report(
            {
                "mode": "post",
                "status": "succeeded",
                "results": result["results"],
                "metrics": result.get("metrics", {}),
                "protocol": protocol,
            },
            stage="post",
        )
    return result


def read_sample(manifest) -> dict:
    """按清单读回具名物理数组及派生字段，校验 point 身份与分量。"""
    path = Path(manifest)
    metadata = json.loads(path.read_text())
    fields = {}
    for key, value in metadata["filemap"].items():
        member = Path(value)
        if member.name != str(member):
            raise ValueError("推理成员路径越界")
        fields[key] = load_named_tensor(path.parent / member)
    for domain in metadata["domains"].values():
        for declaration in domain.get("derived_fields", {}).values():
            value = fields[declaration["field"]]
            if value.shape != (len(fields[declaration["ids"]]), declaration["components"]):
                raise ValueError("派生字段与持久实体声明不一致")
    return {"metadata": metadata, "fields": fields}


def compare_results(reports: list[dict]) -> dict:
    """比较完整物理推理报告的口径；不加载模型或重算预测。

    每项为 physical-predictions.json 的内容，可附 run_id。模型权重允许不同；
    来源、准备、样本顺序、分片、执行精度及字段声明必须一致。
    """
    import math

    rows = [
        {"run_id": report.get("run_id"), "metrics": report.get("metrics", {})} for report in reports
    ]

    def outcome(status, reason):
        return {"status": status, "reason": reason, "rows": rows}

    if reports and all(r.get("version") == 2 for r in reports):
        return _compare_v2(reports, rows)
    if len(reports) < 2:
        return outcome("insufficient", "至少需要两份推理结果")
    signatures = []
    try:
        for report in reports:
            if report.get("status") != "succeeded" or not report.get("metrics"):
                return outcome("insufficient", "推理尚未完整交付评价指标")
            protocol = report.get("protocol", {})
            required = ("dataset", "preparation", "model", "samples", "split", "execution")
            if any(key not in protocol for key in required):
                return outcome("insufficient", "历史结果缺少完整比较协议")
            if protocol.get("digest") != fingerprint(
                {k: v for k, v in protocol.items() if k != "digest"}
            ):
                return outcome("incompatible", "推理协议摘要不一致")
            results = report.get("results", [])
            if [r.get("sample") for r in results] != protocol["samples"]:
                return outcome("insufficient", "实际样本未完整覆盖协议名单")
            fields, totals = [], {}
            for item in results:
                if not item.get("manifest"):
                    return outcome("insufficient", "缺少持久字段与实体声明")
                manifest = json.loads(Path(item["manifest"]).read_text())
                if manifest["protocol"] != protocol["digest"] or manifest.get(
                    "metrics"
                ) != item.get("metrics"):
                    return outcome("incompatible", "样本清单与推理报告不一致")
                fields.append({"identity": manifest["identity"], "domains": manifest["domains"]})
                if set(item["metrics"]) != set(report["metrics"]):
                    return outcome("incompatible", "样本与总体的评价字段不一致")
                for name, metrics in item["metrics"].items():
                    row = totals.setdefault(
                        name,
                        dict.fromkeys(
                            ("count", "squared_error", "absolute_error", "truth_squared"), 0
                        ),
                    )
                    for key in row:
                        value = metrics[key]
                        if (
                            not isinstance(value, (int, float))
                            or not math.isfinite(value)
                            or value < 0
                        ):
                            return outcome("incompatible", "无效指标累计量")
                        row[key] += value
            for name, total in totals.items():
                if not total["count"]:
                    return outcome("insufficient", "评价没有有效实体")
                metric = report["metrics"][name]
                expected = {
                    **total,
                    "mse": total["squared_error"] / total["count"],
                    "mae": total["absolute_error"] / total["count"],
                    "relative_l2": math.sqrt(total["squared_error"] / total["truth_squared"])
                    if total["truth_squared"]
                    else None,
                }
                for key, value in expected.items():
                    actual = metric[key]
                    if (value is None and actual is not None) or (
                        value is not None
                        and (
                            actual is None
                            or not math.isclose(actual, value, rel_tol=1e-10, abs_tol=1e-12)
                        )
                    ):
                        return outcome("incompatible", "总体指标与逐样本累计量不一致")
            settings = {
                key: value
                for key, value in protocol.get("settings", {}).items()
                if key
                not in {
                    "checkpoint",
                    "preparation",
                    "results",
                    "overwrite",
                    "save_predictions",
                    "export_vtk",
                }
            }
            signatures.append(
                {
                    **{key: protocol[key] for key in required},
                    "settings": settings,
                    "extensions": protocol.get("extensions", {}),
                    "fields": fields,
                    "metrics": sorted(report["metrics"]),
                }
            )
    except (KeyError, TypeError, ValueError, OSError) as exc:
        return outcome("incompatible", f"结果证据无效: {exc}")
    if any(signature != signatures[0] for signature in signatures[1:]):
        return outcome("incompatible", "数据、准备、样本、字段或执行口径不同")
    return outcome("comparable", None)


def _compare_v2(reports, rows):
    """新版支持只评价结果；只有同分片同口径的不同权重才能比较。"""
    signatures, weights = {}, {}

    def outcome(status, reason):
        return {"status": status, "reason": reason, "rows": rows}

    try:
        for report in reports:
            protocol = report.get("protocol", {})
            if report.get("status") != "succeeded":
                return outcome("insufficient", "存在未完整交付的结果")
            if fingerprint({k: v for k, v in protocol.items() if k != "digest"}) != protocol.get(
                "digest"
            ):
                return outcome("incompatible", "推理协议摘要失效")
            items = report.get("results", [])
            if [r.get("sample") for r in items] != protocol["samples"]:
                return outcome("insufficient", "样本未覆盖固定名单")
            for item in items:
                if item.get("evidence") != fingerprint(
                    {
                        k: item[k]
                        for k in ("identity", "fields", "metrics", "metric_records", "timings")
                    }
                ):
                    return outcome("incompatible", "结果指标或来源证据不一致")
                if not item.get("metric_records"):
                    return outcome("insufficient", "尚无评价指标")
            split = protocol["split"]
            signature = {
                k: protocol[k] for k in ("dataset", "preparation", "model", "samples", "execution")
            }
            signature["settings"] = {
                k: v
                for k, v in protocol["settings"].items()
                if k
                not in {
                    "checkpoint",
                    "preparation",
                    "results",
                    "overwrite",
                    "save_predictions",
                    "export_vtk",
                }
            }
            signature["extensions"] = protocol.get("extensions", {})
            signature["fields"] = [
                {"identity": r["identity"], "fields": r["fields"]} for r in items
            ]
            signature["metrics"] = [
                [
                    (r["field_id"], r.get("selected_metrics", list(r["values"])), r["algorithm"])
                    for r in item["metric_records"]
                ]
                for item in items
            ]
            if split in signatures and signatures[split] != signature:
                return outcome("incompatible", "同分片的样本、字段、算法或执行口径不一致")
            signatures[split] = signature
            weights.setdefault(split, set()).add(protocol["weights"])
    except (KeyError, TypeError, ValueError) as exc:
        return outcome("incompatible", f"结果证据无效: {exc}")
    if not any(len(v) > 1 for v in weights.values()):
        return outcome("insufficient", "同分片仅一份权重，可查看统计")
    return outcome("comparable", None)
