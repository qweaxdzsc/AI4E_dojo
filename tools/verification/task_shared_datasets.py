"""项目共享数据迁移与全文件核验；真实运行证据保存到指定报告目录。"""

import argparse
import json
from pathlib import Path

import ai4e_task as task
from ai4e_task.storage.snapshots import inventory


def migrate(project: Path, reports: Path, *, execute: bool) -> list[dict]:
    """先记录正式候选；执行时核验源文件不变及每个复制成员的 SHA256。"""
    reports.mkdir(parents=True, exist_ok=True)
    plan = task.migrate_shared_datasets(project)
    (reports / "migration-plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2))
    if not execute:
        return plan
    sources = {item["name"]: inventory(Path(item["source_manifest"]).parent) for item in plan}
    result = task.migrate_shared_datasets(project, dry_run=False)
    for item in result:
        before = sources[item["name"]]
        after = inventory(Path(item["source_manifest"]).parent)
        copied = inventory(Path(item["target"]))
        assert before == after, "迁移期间原文件发生变化"
        mismatched = [
            key
            for key, value in before.items()
            if key != "manifest.json" and copied.get(key) != value
        ]
        assert not mismatched, mismatched
        item.update(
            source_unchanged=True, checked_files=len(before), matching_copied_files=len(before) - 1
        )
        (reports / (item["name"] + "-file-checksums.json")).write_text(
            json.dumps({"source": before, "shared": copied}, indent=2)
        )
    (reports / "migration-result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2))
    assert all(
        item["status"] == "already_migrated"
        for item in task.migrate_shared_datasets(project, dry_run=False)
    )
    return result


def consume(project: Path, reports: Path, name: str, workdir: Path) -> list[dict]:
    """在两个新任务完成真实准备、单轮 CPU 短训和独立推理；不读取原始网格。"""
    import os
    import shutil

    import yaml

    root = Path(__file__).resolve().parents[2]
    source = workdir / "recipe"
    reports.mkdir(parents=True, exist_ok=True)
    source.mkdir(parents=True, exist_ok=True)
    shutil.copytree(root / "examples/aero_cfd/shapenet_car_abupt", source, dirs_exist_ok=True)
    shutil.copyfile(root / "recipes/aero_cfd/task-entry.json", source / "task-entry.json")
    shared = task.get_shared_dataset(project, name)
    forbidden = shared.get("migration", {}).get("source_manifest")
    if forbidden:
        forbidden = str(Path(forbidden).parent.resolve())
        pipeline = source / "pipeline.py"
        guard = "import sys, os\n" + "_forbidden = " + repr(forbidden) + "\n"
        guard += "def _isolate(event, args):\n    if event in {'open', 'os.listdir', 'os.scandir'} and args and isinstance(args[0], (str, bytes)):\n        location = os.path.realpath(os.fsdecode(args[0]))\n        if location == _forbidden or location.startswith(_forbidden + os.sep):\n            raise PermissionError('original task data is isolated')\nsys.addaudithook(_isolate)\n"
        pipeline.write_text(guard + pipeline.read_text())
    m = json.loads(Path(shared["manifest_path"]).read_text())
    train = m["partitions"]["train"][0]
    test = m["partitions"]["test"][0]
    cfg = yaml.safe_load((source / "config.yaml").read_text())
    cfg["dataset"].update(
        root="/unavailable-original-grid",
        samples={"train": [train], "test": [test]},
        processed_name=name,
    )
    cfg["train"].update(
        manifest=shared["manifest_path"],
        device="cpu",
        max_epochs=1,
        test_repeat=1,
        snapshot=False,
        optimizer="adamw",
        scheduler="constant",
    )
    cfg["model"]["parameters"].update(
        dim=24,
        geometry_depth=1,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    s = cfg["model"]["sampling"]
    s["geometry"]["max_points"] = 128
    s["supernodes"]["num_points"] = 8
    for v in s["domains"].values():
        v["anchor"]["num_points"] = 8
        v["query"]["num_points"] = 16
    cfg["infer"].update(
        samples=[test],
        split="test",
        query=False,
        export_vtk=False,
        device="cpu",
        evaluate=True,
        save_predictions=True,
    )
    cfg["trainprep"]["split"] = {"method": "original", "samples": [train, test]}
    cfg["pipeline"]["stages"] = ["trainprep", "train"]
    (source / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
    results = []
    for label in ["shared-consumer-a", "shared-consumer-b"]:
        item = task.new_task(project, label, source=source)
        current = task.read_configuration(project, item["id"])
        task.bind_shared_dataset(project, item["id"], name, revision=current["revision"])
        run = task.wait_run(project, task.submit_run(project, item["id"])["id"], timeout=240)
        assert run["status"] == "succeeded", (
            run.get("error"),
            task.read_log(project, run["id"])[-5000:],
        )
        prep = str(Path(run["run_dir"]) / "artifacts/preparation.json")
        weight = str(Path(run["run_dir"]) / "checkpoints/last.pt")
        inferred = task.wait_run(
            project,
            task.submit_run(
                project,
                item["id"],
                overrides=[
                    "pipeline.stages=[infer]",
                    "train.preparation=" + prep,
                    "infer.preparation=" + prep,
                    "infer.checkpoint=" + weight,
                ],
            )["id"],
            timeout=240,
        )
        assert inferred["status"] == "succeeded", (
            inferred.get("error"),
            task.read_log(project, inferred["id"])[-5000:],
        )
        results.append(
            {
                "task": item["id"],
                "training": run["id"],
                "inference": inferred["id"],
                "shared": shared["manifest_path"],
                "train_samples": [train],
                "test_samples": [test],
                "epochs": 1,
                "device": "cpu",
                "raw_grid": "unavailable",
                "isolated_original_data": forbidden,
                "prediction": str(Path(inferred["run_dir"]) / "artifacts/inference-results.json"),
            }
        )
        (reports / "real-two-consumers.json").write_text(
            json.dumps(results, indent=2, ensure_ascii=False)
        )
        print(results[-1], flush=True)
    return results


def main():
    """默认只预览，--execute 执行已经明确指定的项目迁移。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--reports", type=Path, required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--consume", action="store_true")
    parser.add_argument("--dataset", default="shapenet_car4")
    parser.add_argument("--workdir", type=Path)
    args = parser.parse_args()
    if args.consume:
        if not args.workdir:
            parser.error("--consume requires --workdir")
        result = consume(args.project, args.reports, args.dataset, args.workdir)
    else:
        result = migrate(args.project, args.reports, execute=args.execute)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
