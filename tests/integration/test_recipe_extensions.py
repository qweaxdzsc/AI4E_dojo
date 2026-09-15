"""仓库外复制案例真实扩展：字段落盘、训练消费、在线采样与配置错误。"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import torch
import yaml

from tests.integration.test_dataset_recipe import setup_case

ROOT = Path(__file__).resolve().parents[2]


def extension_case(tmp_path, name):
    """真实网格与完整扩展示例组合，仅缩小网络和样本预算。"""
    folder, _ = setup_case(tmp_path)
    original = yaml.safe_load((folder / "config.yaml").read_text())
    shutil.copytree(ROOT / "examples/recipe_extensions" / name, folder, dirs_exist_ok=True)
    config = yaml.safe_load((folder / "config.yaml").read_text())
    for key in ("dataset", "data_root", "run_root"):
        config[key] = original[key]
    config["pipeline"]["stages"] = ["rawprep", "trainprep", "train"]
    config["model"]["parameters"].update(
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
    )
    sampling = config["model"]["sampling"]
    sampling["supernodes"]["num_points"] = 2
    sampling["domains"]["surface"]["anchor"]["num_points"] = 2
    sampling["domains"]["volume"]["anchor"]["num_points"] = 1
    config["train"].update(
        max_epochs=2,
        device="cpu",
        optimizer="adamw",
        scheduler="constant",
        test_repeat=1,
        snapshot=False,
    )
    # 此夹具外侧四点到表面的距离全为 1，不能对常量拟合 zscore。
    config["trainprep"]["normalization"]["fields"]["volume_sdf"] = {"method": "identity"}
    config["post"].update(evaluate=True, save_predictions=True, export_vtk=False)
    (folder / "config.yaml").write_text(yaml.safe_dump(config, sort_keys=False))
    return folder, config


def script(folder, entry="pipeline.py", *extra):
    """独立解释器保证读取复制目录的本地参数声明，跨目录启动。"""
    return subprocess.run(
        [sys.executable, "-B", str(folder / entry), *extra],
        cwd=folder.parent,
        env={**os.environ, "OMP_NUM_THREADS": "1", "VECLIB_MAXIMUM_THREADS": "1"},
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )


@pytest.mark.parametrize("format", ["pt", "zarr"])
def test_field_extension_saved_normalized_and_trained(tmp_path, format):
    folder, cfg = extension_case(tmp_path, "field_mapping")
    result = script(folder, "pipeline.py", "--set", f"rawprep.format={format}")
    assert result.returncode == 0, result.stdout + result.stderr
    from ai4e_core.abilities.data.source.manifest import ManifestIndex

    index = ManifestIndex(tmp_path / "data/manifest.json")
    fields = index.read("train")
    torch.testing.assert_close(
        fields["volume_speed"], torch.linalg.vector_norm(fields["volume_velocity"], dim=-1)
    )
    manifest = index.manifest
    assert manifest["extensions"][0]["outputs"]["speed"]["state"] == "physical"
    assert (
        yaml.safe_load((tmp_path / "data/train/statistics.yaml").read_text())["volume_speed_count"]
        > 0
    )
    directory = next((tmp_path / "records").iterdir())
    prepared = json.loads((directory / "artifacts/preparation.json").read_text())
    assert "volume_speed" in prepared["normalization"]["fields"]
    checkpoint = torch.load(directory / "checkpoints/last.pt", weights_only=False)
    assert checkpoint["updates"] == 2
    assert prepared["declarations"]["trainprep"]["domains"]["volume"]["features"] == {
        "speed": "volume_speed"
    }
    assert checkpoint["model"]["feature_projections.volume.0.weight"].shape[1] == 1
    # 从真实准备重建输入，断言新字段进入模型特征且影响同权重前向。
    check = folder / "check_features.py"
    check.write_text("""from configuration import load_configuration, application_parameters, load_components
from ai4e_core.applications.aero_cfd.trainprep.preparation import consume
from ai4e_core.applications.aero_cfd.trainprep.dataset import iter_partition_batches
import torch, sys
cfg = load_configuration(__file__.replace("check_features.py", "config.yaml"))
config = application_parameters(cfg)
component = load_components(cfg).model
data = consume(config, sys.argv[1], prepare=component.prepare_inputs, collate=component.collate)
batch = next(iter_partition_batches(data.index, "train", prepare=data.prepare, collate=data.collate, normalization=data.normalization, physical_prepare=data.physical_prepare, normalized_input=False, sampling=config["sampling"], config=config, batch_size=1, device=torch.device("cpu"), evaluation=True))
features = batch["inputs"]["domain_anchor_features"]["volume"]
assert features.shape[-1] == 1 and features.abs().sum() > 0
model = component.construct(**config["model"]["parameters"], data_specs=config["model"]["data_specs"]).eval()
model.load_state_dict(torch.load(sys.argv[2], weights_only=False)["model"])
with torch.no_grad():
    before = component.predict(model, batch["inputs"])
    batch["inputs"]["domain_anchor_features"]["volume"] = features + 2
    after = component.predict(model, batch["inputs"])
