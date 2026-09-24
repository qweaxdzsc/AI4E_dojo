"""经典案例配置、公开准备入口、实际预测与固定结果消费；不执行训练。"""

import json
import os
import shutil
import subprocess
from functools import partial
from pathlib import Path

import numpy as np
import pytest
import torch
import yaml
from omegaconf import OmegaConf
from scipy.io import savemat
from torch import nn

from ai4e_contrib.application.classic_networks import binding, configuration, prediction
from ai4e_contrib.application.classic_networks.preparation import read_prepared
from ai4e_core import run
from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays, save_arrays
from ai4e_core.abilities.geometry import mesh_graph
from ai4e_core.abilities.modeling.models.rnn import RNN

ROOT = Path(__file__).resolve().parents[2]


def case_configuration(case="darcy"):
    """直接读取交付中的真实配置正文，避免测试维护另一份默认配置。"""
    return yaml.safe_load((ROOT / "recipes/classic_networks" / case / "config.yaml").read_text())


def test_omegaconf_validation_returns_resolved_plain_containers():
    raw = case_configuration()
    raw["train"]["checkpoint_every"] = "${train.updates}"
    cfg = OmegaConf.create(raw)
    validated = configuration.validate(cfg)
    assert type(validated) is dict
    assert type(validated["dataset"]) is dict
    assert type(validated["model"]["parameters"]["hidden_features"]) is list
    assert validated["train"]["checkpoint_every"] == 100
    assert json.loads(json.dumps(validated)) == validated
    validated["dataset"]["train_count"] = 1
    assert cfg.dataset.train_count == 32


@pytest.mark.parametrize(
    "section,key,value",
    [
        ("dataset", "train_count", 0),
        ("train", "updates", True),
        ("train", "updates", 0),
        ("train", "batch_size", 2),
        ("train", "seconds", 10801),
        ("train", "lr", -1),
        ("components", "model", None),
        ("model", "family", "unknown"),
    ],
)
def test_invalid_configuration_rejects_instead_of_falling_back(section, key, value):
    cfg = case_configuration()
    cfg[section][key] = value
    with pytest.raises((ValueError, TypeError)):
        configuration.validate(cfg)


@pytest.mark.parametrize("rate", [float("nan"), float("inf")])
def test_configuration_rejects_nonfinite_learning_rate(rate):
    cfg = case_configuration()
    cfg["train"]["lr"] = rate
    with pytest.raises(ValueError):
        configuration.validate(cfg)


@pytest.mark.parametrize("points", [0, -1])
def test_configuration_rejects_nonpositive_sample_points(points):
    cfg = case_configuration("double_cylinder")
    cfg["train"]["sample_points"] = points
    with pytest.raises(ValueError):
        configuration.validate(cfg)


@pytest.mark.parametrize(
    "section,key", [("dataset", "case"), ("train", "updates"), ("model", "family")]
)
def test_missing_configuration_is_not_defaulted(section, key):
    cfg = case_configuration()
    del cfg[section][key]
    with pytest.raises((KeyError, ValueError)):
        configuration.validate(cfg)


def test_static_points_cannot_be_declared_as_rnn_time():
    cfg = case_configuration()
    cfg["model"]["family"] = "rnn"
    with pytest.raises(ValueError, match="时间"):
        configuration.validate(cfg)
    assert configuration.component(None) is None
    assert configuration.component("torch.nn.Identity") is nn.Identity


def sequence_arrays():
    """用真实轴含义编码点和时间；每个时间层相差1000，通道仍各自可区分。"""
    field = np.arange(2 * 3 * 4, dtype=np.float32).reshape(2, 3, 4)
    history = np.stack([field + index * 1000 for index in range(3)])[None]
    return {
        "input": history,
        "physical_input": history.copy(),
        "target": (field + 3000)[None],
        "valid": np.ones((1, 2, 3), dtype=bool),
    }


def test_rnn_batch_uses_time_axis_and_preserves_point_selection():
    arrays = sequence_arrays()
    item = binding.batch(arrays, [0], device="cpu", case="double_cylinder")
    assert item["input"].shape == (6, 3, 4)
    for point in range(6):
        row, column = divmod(point, 3)
        np.testing.assert_array_equal(item["input"][point], arrays["input"][0, :, row, column])
    torch.testing.assert_close(item["target"] - item["input"][:, -1], torch.full((6, 4), 1000.0))
    torch.manual_seed(7)
    subset = binding.batch(arrays, [0], device="cpu", case="double_cylinder", sample_points=3)
    assert subset["input"].shape == (3, 3, 4)
    torch.testing.assert_close(
        subset["target"] - subset["input"][:, -1], torch.full((3, 4), 1000.0)
    )
    model = binding.FieldModel(RNN(4, 4, hidden_size=5), "rnn", 2)
    actual = model(item["input"], item["valid"])
    torch.testing.assert_close(actual, model.network(item["input"])[0][:, -1])
    assert torch.isfinite(binding.objective(model, item))


