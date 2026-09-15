"""在独立项目中准备真实 CFD 的推理浏览器验收，不更改已有用户任务。"""

import argparse
import json
from pathlib import Path

import ai4e_task as task
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings
from fastapi.testclient import TestClient


def prepare(root: Path, source: Path, *, cross_split: bool = False) -> dict:
    """用真实三辆车创建一个训练样本、两个推理样本及两份不同轮次权重。"""
    repository = Path(__file__).resolve().parents[2]
    root.mkdir(parents=True, exist_ok=True)
    evidence = root / "context.json"
    if evidence.exists():
        return json.loads(evidence.read_text())
    names = []
    for file in sorted(source.glob("param1/*/quadpress_smpl.vtk")):
        if (file.parent / "hexvelo_smpl.vtk").is_file():
            names.append(str(file.parent.relative_to(source)))
        if len(names) == 3:
            break
    if len(names) != 3:
        raise ValueError("需要三份真实 ShapeNet-Car 数据")
    settings = Settings(root / "platform", repository / "recipes/aero_cfd", [source])
    with TestClient(create_app(settings)) as client:
        project = client.post("/api/v1/projects", json={"name": "真实 CFD 推理验收"}).json()["id"]
        response = client.post(
            f"/api/v1/projects/{project}/tasks",
            json={"name": "Transolver 推理", "case_id": "shapenet_car_transolver3_surface"},
        )
        response.raise_for_status()
        item = response.json()
        base = client.app.state.services.project(project)
        identity = item["id"]
        config = task.read_configuration(base, identity)
        config = task.save_configuration(
            base,
            identity,
            {
                "dataset": {
                    "root": str(source),
                    "partition": {"train": names[:1], "eval": names[1:2], "test": names[2:]} if cross_split else {"train": names[:1], "test": names[1:]},
                    "samples": "all",
                },
                "data_root": str(root / "outputs"),
                "run_root": str(root / "runs"),
                "train": {"device": "cpu", "max_epochs": 2, "snapshot": False},
                "model": {
                    "parameters": {"n_hidden": 16, "n_layers": 2, "n_head": 4, "slice_num": 4},
                    "sampling": {"stride": 4, "chunk_count": 1},
                },
            },
            revision=config["revision"],
        )

        def run(stages, keys, overrides=()):
            record = task.submit_run(
                base,
                identity,
                input_keys=keys,
                overrides=["pipeline.stages=" + json.dumps(stages), *overrides],
            )
            result = task.wait_run(base, record["id"], timeout=600)
            if result["status"] != "succeeded":
                raise RuntimeError(task.read_log(base, result["id"]))
            return result

        raw = run(["rawprep"], ["dataset.root", "dataset.partition"])
        config = task.save_configuration(
            base,
            identity,
            {"train": {"manifest": str(Path(raw["data_dir"]) / "manifest.json")}},
            revision=config["revision"],
        )
        first = run(["trainprep", "train"], ["train.manifest"])
        prep = str(Path(first["run_dir"]) / "artifacts/preparation.json")
        second = run(
            ["train"],
            ["train.preparation"],
            ["train.preparation=" + json.dumps(prep), "train.max_epochs=1"],
        )
        checkpoint_ids = [r["id"] + ":last.pt" for r in [first, second]]
        value = {
            "project": project,
            "task": identity,
            "project_directory": str(base),
            "platform_root": str(settings.root),
            "data_root": str(source),
            "checkpoint_ids": checkpoint_ids,
            "samples": names[1:],
            "sample_selection": [{"split":s,"sample":n} for s,n in zip(("train","eval","test"),names)] if cross_split else [{"split":"test","sample":n} for n in names[1:]],
            "raw_run": raw["id"],
            "training_runs": [first["id"], second["id"]],
            "budget": {
                "device": "cpu",
                "epochs": [2, 1],
                "training_samples": 1,
                "note": "真实 CFD 输入与完整表面输出；小模型交接验收，不代表生产精度",
            },
        }
        evidence.write_text(json.dumps(value, ensure_ascii=False, indent=2))
        return value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--cross-split", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps(
            prepare(args.root.resolve(), args.source.resolve(), cross_split=args.cross_split), ensure_ascii=False, indent=2
        )
    )
