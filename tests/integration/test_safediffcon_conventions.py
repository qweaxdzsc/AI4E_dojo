"""控制公共配置、旧产物兼容和自包含案例入口。"""

from copy import deepcopy
from pathlib import Path

import pytest
import yaml

from ai4e_contrib.application.pde_control.safediffcon.configuration import (
    application_parameters,
    load_configuration,
    validate,
)
from ai4e_contrib.application.pde_control.safediffcon.migration import migrate_legacy

ROOT = Path(__file__).resolve().parents[2]
RECIPE = ROOT / "recipes/safediffcon"


@pytest.mark.parametrize("case", ["burgers", "tokamak"])
def test_self_contained_examples(case, tmp_path):
    """案例复制后包含可编辑正文，Task不需要额外入口描述。"""
    import shutil

    from ai4e_task.templates.materialize import read_entry

    destination = tmp_path / case
    shutil.copytree(ROOT / "examples/safediffcon" / case, destination)
    for name in (
        "pipeline",
        "configuration",
        "rawprep",
        "trainprep",
        "train",
        "posttrain",
        "infer",
        "post",
    ):
        assert (destination / f"{name}.py").is_file()
    assert not (destination / "task-entry.json").exists()
    assert read_entry(destination)["script"] == "pipeline.py"
    cfg = load_configuration(destination / "config.yaml")
    assert cfg["case"] == case
    assert cfg == load_configuration(destination / "quick.yaml")


def test_legacy_paths_and_frozen_production(tmp_path):
    """转换只创建配置值，旧准备及权重内容不参与改写。"""
    cfg = load_configuration(RECIPE / "config.yaml")
    old = application_parameters(cfg)
    old["data"].update(
        root="raw",
        output="data",
        physical=None,
        prepared={s: f"prepared/{s}/manifest.json" for s in ("train", "cal", "test")},
    )
    old["solver"].update(python="env/bin/python", assets="kstar")
    old["train"]["resume"] = "weights.pt"
    old["pipeline"]["stages"] = ["pipeline"]
    before = deepcopy(old)
    result = migrate_legacy(old, base=tmp_path)
    assert old == before
    assert result["inputs"]["infer"]["solver_assets"] == str(tmp_path / "kstar")
    assert result["inputs"]["train"]["resume"] == str(tmp_path / "weights.pt")
    assert result["inputs"]["posttrain"]["preparation_train"] == str(
        tmp_path / "prepared/train/manifest.json"
    )
    assert result["solver"]["python"] == str(tmp_path / "env/bin/python")
    assert migrate_legacy(result, base=tmp_path) == result


@pytest.mark.parametrize(
    "override", ["data.output=foo", "train.resume=foo", "post.results=foo", "solver.assets=foo"]
)
def test_old_keys_rejected_from_files_overrides_and_program(tmp_path, override):
    """程序/文件/覆盖一律拒绝旧键，包括新旧同时存在。"""
    from omegaconf import OmegaConf

    cfg = OmegaConf.merge(
        OmegaConf.load(RECIPE / "config.yaml"), OmegaConf.from_dotlist([override])
    )
    file = tmp_path / "bad.yaml"
    OmegaConf.save(cfg, file)
    with pytest.raises(ValueError, match="旧配置键"):
        load_configuration(file)
    with pytest.raises(ValueError, match="旧配置键"):
        load_configuration(RECIPE / "config.yaml", [override])
    with pytest.raises(ValueError, match="旧配置键"):
        validate(OmegaConf.to_container(cfg))


def test_partial_public_solver_migration_and_conflict(tmp_path):
    """上一版公共配置也可显式迁移，但不猜测冲突的两个资源路径。"""
    cfg = yaml.safe_load((RECIPE / "config.yaml").read_text())
    cfg["inputs"]["infer"].pop("solver_assets")
    cfg["solver"]["assets"] = "models"
    result = migrate_legacy(cfg, base=tmp_path)
    assert result["inputs"]["infer"]["solver_assets"] == str(tmp_path / "models")
    cfg["inputs"]["infer"]["solver_assets"] = "other"
    with pytest.raises(ValueError, match="新旧键混用"):
        migrate_legacy(cfg, base=tmp_path)


def test_solver_resources_captured_only_for_inference(tmp_path):
    """推理捕获模型资源；固定结果post不要求求解器资源可用。"""
    import json

    import ai4e_task as task

    project = tmp_path / "project"
    task.create_project(project)
    cfg = load_configuration(RECIPE / "config.yaml")
    assets = tmp_path / "models"
    assets.mkdir()
    (assets / "weights").write_bytes(b"fixed")
    cfg["inputs"]["infer"]["solver_assets"] = str(assets)
    cfg["pipeline"]["stages"] = ["infer"]
    item = task.new_task(project, "capture", source=RECIPE, configuration=cfg)
    run = task.submit_run(project, item["id"], start=False)
    request = json.loads((project / run["request_path"]).read_text())
    assert "inputs.infer.solver_assets" in request["context"]["assets"]


