"""固定预测的评价、运行记录及显式导出；不读取模型或训练配置。"""

import csv
import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

from ai4e_core.abilities.data.save.arrays import atomic_path, save_json
from ai4e_core.abilities.eval.result_metrics import METRICS, evaluate_arrays
from ai4e_core.applications.aero_cfd.infer.results import read_sample
from ai4e_core.run import RunWriter


def metric_catalog():
    """返回固定结果可重算的评价指标。"""
    from ai4e_core.abilities.eval.catalog import metric_catalog as catalog
    return [m for m in catalog() if m["scope"] == "field"]


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


def run_evaluation(job, *, publish, canceled):
    """在独立评价运行中逐样本计算；writer写运行，save写数据。"""
    directory = Path(job["run_dir"])
    directory.mkdir(parents=True, exist_ok=False)
    (directory / "inputs").mkdir()
    (directory / "logs").mkdir()
    writer = RunWriter(directory)
    writer.write_inputs(None, job["request"])
    writer.write_provenance({k: job[k] for k in ("run_id", "task_id", "version_id")})
    logger = logging.getLogger("dojo.post.metrics." + job["id"])
    handler = writer.attach_log(logger)
    rows, status = [], "running"
    try:
        for item in job["inputs"]:
            if canceled():
                status = "canceled"
                break
            logger.info("[post/指标/开始] %s", item["sample"])
            try:
                current = evaluate_result(item, job["request"]["fields"], job["request"]["metrics"])
            except Exception as exc:  # noqa: BLE001 - 单个坏结果返回失败行，不中断其他样本。
                current = [
                    {
                        "id": item["id"] + ":" + f["id"],
                        "field_id": f["id"],
                        "result_id": item["id"],
                        "batch_id": item["batch_id"],
                        "run_id": item["run_id"],
                        "sample": item["sample"],
            "split": item.get("split", "unknown"),
            "algorithm": "physical-metrics-v2",
                        "checkpoint": item["checkpoint"],
                        "field": f["field"],
                        "domain": f["domain"],
                        "component": f["component"],
                        "status": "failed",
                        "error": str(exc),
                        "values": {},
                        "calculated_at": datetime.now(UTC).isoformat(),
                    }
                    for f in job["request"]["fields"]
                ]
            rows.extend(current)
            record = {
                "version": 1,
                "algorithm": "physical-metrics-v1",
                "rows": rows,
                "status": "running",
            }
            save_json(Path(job["data_dir"]) / "metrics.json", record)
            writer.write_artifact(
                "post-metrics.json", {"status": "running", "completed": len(rows)}
            )
            publish({"completed": len(rows), "failed": sum(r["status"] == "failed" for r in rows)})
        if status != "canceled":
            status = (
                "canceled"
                if canceled()
                else "partial"
                if any(r["status"] == "failed" for r in rows)
                else "succeeded"
            )
        record = {
            "version": 1,
            "algorithm": "physical-metrics-v1",
            "rows": rows,
            "status": status,
            "selection": job["request"],
            "calculated_at": datetime.now(UTC).isoformat(),
        }
        save_json(Path(job["data_dir"]) / "metrics.json", record)
        writer.write_artifact(
            "post-metrics.json",
            {
                "status": status,
                "completed": len(rows),
                "path": str(Path(job["data_dir"]) / "metrics.json"),
            },
        )
        writer.write_summary(
            {
                "failed": status != "succeeded",
                "reports": {"post": {"status": status}},
                "run_dir": str(directory),
            }
        )
        logger.info("[post/指标/结束] %s", status)
        return {
            "status": status,
            "completed": len(rows),
            "failed": sum(r["status"] == "failed" for r in rows),
        }
    except BaseException as exc:
        writer.write_summary({"failed": True, "error": str(exc), "reports": {}})
        raise
    finally:
        logger.removeHandler(handler)
        handler.close()


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