class LastGridFrame(nn.Module):
    """复制用户组件的最小网格时序接口，不将空间轴重排成RNN点批。"""

    def forward(self, history):
        return history[:, -1] + 1000


def test_custom_sequence_layout_is_not_forced_to_point_sequence():
    arrays = sequence_arrays()
    item = binding.batch(arrays, [0], device="cpu", case="double_cylinder", point_sequence=False)
    assert item["input"].shape == (1, 3, 2, 3, 4)
    model = binding.FieldModel(LastGridFrame(), "custom", 2)
    torch.testing.assert_close(model(item["input"]), item["target"])
    assert binding.objective(model, item).item() == 0


class CaptureGraph(nn.Module):
    """观察图连接输入并返回节点首通道，不替换公共图构造计算。"""

    def forward(self, nodes, features, edges):
        self.observed = nodes, features, edges
        return nodes[:, :1]


def test_graph_handoff_reuses_sender_minus_receiver_features(monkeypatch):
    calls = []
    original = mesh_graph.edge_features

    def observed(positions, edges):
        calls.append((positions.clone(), edges.clone()))
        return original(positions, edges)

    monkeypatch.setattr(mesh_graph, "edge_features", observed)
    network = CaptureGraph()
    model = binding.FieldModel(network, "gnn", 2)
    values = torch.arange(1, 13, dtype=torch.float32).reshape(1, 2, 3, 2)
    coords = torch.tensor(
        [[[[0.0, 0.0], [2.0, 0.0], [4.0, 0.0]], [[0.0, 3.0], [2.0, 3.0], [4.0, 3.0]]]]
    )
    valid = torch.tensor([[[True, True, False], [True, False, True]]])
    result = model(values, valid, coords)
    assert len(calls) == 1
    nodes, features, edges = network.observed
    expected_positions = coords.reshape(-1, 2)[[0, 1, 3, 5]]
    np.testing.assert_array_equal(calls[0][0], expected_positions)
    assert {tuple(pair) for pair in edges.T.tolist()} == {(0, 1), (1, 0), (0, 2), (2, 0)}
    delta = expected_positions[edges[0]] - expected_positions[edges[1]]
    torch.testing.assert_close(features[:, :2], delta)
    torch.testing.assert_close(features[:, 2], torch.linalg.vector_norm(delta, dim=1))
    torch.testing.assert_close(result[valid], values[..., :1][valid])
    assert torch.count_nonzero(result[~valid]) == 0
    assert nodes.shape == (4, 2)  # 孤立有效点仍存在，不能因为没有边被删除。


def fixed_fixture():
    x = np.arange(2 * 2 * 3 * 3, dtype=np.float32).reshape(2, 2, 3, 3) / 10
    physical = (2 * x[..., 0] - 3 * x[..., 1] + 0.5 * x[..., 2] + 0.25)[..., None] * 2 + 10
    valid = np.ones((2, 2, 3), bool)
    valid[:, 0, 2] = False
    target = physical + 1
    target[~valid] = 0
    arrays = {
        "input": x,
        "physical_input": x.copy(),
        "target": (target - 10) / 2,
        "physical_target": target,
        "valid": valid,
        "entity_ids": np.broadcast_to(np.arange(6).reshape(2, 3), valid.shape),
    }
    record = {
        "metadata": {
            "case": "darcy",
            "ids": ["a", "b"],
            "fields": ["solution"],
            "units": ["benchmark"],
            "statistics": {"target": {"mean": [10.0], "scale": [2.0]}},
        }
    }
    return arrays, record, physical