def test_public_and_domain_trees_do_not_alias():
    """调用参数变化不能污染保存的用户树或产生旧公开键。"""
    cfg = load_configuration(RECIPE / "config.yaml")
    before = deepcopy(cfg)
    domain = application_parameters(cfg, stage="infer")
    domain["solver"]["assets"] = "different"
    domain["posttrain"]["checkpoint"] = "different"
    assert cfg == before
    assert "data" not in cfg and "assets" not in cfg["solver"]


def test_solver_interpreter_keeps_virtual_environment_symlink(tmp_path):
    """解释器路径是环境身份，不能解析为没有求解依赖的基础Python。"""
    base = tmp_path / "base-python"
    base.write_text("binary")
    executable = tmp_path / "venv/bin/python"
    executable.parent.mkdir(parents=True)
    executable.symlink_to(base)
    cfg = yaml.safe_load((RECIPE / "config.yaml").read_text())
    cfg["solver"]["python"] = "venv/bin/python"
    source = tmp_path / "config.yaml"
    source.write_text(yaml.safe_dump(cfg))
    assert load_configuration(source)["solver"]["python"] == str(executable)
    assert migrate_legacy(cfg, base=tmp_path)["solver"]["python"] == str(executable)


def test_derived_energy_layout_is_stable(tmp_path):
    """派生扩展示例固定归约布局，读回不能因非连续轴改变舍入顺序。"""
    import numpy as np

    from tools.verification.safediffcon.public_conventions import EXTENSION

    namespace = {}
    exec(EXTENSION, namespace)  # noqa: S102 - 仅执行仓库维护的固定扩展测试正文
    values = np.random.default_rng(42).normal(size=(2, 122, 8))[:, :, [1, 4, 6]].transpose(0, 2, 1)
    before = namespace["energy"](values, case="tokamak")["energy"]["values"]
    np.save(tmp_path / "response.npy", values)
    after = namespace["energy"](np.load(tmp_path / "response.npy"), case="tokamak")["energy"][
        "values"
    ]
    np.testing.assert_array_equal(before, after)


@pytest.mark.parametrize("change", ["prediction", "target", "ids", "statistic"])
def test_control_metric_comparability_and_array_tampering(tmp_path, change):
    """固定真值的不同预测可比；样本/真值/归约变化不可比，数组篡改失效。"""
    import json

    import ai4e_task as task
    import numpy as np

    from ai4e_contrib.ability.eval.safediffcon.control import metrics
    from ai4e_contrib.application.pde_control.safediffcon.handoff import register_metrics
    from ai4e_core.abilities.data.save.array_manifest import save_arrays
    from ai4e_core.run.writer import RunWriter

    project = tmp_path / "project"
    task.create_project(project)
    runs = []
    for side in range(2):
        arrays = {
            "ids": np.arange(2),
            "target": np.zeros((2, 11, 128)),
            "paper_target": np.zeros((2, 11, 128)),
            "response": np.ones((2, 11, 128)),
        }
        if side and change != "statistic":
            arrays["response" if change == "prediction" else change] += 1
        reference = Path(
            save_arrays(
                tmp_path / str(side),
                arrays,
                kind="control_results_v1",
                metadata={"case": "burgers"},
            )
        )
        writer = RunWriter.create(tmp_path / "runs")
        register_metrics(
            writer,
            reference,
            metrics(arrays["response"], arrays["target"], case="burgers"),
            evaluate=metrics,
        )
        if side and change == "statistic":
            item = json.loads((writer.run_dir / "artifacts/metrics.json").read_text())["items"][
                "post/J"
            ]
            semantics = {**item["semantics"], "statistic": "sum_instead_of_mean"}
            writer.record_metric(
                "J", item["value"], stage="post", assets=item["assets"], semantics=semantics
            )
        writer.write_summary({"failed": False})
        runs.append(task.import_run(project, writer.run_dir)["id"])
    compared = task.compare_runs(project, *runs)["metrics"]["post/J"]
    assert compared["status"] == ("available" if change == "prediction" else "incompatible")
    reference.with_name("response.npy").write_bytes(b"changed")
    assert task.compare_runs(project, *runs)["metrics"]["post/J"]["status"] == "missing"
