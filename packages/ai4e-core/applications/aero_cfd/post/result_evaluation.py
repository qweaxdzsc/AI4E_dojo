"""固定预测的评价、运行记录及显式导出；不读取模型或训练配置。"""

import csv
import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.eval.result_metrics import METRICS, evaluate_arrays
from ai4e_core.applications.aero_cfd.infer.results import read_sample


def metric_catalog():
    """返回固定结果可重算的评价指标。"""
    from ai4e_core.abilities.eval.catalog import metric_catalog as catalog

    return [m for m in catalog() if m["scope"] == "field"]


def evaluate_fields(
    sample: dict,
    *,
    selections: list[str] | None,
    metrics: list[str] | None = None,
    operation: Callable | None = None,
) -> list[dict]:
    """评价已经绑定的内存字段；与文件评价复用同一数值能力。"""
    from ai4e_core.abilities.eval.region_statistics import region_statistics

    from .field_binding import select_field

    rows = []
    arrays = sample["fields"]
    if not selections:
        selections = [
            f"{domain}:{name}:"
            + ("scalar" if arrays[key + ".prediction"].shape[1] == 1 else "magnitude")
            for domain, declaration in sample["metadata"]["domains"].items()
            for name, key in declaration["targets"].items()
        ]
    for selection in selections:
        domain, declaration, key, component = select_field(sample, selection)
        truth = arrays.get(key + ".truth")
        row = {
            "id": selection,
            "domain": domain,
            "field": key,
            "component": component,
            "unit": declaration.get("units", {}).get(selection.split(":")[1]),
            "region": "whole",
            "algorithm": "physical-metrics-v2",
        }
        prediction = arrays[key + ".prediction"]
        if component == "magnitude":
            values = np.linalg.norm(prediction.astype(np.float64), axis=1)
        else:
            index = 0 if component == "scalar" and prediction.shape[1] == 1 else int(component)
            if not 0 <= index < prediction.shape[1]:
                raise ValueError("分量选择不合法")
            values = prediction[:, index]
        row["statistics"] = {
            **region_statistics(
                values,
                mask=arrays[declaration["validity"]] if declaration.get("validity") else None,
            ),
            "field": key + ".prediction",
            "component": component,
            "unit": row["unit"],
        }
        if truth is None:
            row.update(
                values={},
                status="unavailable",
                reason="没有真值",
                count=row["statistics"]["count"],
                excluded=row["statistics"]["excluded"],
            )
        else:
            row.update(
                (operation or evaluate_arrays)(
                    arrays[key + ".prediction"],
                    truth,
                    component=component,
                    mask=arrays[declaration["validity"]] if declaration.get("validity") else None,
                    metrics=metrics,
                )
            )
            row["status"] = "succeeded"
        rows.append(row)
    return rows


def describe_result_fields(manifests):
    """只读张量头部获取分量，FakeTensorMode不载入场数组或模型权重。"""
    import torch
    from torch._subclasses.fake_tensor import FakeTensorMode

    result = {}
    for manifest in manifests:
        try:
            path = Path(manifest)
            meta = json.loads(path.read_text())
            counts = {}
            for domain in meta["domains"].values():
                for key in domain.get("targets", {}).values():
                    shapes = []
                    for suffix in (".prediction", ".truth"):
                        member = meta["filemap"][key + suffix]
                        if Path(member).name != member:
                            raise ValueError("结果成员路径越界")
                        with FakeTensorMode():
                            tensor = torch.load(path.parent / member, weights_only=True)
                        if not isinstance(tensor, torch.Tensor) or tensor.ndim != 2:
                            raise ValueError("缺少二维物理场声明")
                        shapes.append(tuple(tensor.shape))
                    if shapes[0] != shapes[1] or shapes[0][1] < 1:
                        raise ValueError("预测和真值分量不匹配")
                    counts[key] = shapes[0][1]
            result[manifest] = {"components": counts}
        except (ValueError, KeyError, OSError, RuntimeError, TypeError) as exc:
            result[manifest] = {"error": str(exc)}
    return result


def _verify(item):
    for file in item["files"]:
        path = Path(file["path"])
        h = hashlib.sha256()
        with path.open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                h.update(block)
        if h.hexdigest() != file["revision"]:
            raise ValueError("来源修订变化: " + path.name)