assert not torch.equal(before["volume_velocity"], after["volume_velocity"])
""")
    check_result = script(
        folder,
        "check_features.py",
        str(directory / "artifacts/preparation.json"),
        str(directory / "checkpoints/last.pt"),
    )
    assert check_result.returncode == 0, check_result.stderr
    snapshot = yaml.safe_load((directory / "inputs/config.yaml").read_text())
    assert snapshot["rawprep"]["speed"] == cfg["rawprep"]["speed"]
    cfg["post"]["checkpoint"] = str(directory / "checkpoints/last.pt")
    cfg["post"]["query"] = False
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder, "post.py")
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("injection", ["target", "direct"])
def test_sampling_runs_during_each_training_epoch(tmp_path, injection):
    folder, cfg = extension_case(tmp_path, "sampling")
    cfg["pipeline"]["stages"].append("post")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    path = folder / "custom_abilities.py"
    source = path.read_text().replace(
        "count = len(",
        'with open(__file__ + ".calls", "a") as stream:\n        stream.write(str(kwargs.get("epoch")) + ":" + str(kwargs.get("evaluation")) + "\\n")\n    count = len(',
    )
    path.write_text(source)
    if injection == "direct":
        cfg["model"]["sampling"].pop("target")
        cfg["model"]["sampling"].pop("parameters")
        (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        stage = folder / "trainprep.py"
        stage.write_text(
            "from custom_abilities import reverse_geometry\n"
            + stage.read_text().replace(
                "data, settings=cfg.model.sampling, model_component=components.model",
                "data, settings=cfg.model.sampling, model_component=components.model, operation=reverse_geometry",
            )
        )
    result = script(folder)
    assert result.returncode == 0, result.stdout + result.stderr
    calls = Path(str(path) + ".calls").read_text().splitlines()
    assert "0:False" in calls and "1:False" in calls, calls
    directory = next((tmp_path / "records").iterdir())
    record = json.loads((directory / "artifacts/preparation.json").read_text())
    assert record["components"]["prepare"]["name"] == "custom_abilities.reverse_geometry"
    cfg["train"]["preparation"] = str(directory / "artifacts/preparation.json")
    path.write_text(source + "\n# implementation changed\n")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder, "train.py")
    assert result.returncode != 0
    assert "变化" in result.stderr


def test_extension_parameters_and_bad_output_fail_before_publish(tmp_path):
    folder, _cfg = extension_case(tmp_path, "field_mapping")
    result = script(folder, "rawprep.py", "--set", "rawprep.speed.unexpected=1")
    assert result.returncode != 0 and "rawprep.speed" in result.stderr
    assert not (tmp_path / "data/manifest.json").exists()
    ability = folder / "custom_abilities.py"
    ability.write_text(
        ability.read_text().replace(
            "np.linalg.norm(velocity, axis=-1, keepdims=True)",
            "np.linalg.norm(velocity, axis=-1, keepdims=True)[:-1]",
        )
    )
    result = script(folder, "rawprep.py")
    assert result.returncode != 0 and "输出形状" in result.stderr
    assert not (tmp_path / "data/manifest.json").exists()


def test_transform_objective_metric_prediction_replacements(tmp_path):
    """四类接口分别改变真实训练目标、评价结果和保存的物理预测。"""
    folder, cfg = extension_case(tmp_path, "sampling")
    ability = folder / "custom_abilities.py"
    ability.write_text(
        ability.read_text()
        + """
from ai4e_contrib.ability.model.abupt.component import predict

class Scale:
    def __init__(self, factor=2.0):
        self.factor = factor
    def apply(self, value):
        return value * self.factor
    def inverse(self, value):
        return value / self.factor

def zero_objective(model, batch, config):
    values = predict(model, batch["inputs"])
    loss = sum(value.square().mean() for value in values.values()) * 0
    return {"loss": loss, "losses": {"custom": loss}}

def count_metric(model, batches, config, normalization):
    count = sum(1 for batch in batches if predict(model, batch["inputs"]))
    return {"loss": 7.0, "metrics": {"custom_count": count}}

def constant_prediction(model, inputs):
    return {key: value * 0 + 2 for key, value in predict(model, inputs).items()}