def test_fixed_prediction_derived_save_readback_and_independent_post(tmp_path):
    arrays, record, expected = fixed_fixture()
    network = nn.Linear(3, 1)
    with torch.no_grad():
        network.weight.copy_(torch.tensor([[2.0, -3.0, 0.5]]))
        network.bias.fill_(0.25)
    model = binding.FieldModel(network, "mlp", 2)
    model.train()
    get_batch = partial(binding.batch, arrays, device="cpu", case="darcy")

    def derive(payload, metadata):
        assert metadata["fields"] == ["solution"]
        return {"signed_error": payload["prediction"] - payload["target"]}, {
            "signed_error": {"units": "benchmark", "identity": "entity_ids"}
        }

    fixed = prediction.predict_fields(
        model, arrays, record, get_batch, tmp_path / "fixed", derived=derive
    )
    assert model.training  # 原推理保护层须恢复调用者模式。
    saved_record, saved = read_arrays(fixed, kind="classic-results-v1")
    np.testing.assert_allclose(
        saved["prediction"][arrays["valid"]], expected[arrays["valid"]], atol=2e-6
    )
    np.testing.assert_array_equal(saved["prediction"][~arrays["valid"]], 0)
    np.testing.assert_array_equal(saved["entity_ids"], arrays["entity_ids"])
    assert saved_record["metadata"]["derived"]["signed_error"]["identity"] == "entity_ids"
    moved = tmp_path / "copied"
    shutil.copytree(Path(fixed).parent, moved)
    Path(fixed).parent.rename(tmp_path / "old-fixed-hidden")

    def forbidden(*args, **kwargs):
        raise AssertionError("固定后处理不得重新运行网络")

    model.forward = forbidden
    report = prediction.evaluate(
        moved / "manifest.json",
        tmp_path / "post",
        consume=lambda values, declarations: {
            "signed_error_mean": float(values["signed_error"][values["valid"]].mean())
        },
    )
    assert report["mse"] == pytest.approx(1, abs=3e-6)
    assert report["derived"]["signed_error_mean"] == pytest.approx(-1, abs=2e-6)
    assert [row["valid_count"] for row in report["rows"]] == [5, 5]
    assert json.loads((tmp_path / "post/metrics.json").read_text())["rows"] == report["rows"]


def test_derived_field_cannot_overwrite_fixed_prediction(tmp_path):
    arrays, record, _ = fixed_fixture()
    with pytest.raises(ValueError, match="覆盖"):
        prediction.predict_fields(
            binding.FieldModel(nn.Linear(3, 1), "mlp", 2),
            arrays,
            record,
            partial(binding.batch, arrays, device="cpu", case="darcy"),
            tmp_path / "invalid",
            derived=lambda payload, metadata: (
                {"prediction": payload["prediction"]},
                {"prediction": {}},
            ),
        )


def test_copied_recipe_launch_rawprep_trainprep_serializes_plain_config(tmp_path):
    case = tmp_path / "copied-case"
    shutil.copytree(ROOT / "recipes/classic_networks/darcy", case)
    source = case / "source"
    source.mkdir()
    row, column = np.meshgrid(np.arange(9), np.arange(9), indexing="ij")
    for suffix, shift in (("smooth1", 0), ("smooth2", 100)):
        savemat(
            source / f"piececonst_r421_N1024_{suffix}.mat",
            {
                "coeff": np.stack([row + column + 1 + shift, row + 2 * column + 3 + shift]),
                "sol": np.stack([3 * row - column + 1 + shift, row + column + 10 + shift]),
            },
        )
    cfg = case_configuration()
    cfg["pipeline"]["stages"] = ["rawprep", "trainprep"]
    cfg["inputs"]["rawprep"]["source"] = "./source"
    cfg["dataset"].update(train_count=2, test_count=1, stride=2)
    cfg["run_root"], cfg["data_root"] = "../outputs/runs", "../outputs/data"
    (case / "config.yaml").write_text(yaml.safe_dump(cfg))
    # 从案例外执行实际 launch，覆盖路径解析、OmegaConf 与两次真实阶段交接。
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            str(case / "pipeline.py"),
            "--config",
            str(case / "config.yaml"),
        ],
        cwd=ROOT,
        env=dict(os.environ),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    manifests = [
        path
        for path in (tmp_path / "outputs/data").rglob("manifest.json")
        if json.loads(path.read_text()).get("kind") == "classic-preparation-v1"
    ]
    assert len(manifests) == 1
    record, train = read_prepared(manifests[0], "train")
    assert train["input"].shape == (2, 5, 5, 3)
    assert record["metadata"]["statistics"]["fit_ids"] == ["train_0000", "train_0001"]
    frozen = json.loads(manifests[0].read_text())
    assert frozen["dataset"]["stride"] == 2
    assert not list((tmp_path / "outputs").rglob("checkpoints/*.pt"))