def evaluate_result(item, selections, metrics):
    """逐样本读回，核对固定成员、域和实体；每个字段返回独立状态。"""
    _verify(item)
    sample = read_sample(item["manifest"])
    meta, arrays = sample["metadata"], sample["fields"]
    if meta.get("identity", {}).get("sample") not in (None, item["sample"]):
        raise ValueError("样本身份不匹配")
    rows = []
    for selection in selections:
        row = {
            "result_id": item["id"],
            "batch_id": item["batch_id"],
            "run_id": item["run_id"],
            "sample": item["sample"],
            "split": item.get("split", "unknown"),
            "algorithm": "physical-metrics-v2",
            "checkpoint": item["checkpoint"],
            **selection,
            "id": item["id"] + ":" + selection["id"],
            "field_id": selection["id"],
            "calculated_at": datetime.now(UTC).isoformat(),
            "status": "succeeded",
            "source_revision": item["revision"],
            "identity": meta.get("identity", {}),
            "protocol": meta.get("protocol"),
            "values": {},
        }
        try:
            domain = meta["domains"][selection["domain"]]
            key = domain["targets"][selection["field"]]
            pred, truth = arrays[key + ".prediction"], arrays[key + ".truth"]
            ids = np.asarray(arrays[domain["ids"]])
            if ids.ndim != 1 or len(np.unique(ids)) != len(ids) or len(ids) != len(pred):
                raise ValueError("实体ID不唯一或数量不匹配")
            if domain.get("truth_ids") and not np.array_equal(ids, arrays[domain["truth_ids"]]):
                raise ValueError("预测和真值实体顺序不一致")
            row.update(
                evaluate_arrays(
                    pred,
                    truth,
                    component=selection["component"],
                    mask=arrays[domain["validity"]] if domain.get("validity") else None,
                    metrics=metrics,
                )
            )
            row["unit"] = domain.get("units", {}).get(selection["field"])
        except (KeyError, ValueError, TypeError) as exc:
            row.update(status="failed", error=str(exc))
        rows.append(row)
    _verify(item)
    return rows


def run_evaluation(job, *, runtime):
    """计算固定结果；运行外围由调用方注入，数据逐样本追加以保留部分交付。"""
    destination = Path(job["data_dir"])
    destination.mkdir(parents=True, exist_ok=True)
    rows, failed = [], 0

    def process(item):
        runtime.logger.info("[post/指标/开始] %s", item["sample"])
        try:
            return evaluate_result(item, job["request"]["fields"], job["request"]["metrics"])
        except Exception as exc:  # noqa: BLE001 - 单个坏结果保留失败行，继续其它样本。
            return [
                {
                    "id": item["id"] + ":" + field["id"],
                    "field_id": field["id"],
                    "result_id": item["id"],
                    "batch_id": item["batch_id"],
                    "run_id": item["run_id"],
                    "sample": item["sample"],
                    "split": item.get("split", "unknown"),
                    "algorithm": "physical-metrics-v2",
                    "checkpoint": item["checkpoint"],
                    "field": field["field"],
                    "domain": field["domain"],
                    "component": field["component"],
                    "status": "failed",
                    "error": str(exc),
                    "values": {},
                    "calculated_at": datetime.now(UTC).isoformat(),
                }
                for field in job["request"]["fields"]
            ]

    # 一行是一份完整样本结果；强制结束产生的最后半行由读端忽略。
    with (destination / "metrics.jsonl").open("x", encoding="utf-8") as journal:
        for current in runtime.execute_samples(job["inputs"], process):
            journal.write(json.dumps(current, ensure_ascii=False) + "\n")
            journal.flush()
            rows.extend(current)
            failed += sum(row["status"] == "failed" for row in current)
            runtime.artifact("post-metrics.json", {"status": "running", "completed": len(rows)})
            runtime.publish({"completed": len(rows), "failed": failed})
    status = "canceled" if runtime.canceled() else "partial" if failed else "succeeded"
    save_json(
        destination / "metrics.json",
        {
            "version": 1,
            "algorithm": "physical-metrics-v1",
            "rows": rows,
            "status": status,
            "selection": job["request"],
            "calculated_at": datetime.now(UTC).isoformat(),
        },
    )
    runtime.artifact(
        "post-metrics.json",
        {
            "status": status,
            "completed": len(rows),
            "path": str(destination / "metrics.json"),
        },
    )
    runtime.logger.info("[post/指标/结束] %s", status)
    return {"status": status, "completed": len(rows), "failed": failed}


def export_evaluation(record, path, *, format, row_ids=None):
    """显式导出固定评价行，完整保留数值、来源、单位和失败状态。"""
    rows = record["rows"]
    if row_ids is not None:
        if len(row_ids) != len(set(row_ids)) or set(row_ids) - {r["id"] for r in rows}:
            raise ValueError("导出行不存在或重复")
        rows = [r for r in rows if r["id"] in row_ids]
    if format == "json":
        save_json(path, {**record, "rows": rows})
    elif format == "xlsx":
        from ai4e_core.abilities.report import export_tables

        export_tables(path, {"指标": [{**r, **r["values"]} for r in rows]}, format="xlsx")
    elif format == "csv":
        names = [
            "sample",
            "split",
            "algorithm",
            "field_id",
            "protocol",
            "batch_id",
            "run_id",
            "checkpoint",
            "domain",
            "field",
            "component",
            "unit",
            *METRICS,
            "status",
            "error",
            "undefined",
            "count",
            "excluded",
            "source_revision",
            "calculated_at",
        ]
        with (
            atomic_path(path) as temporary,
            temporary.open("w", encoding="utf-8-sig", newline="") as stream,
        ):
            writer = csv.DictWriter(stream, fieldnames=names, extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                value = {**row, **row["values"]}
                for key, val in list(value.items()):
                    if isinstance(val, (dict, list)):
                        value[key] = json.dumps(val, ensure_ascii=False)
                    elif isinstance(val, str) and val.startswith(("=", "+", "-", "@")):
                        value[key] = "'" + val
                writer.writerow(value)
    else:
        raise ValueError("只支持CSV或JSON")