"""
    )
    cfg["model"]["objective"] = {"target": "custom_abilities.zero_objective", "parameters": {}}
    cfg["train"]["metric"] = {"target": "custom_abilities.count_metric", "parameters": {}}
    cfg["trainprep"]["normalization"]["fields"]["surface_pressure"] = {
        "method": "custom",
        "target": "custom_abilities.Scale",
        "parameters": {"factor": 2.0},
    }
    cfg["post"].update(query=False, evaluate=False)
    cfg["post"]["prediction"] = {"target": "custom_abilities.constant_prediction", "parameters": {}}
    cfg["pipeline"]["stages"].append("post")
    (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder)
    assert result.returncode == 0, result.stdout + result.stderr
    directory = next((tmp_path / "records").iterdir())
    summary = json.loads((directory / "summary.json").read_text())
    history = summary["reports"]["train"]["history"]
    assert all(row["loss"] == 0 for row in history)
    assert history[0]["evaluation"]["metrics"]["custom_count"] == 1
    assert history[0]["evaluation"]["loss"] == 7
    protocol = json.loads((directory / "artifacts/comparison-protocol.json").read_text())
    assert protocol["extensions"]["prediction"]["name"].endswith("constant_prediction")
    assert list((directory / "sources").glob("*.py"))
    predictions = list((tmp_path / "data/predictions").rglob("*.pt"))
    assert predictions
    payload = torch.load(tmp_path / "data/predictions/b/surface_pressure.pt", weights_only=True)
    torch.testing.assert_close(payload, torch.ones_like(payload))


def test_callable_reconstruction_and_custom_transform_contract():
    """普通函数/对象共用解析，冻结重建拒绝变形与无效参数。"""
    from ai4e_core.abilities.transform.normalization import Normalization
    from ai4e_core.base.config.steps import operation_record, resolve_operation, restore_operation

    operation = resolve_operation(operation=_scale_factory, selection={"parameters": {"factor": 3}})
    restored = restore_operation(operation_record(operation))
    value = torch.arange(6).reshape(3, 2).float()
    torch.testing.assert_close(restored().inverse(restored().apply(value)), value)
    target = __name__ + "._scale_factory"
    normalization = Normalization(
        {
            "version": 2,
            "fields": {
                "field": {"method": "custom", "target": target, "parameters": {"factor": 3}}
            },
        }
    )
    torch.testing.assert_close(
        normalization.inverse("field", normalization.apply({"field": value})["field"]), value
    )
    with pytest.raises(ValueError, match="签名"):
        resolve_operation({"target": target, "parameters": {"typo": 1}})
    normalization.transforms["field"].transform = _MalformedTransform()
    with pytest.raises(ValueError, match="形状"):
        normalization.apply({"field": value})


def test_task_fork_preserves_local_extension(tmp_path):
    """本地扩展参数与真实能力脚本随任务复制，编辑不创建版本。"""
    import ai4e_task as task

    folder, config = extension_case(tmp_path / "source", "field_mapping")
    project = tmp_path / "project"
    task.create_project(project)
    first = task.new_task(project, "field", source=folder)
    current = task.read_configuration(project, first["id"])
    updated = task.save_configuration(
        project, first["id"], {"train": {"learning_rate": 1e-4}}, revision=current["revision"]
    )
    assert updated["config"]["rawprep"]["speed"] == config["rawprep"]["speed"]
    second = task.fork_task(project, first["id"])
    assert (
        task.read_configuration(project, second["id"])["config"]["rawprep"]["speed"]
        == config["rawprep"]["speed"]
    )
    assert len(task.get_lineage(project)) == 2


def test_extension_comparison_is_scoped():
    """预测扩展影响推理比较，学习目标扩展影响训练比较。"""
    from copy import deepcopy

    from tests.integration.test_comparison_protocol import protocol
    from tools.verification.comparison_protocol import assess

    left, right = protocol(), protocol()
    left["extensions"] = {"prediction": {"name": "custom.predict", "sha256": "changed"}}
    assert assess(left, right, "inference")["status"] == "not_comparable"
    assert assess(left, right, "training")["status"] == "comparable"
    right = deepcopy(left)
    right["extensions"]["objective"] = {"name": "custom.loss", "sha256": "changed"}
    assert assess(left, right, "training")["status"] == "not_comparable"


class _Scale:
    def __init__(self, factor):
        self.factor = factor

    def apply(self, value):
        return value * self.factor

    def inverse(self, value):
        return value / self.factor


def _scale_factory(factor=2):
    return _Scale(factor)


class _MalformedTransform:
    def apply(self, value):
        return value[:-1]

    def inverse(self, value):
        return value


@pytest.mark.parametrize("change", ["remove_step", "identity", "state"])
def test_field_step_removal_and_invalid_identity_state(tmp_path, change):
    """步骤删除不再计算；跨实体输出与错误物理状态不能发布清单。"""
    import ast

    folder, cfg = extension_case(tmp_path, "field_mapping")
    if change == "remove_step":
        path = folder / "rawprep.py"
        lines = path.read_text().splitlines(keepends=True)
        for node in ast.walk(ast.parse("".join(lines))):
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Attribute)
                and node.value.func.attr == "map_fields"
            ):
                del lines[node.lineno - 1 : node.end_lineno]
                break
        path.write_text("".join(lines))
    else:
        output = cfg["rawprep"]["speed"]["outputs"]["speed"]
        output["entity_like" if change == "identity" else "state"] = (
            "surface.pressure" if change == "identity" else "normalized"
        )
        (folder / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    result = script(folder, "rawprep.py")
    assert result.returncode != 0
    assert not (tmp_path / "data/manifest.json").exists()
    assert any(value in result.stderr for value in ["volume_speed", "实体身份", "physical"])
