"""SafeDiffCon 托管入口的阶段选择、输入捕获和运行目录约束。"""

import importlib.util
import json
import sys
from pathlib import Path

import ai4e_task as task
import pytest
from omegaconf import OmegaConf

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / "recipes/safediffcon"


@pytest.fixture
def entry_module(monkeypatch):
    """隔离同名研究脚本导入，测试后恢复调用者环境。"""
    monkeypatch.syspath_prepend(str(RECIPE))
    names = ["configuration", "infer", "post", "posttrain", "rawprep", "train", "trainprep"]
    prior = {name: sys.modules.pop(name) for name in names if name in sys.modules}
    spec = importlib.util.spec_from_file_location("control_task_entry", RECIPE / "pipeline.py")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
        yield module
    finally:
        for name in names:
            sys.modules.pop(name, None)
        sys.modules.update(prior)


@pytest.mark.parametrize("selection", ["[]", "[train,train]"])
def test_reject_invalid_stage_selection(entry_module, selection):
    with pytest.raises(ValueError, match="非空、无重复"):
        entry_module.load_configuration(RECIPE / "config.yaml", [f"pipeline.stages={selection}"])


def test_selected_flow_passes_actual_predecessor_results(entry_module, monkeypatch):
    seen = []

    def stage(name, fn, cfg, *args):
        seen.append((name, args))
        return name + "-output"

    monkeypatch.setattr(entry_module.run, "stage", stage)
    cfg = OmegaConf.create({"pipeline": {"stages": ["post", "infer", "posttrain", "train"]}})
    assert entry_module.pipeline(cfg) == "post-output"
    assert seen == [
        ("train", (None,)),
        ("posttrain", (None, "train-output")),
        ("infer", (None, "posttrain-output")),
        ("post", ("infer-output",)),
    ]


def test_unknown_stage_is_recorded_as_incomplete(entry_module, tmp_path):
    """自由流程没有全仓阶段枚举，未执行的选择不能冒充研究完成。"""
    from ai4e_core.run.session import run_recipe

    cfg = entry_module.load_configuration(
        RECIPE / "config.yaml",
        [
            "pipeline.stages=[typo]",
            f"run_root={tmp_path / 'runs'}",
            f"data_root={tmp_path / 'data'}",
        ],
    )
    assert run_recipe(cfg, stages=entry_module.pipeline, script=RECIPE / "pipeline.py") == 0
    summary = json.loads(next((tmp_path / "runs").glob("*/summary.json")).read_text())
    assert summary["research_status"] == "incomplete"
    assert summary["unverified_stages"] == ["typo"]


def test_task_new_and_post_capture_does_not_require_training_inputs(tmp_path):
    project = tmp_path / "project"
    task.create_project(project)
    cfg = OmegaConf.to_container(OmegaConf.load(RECIPE / "config.yaml"), resolve=True)
    cfg["inputs"]["rawprep"]["source"] = str(tmp_path / "unavailable-raw")
    cfg["inputs"]["infer"]["solver_assets"] = str(tmp_path / "unavailable-solver")
    results = tmp_path / "results.json"
    results.write_text("{}")
    cfg["inputs"]["post"]["results"] = str(results)
    current = task.new_task(project, "control", source=RECIPE, configuration=cfg)
    run = task.submit_run(project, current["id"], overrides=["pipeline.stages=[post]"], start=False)
    request = json.loads((project / run["request_path"]).read_text())
    assert set(request["context"]["assets"]) == {"inputs.post.results"}
    captured = OmegaConf.load(project / run["code_path"] / "config.yaml")
    assert captured.pipeline.stages == ["post"]
    assert Path(captured.data_root) == project / run["data_path"]
    assert Path(captured.run_root) == (project / run["run_path"]).parent
    assert run["version_id"] == current["version_id"]
    assert len(task.get_lineage(project)) == 1