def test_copied_post_launch_records_each_physical_field_semantics(tmp_path):
    case = tmp_path / "copied-case"
    shutil.copytree(ROOT / "recipes/classic_networks/shapenet_volume", case)
    valid = np.ones((2, 2, 3), dtype=bool)
    valid[0, 0, 2] = False
    valid[1, 0, :] = False
    target = np.ones((2, 2, 3, 3), dtype=np.float32)
    errors = np.asarray([[1, 2, 3], [3, 4, 5]], dtype=np.float32)[:, None, None, :]
    predicted = target + errors
    predicted[~valid] = 10000  # 无效域不能进入物理指标。
    fields = ["velocity_x", "velocity_y", "velocity_z"]
    fixed = save_arrays(
        tmp_path / "fixed",
        {"prediction": predicted, "target": target, "valid": valid},
        kind="classic-results-v1",
        metadata={
            "case": "shapenet_volume",
            "ids": ["a", "b"],
            "fields": fields,
            "units": ["m/s"] * 3,
            "derived": {},
        },
    )
    cfg = case_configuration("shapenet_volume")
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["post"]["results"] = fixed
    cfg["run_root"], cfg["data_root"] = "../outputs/runs", "../outputs/data"
    (case / "config.yaml").write_text(yaml.safe_dump(cfg))
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-sync",
            "python",
            str(case / "post.py"),
            "--config",
            str(case / "config.yaml"),
        ],
        cwd=ROOT,
        env=dict(os.environ),
        capture_output=True,
        text=True,
        timeout=90,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    indexes = list((tmp_path / "outputs/runs").glob("*/artifacts/metrics.json"))
    assert len(indexes) == 1
    items = json.loads(indexes[0].read_text())["items"]
    assert set(items) == {f"post/mse_{field}" for field in fields}
    expected = [5.0, 10.0, 17.0]  # 两样本等权，不按有效点数量加权。
    for field, mse in zip(fields, expected, strict=True):
        metric = items[f"post/mse_{field}"]
        assert metric["value"] == pytest.approx(mse)
        assert metric["semantics"] == {
            "field": field,
            "unit": "(m/s)^2",
            "split": "test",
            "statistic": "sample_equal_mean_mse",
            "data_identity": digest(fixed),
            "space": "physical-valid-domain",
        }
        assert metric["assets"] == [fixed]
        assert metric["asset_digests"][fixed]
    reports = list((tmp_path / "outputs/data").glob("*/post/metrics.json"))
    assert len(reports) == 1
    report = json.loads(reports[0].read_text())
    assert [item["mse"] for item in report["field_metrics"]] == expected
    assert [row["valid_count"] for row in report["rows"]] == [5, 3]
    assert not list((tmp_path / "outputs/runs").rglob("*.pt"))


def test_launch_initial_checkpoint_uses_supported_label_and_reads_back(tmp_path):
    code = tmp_path / "case"
    code.mkdir()
    script = code / "initial.py"
    script.write_text('"""仅保存初始化状态，不更新参数。"""\n')
    cfg = {
        "run_root": str(tmp_path / "runs"),
        "data_root": str(tmp_path / "data"),
        "pipeline": {"stages": ["initial"]},
        "seed": 17,
    }
    configuration_path = code / "config.yaml"
    configuration_path.write_text(yaml.safe_dump(cfg))
    paths = []
    weights = torch.arange(6, dtype=torch.float32).reshape(2, 3)

    def save_initial(configuration):
        assert configuration["seed"] == 17
        session = run.TrainingRun()
        paths.append(
            session.checkpoint(
                "latest", {"model": {"weight": weights}, "updates": 0}, namespace="initial"
            )
        )

    status = run.launch(
        {"initial": save_initial},
        script=str(script),
        config_loader=lambda path, overrides: yaml.safe_load(Path(path).read_text()),
        argv=["--config", str(configuration_path)],
    )
    assert status == 0
    assert len(paths) == 1
    checkpoint = paths[0]
    assert (
        checkpoint.relative_to(checkpoint.parents[2]).as_posix() == "checkpoints/initial/latest.pt"
    )
    restored = torch.load(checkpoint, weights_only=True)
    torch.testing.assert_close(restored["model"]["weight"], weights)
    assert restored["updates"] == 0
    assert restored["effective_config"]["seed"] == 17
    assert restored["effective_config"]["pipeline"]["stages"] == ["initial"]
    assert "optimizer" not in restored
    assets = json.loads((checkpoint.parents[2] / "artifacts/assets.json").read_text())["items"]
    assert assets["train/initial/latest"]["path"] == str(checkpoint)
    assert assets["train/initial/latest"]["kind"] == "checkpoint"
