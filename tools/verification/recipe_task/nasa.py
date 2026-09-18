"""已随机抽中的 NASA CRM/AB-UPT：原始数据到固定 post 的直接/Task 实跑。"""

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

import ai4e_task as task
import torch
import yaml

from ai4e_contrib.application.datasets.nasa_crm.adapter import RawDataset

ROOT = Path(__file__).resolve().parents[3]


def compare_predictions(left, right):
    """读回全部具名数组；固定预测与逐分量指标都需对齐。"""
    from ai4e_core.applications.aero_cfd.infer.results import read_sample

    a, b = (json.loads(Path(path).read_text()) for path in (left, right))
    assert a["metrics"] == b["metrics"]
    assert len(a["results"]) == len(b["results"])
    for x, y in zip(a["results"], b["results"], strict=True):
        assert (x["sample"], x["split"], x["metrics"]) == (y["sample"], y["split"], y["metrics"])
        u, v = read_sample(x["manifest"])["fields"], read_sample(y["manifest"])["fields"]
        assert u.keys() == v.keys()
        for key in u:
            torch.testing.assert_close(u[key], v[key], rtol=1e-4, atol=1e-6)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    base = args.output.resolve()
    base.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    source = base / "recipe"
    shutil.copytree(ROOT / "examples/aero_cfd/nasa_crm_abupt", source)
    cfg = yaml.safe_load((source / "config.yaml").read_text())
    raw = Path("/Users/zonghui/work/datasets/NASA")
    cfg["inputs"]["rawprep"].update(
        source=str(raw), train_h5=str(raw / "Case 4 - NASA CRM 2/trainingData_NASA-CRM.h5"),
        test_h5=str(raw / "Case 4 - NASA CRM/testData_NASA-CRM.h5"),
        connectivity_h5=str(raw / "Case 4 - NASA CRM/connectivity_NASA-CRM.h5"),
    )
    available = RawDataset({**cfg["dataset"], **cfg["inputs"]["rawprep"]})
    samples = {s: available.partitions[s][:2] for s in ("train", "test")}
    cfg["dataset"].update(samples=samples, processed_name="nasa_recipe_contract")
    cfg["inputs"]["trainprep"]["dataset"] = None
    cfg["train"].update(max_epochs=2, device="cpu", snapshot=False, test_repeat=1)
    cfg["model"]["parameters"].update(dim=24, num_heads=3, geometry_depth=1, blocks="ps", num_domain_decoder_blocks={"surface":1})
    sampling = cfg["model"]["sampling"]
    sampling["geometry"]["max_points"] = 256
    sampling["supernodes"]["num_points"] = 16
    sampling["domains"]["surface"]["anchor"]["num_points"] = 16
    cfg["infer"].update(device="cpu", samples=samples["test"], export_vtk=False)
    cfg["run_root"] = str(base / "runs")
    cfg["data_root"] = str(base / "data")
    project = base / "project"
    task.create_project(project)
    (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    managed = task.new_task(project, "NASA comparison", source=source)
    # 固定总训练目标，复制目录使用公开回调额外保留第一轮状态供恢复对照。
    train_script = source / "train.py"
    code = train_script.read_text()
    code = code.replace("    return fitting.execute_training(job)", """    from ai4e_core.abilities.training.checkpoint import capture
    def retain_first(context):
        if context.epoch == 1:
            payload = capture(job.model, job.optimizer, epoch=context.epoch,
                updates=context.updates, best=float('inf'), contract=job.contract,
                scheduler=job.scheduler)
            session.checkpoint("best", payload)
    job = fitting.configure_callbacks(job, callbacks=(retain_first,))
    return fitting.execute_training(job)""")
    train_script.write_text(code)
    # Task 捕获必须包含同一份公开扩展。
    managed_recipe = Path(task.get_task(project, managed["id"])["directory"]) / "recipe/train.py"
    managed_recipe.write_text(code)
    report = {"case": "nasa_crm_abupt", "samples": samples, "runs": []}

    def direct(stage):
        cfg["pipeline"]["stages"] = [stage]
        (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        with (base / f"{stage}-{cfg['train']['max_epochs']}.log").open("w") as log:
            subprocess.run([sys.executable, str(source / "pipeline.py")], cwd=base,
                stdout=log, stderr=subprocess.STDOUT, check=True,
                timeout=max(1,10800-(time.monotonic()-started)))
        file = max((base / "runs").glob("*/summary.json"), key=lambda p:p.stat().st_mtime_ns)
        summary = json.loads(file.read_text())
        report["runs"].append({"mode":"direct","stage":stage,"run_dir":str(file.parent)})
        return file.parent, summary

    def managed_run(stage, extra=()):
        if time.monotonic()-started>=10500:
            raise TimeoutError("预算不足，不启动新计算")
        run = task.submit_run(project, managed["id"], overrides=[f"pipeline.stages=[{stage}]",*extra])
        result = task.wait_run(project,run["id"],timeout=max(1,10800-(time.monotonic()-started)))
        if result["status"] not in {"succeeded","failed","stopped"}:
            task.stop_run(project,run["id"])
        if result["status"]!="succeeded":
            raise RuntimeError(task.read_log(project,run["id"]))
        report["runs"].append({"mode":"task","stage":stage,"run_dir":result["run_dir"]})
        return Path(result["run_dir"]), result

    try:
        _, raw_a = direct("rawprep")
        _, _raw_b = managed_run("rawprep")
        left_dataset = str(Path(raw_a["data_dir"]) / "rawprep/manifest.json")
        right_dataset = str(project / "shared/datasets/nasa_recipe_contract/content/manifest.json")
        cfg["inputs"]["trainprep"]["dataset"] = left_dataset
        prep_a, _ = direct("trainprep")
        prep_b, _ = managed_run("trainprep", [f"inputs.trainprep.dataset={right_dataset}"])
        prepared_a, prepared_b = str(prep_a/"artifacts/preparation.json"),str(prep_b/"artifacts/preparation.json")
        cfg["inputs"]["train"]["preparation"] = prepared_a
        train_a, _ = direct("train")
        train_b, _ = managed_run("train", [f"inputs.train.preparation={prepared_b}"])
        for epochs in (1,2):
            if epochs==2:
                cfg["train"]["max_epochs"] = 2
                cfg["inputs"]["train"]["resume"] = str(train_a/"checkpoints/best.pt")
                train_a, _ = direct("train")
                train_b, _ = managed_run("train", [f"inputs.train.preparation={prepared_b}",
                    f"inputs.train.resume={train_b/'checkpoints/best.pt'}","train.max_epochs=2"])
            a=torch.load(train_a/"checkpoints/last.pt",map_location="cpu",weights_only=False)
            b=torch.load(train_b/"checkpoints/last.pt",map_location="cpu",weights_only=False)
            for key in a["model"]:
                torch.testing.assert_close(a["model"][key],b["model"][key],rtol=1e-4,atol=1e-6)
        cfg["inputs"]["infer"].update(preparation=prepared_a,checkpoint=str(train_a/"checkpoints/last.pt"))
        infer_a,_=direct("infer")
        infer_b,_=managed_run("infer",[f"inputs.infer.preparation={prepared_b}",f"inputs.infer.checkpoint={train_b/'checkpoints/last.pt'}"])
        result_a,result_b=infer_a/"artifacts/inference-results.json",infer_b/"artifacts/inference-results.json"
        compare_predictions(result_a, result_b)
        cfg["inputs"]["post"]["results"]=str(result_a)
        direct("post")
        managed_run("post",[f"inputs.post.results={result_b}"])
        report["status"]="passed"
    except Exception as exc:  # noqa: BLE001 - 失败也必须计入同一计算账本
        report.update(status="failed",error=str(exc))
    report["seconds"]=time.monotonic()-started
    (base/"report.json").write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False))
    return int(report["status"]!="passed")


if __name__=="__main__":
    raise SystemExit(main())
