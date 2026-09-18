"""历史任务副本的小样本运行演练；不替换正式任务或历史科学产物。"""

import argparse
import json
import os
import shutil
import time
from pathlib import Path

import ai4e_task as task
import numpy as np
import torch
import yaml

from tools.migration.recipe_conventions.transaction import inventory

ROOT = Path(__file__).resolve().parents[3]


def compare_state(left, right):
    """精确核对完整恢复状态，运行配置中的输出位置另行保留。"""
    if isinstance(left, torch.Tensor):
        torch.testing.assert_close(left, right, rtol=0, atol=0)
    elif isinstance(left, np.ndarray):
        np.testing.assert_array_equal(left, right)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            compare_state(left[key], right[key])
    elif isinstance(left, (tuple, list)):
        assert type(left) is type(right) and len(left) == len(right)
        for a, b in zip(left, right, strict=True):
            compare_state(a, b)
    else:
        assert left == right


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=900)
    parser.add_argument("--keep-going", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    os.environ.update(OMP_NUM_THREADS="1", VECLIB_MAXIMUM_THREADS="1")
    started = time.monotonic()
    reports = []
    for item in json.loads(args.evidence.read_text()):
        if time.monotonic() - started >= args.seconds - 30:
            raise TimeoutError("演练总预算不足，不启动新任务")
        before = time.monotonic()
        base = args.output / item["task"]
        base.mkdir()
        original = Path(item["bundle"]) / "original"
        source = base / "candidate"
        shutil.copytree(Path(item["bundle"]) / "candidate", source)
        physical = "train import physical as fitting" in (original / "train.py").read_text()
        template = ROOT / ("examples/aero_cfd/shapenet_car_abupt" if physical else "recipes/aero_cfd")
        for name in ("configuration.py", "rawprep.py", "trainprep.py", "train.py", "infer.py", "post.py"):
            shutil.copyfile(template / name, source / name)
        record = {"task": item["task"], "source_kind": "physical" if physical else "native",
                  "candidate": str(source), "original_digest": inventory(original), "runs": []}
        reports.append(record)
        try:
            cfg = yaml.safe_load((source / "config.yaml").read_text())
            reference = cfg["inputs"]["trainprep"]["dataset"]
            if not reference or not Path(reference).is_file():
                prepared = cfg["inputs"]["train"].get("preparation")
                if not prepared or not Path(prepared).is_file():
                    raise FileNotFoundError("原引用与冻结准备都没有可用清单")
                reference = json.loads(Path(prepared).read_text())["manifest"]
            manifest = json.loads(Path(reference).read_text())
            partitions = {k: v[:1] for k, v in manifest["partitions"].items() if v}
            keys = {(k, v[0]) for k, v in partitions.items()}
            samples = [r for r in manifest["samples"] if (r["partition"], r["sample"]) in keys]
            for r in samples:
                r["path"] = str((Path(reference).parent / r["path"]).resolve())
            manifest.update(partitions=partitions, samples=samples)
            statistics = manifest.get("statistics")
            if isinstance(statistics, dict) and statistics.get("path"):
                statistics["path"] = str((Path(reference).parent / statistics["path"]).resolve())
            subset = base / "manifest.json"
            subset.write_text(json.dumps(manifest))
            cfg["inputs"]["trainprep"]["dataset"] = str(subset)
            for stage in ("train", "infer", "post"):
                cfg["inputs"][stage] = {k: None for k in cfg["inputs"][stage]}
            cfg["data_root"], cfg["run_root"] = str(base / "data"), str(base / "runs")
            cfg["pipeline"]["stages"] = ["trainprep", "train", "infer", "post"]
            cfg["train"].update(max_epochs=2, device="cpu", snapshot=False)
            cfg["trainprep"].pop("split", None)
            cfg["model"]["parameters"].update(dim=24, geometry_depth=1, num_heads=3, blocks="psc",
                num_domain_decoder_blocks={k: 1 for k in cfg["trainprep"]["domains"]})
            sampling = cfg["model"]["sampling"]
            sampling["geometry"]["max_points"] = 32
            sampling["supernodes"]["num_points"] = 4
            for domain in sampling["domains"].values():
                domain["anchor"]["num_points"] = 4
                if domain.get("query"):
                    domain["query"]["num_points"] = 0
            split = "test" if partitions.get("test") else "train"
            cfg["infer"].update(device="cpu", split=split, samples=partitions[split], export_vtk=False,
                                query_chunk_size=4096)
            cfg["post"]["snapshot_every"] = 0
            (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
            pipeline = source / "pipeline.py"
            # 只在验收副本保留第一轮完整状态，总训练目标始终为两轮。
            retain = '''\nfrom ai4e_core.run import TrainingRun as _Run
_checkpoint = _Run.checkpoint
def _retain_first(self, label, payload, **kwargs):
    result = _checkpoint(self, label, payload, **kwargs)
    if payload.get("epoch") == 1:
        _checkpoint(self, "last", payload, namespace="epoch1")
    return result
_Run.checkpoint = _retain_first
\n'''
            code = pipeline.read_text()
            marker = 'if __name__ == "__main__":'
            if marker not in code:
                raise ValueError("候选没有可核验的直接入口")
            pipeline.write_text(code.replace(marker, retain + "\n" + marker))
            project = base / "project"
            task.create_project(project)
            current = task.new_task(project, "historical migration", source=source)

            def execute(overrides=(), *, project=project, current=current, record=record):
                result = task.submit_run(project, current["id"], overrides=list(overrides))
                result = task.wait_run(project, result["id"], timeout=min(120, args.seconds - (time.monotonic() - started)))
                record["runs"].append({k: result[k] for k in ("id", "status", "run_dir")})
                if result["status"] != "succeeded":
                    if result["status"] not in {"failed", "stopped"}:
                        task.stop_run(project, result["id"])
                    raise RuntimeError(task.read_log(project, result["id"]))
                return Path(result["run_dir"])

            first = execute()
            prepared = first / "artifacts/preparation.json"
            resumed = execute(["pipeline.stages=[train]", f"inputs.train.preparation={prepared}",
                               f"inputs.train.resume={first / 'checkpoints/epoch1/last.pt'}"])
            a, b = [torch.load(p / "checkpoints/last.pt", weights_only=False, map_location="cpu")
                    for p in (first, resumed)]
            matched = sorted(set(a) - {"effective_config"})
            for key in matched:
                compare_state(a[key], b[key])
            results = first / "artifacts/inference-results.json"
            execute(["pipeline.stages=[post]", f"inputs.post.results={results}",
                     "inputs.infer.checkpoint=/unavailable.pt"])
            assert len(task.get_lineage(project)) == 1
            record.update(status="passed", scope="small original-data handoff, not full historical training",
                          samples=partitions, resume="exact_training_state", matched_state=matched, lineage_versions=1)
        except Exception as exc:  # noqa: BLE001 - 每个失败均保留，不当作缺环境跳过
            record.update(status="failed", error=str(exc))
        record["seconds"] = time.monotonic() - before
        (args.output / "report.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2))
        print(item["task"], record["status"], round(record["seconds"], 2), flush=True)
        if record["status"] == "failed" and not args.keep_going:
            break
    return int(any(r["status"] != "passed" for r in reports))


if __name__ == "__main__":
    raise SystemExit(main())
