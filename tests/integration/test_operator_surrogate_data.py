"""NASA 属性表及 POD 时间身份的小样本交接；不读取真实数据或训练网络。"""

import json
import shutil
from pathlib import Path

import h5py
import numpy as np
import pytest

from ai4e_contrib.application.datasets.nasa_crm.constants import (
    CONDITION_FIELDS,
    GLOBAL_TARGET_FIELDS,
)
from ai4e_contrib.application.surrogate_modeling import preparation
from ai4e_contrib.application.surrogate_modeling.configuration import validate
from ai4e_contrib.application.surrogate_modeling.fitting import fit_predictor
from ai4e_contrib.application.surrogate_modeling.prediction import predict_prepared
from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json


def nasa_fixture(tmp_path, test_offset=20):
    rng = np.random.default_rng(124)
    paths, raw = {}, {}
    for split, count in (("train", 40), ("test", 4)):
        x = rng.normal(size=(count, 6)) + (test_offset if split == "test" else 0)
        y = np.column_stack((x[:, 0] ** 2 + 2 * x[:, 1], x[:, 2] * x[:, 3], 1 + x[:, 4] - x[:, 5]))
        path = tmp_path / (split + ".h5")
        with h5py.File(path, "w") as stream:
            for row in range(count):
                group = stream.create_group(f"Sample{row + 1:03d}")
                for name, value in zip(CONDITION_FIELDS, x[row], strict=True):
                    group.attrs[name] = value
                for name, value in zip(GLOBAL_TARGET_FIELDS, y[row], strict=True):
                    group.attrs[name] = value
        paths[split], raw[split] = path, (x, y)
    return paths, raw


def test_nasa_sources_statistics_and_global_only(tmp_path):
    paths, raw = nasa_fixture(tmp_path)
    manifest = preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "prepared")
    train, arrays = preparation.read_prepared(manifest, "train")
    test, other = preparation.read_prepared(manifest, "test")
    statistics = train["metadata"]["statistics"]
    np.testing.assert_allclose(statistics["input"]["mean"], raw["train"][0].mean(0))
    np.testing.assert_allclose(arrays["input"].mean(0), 0, atol=1e-14)
    assert np.mean(other["input"]) > 5  # 测试数据不参与统计。
    assert train["metadata"]["ids"][0] != test["metadata"]["ids"][0]
    assert train["metadata"]["source"]["source_id"] != test["metadata"]["source"]["source_id"]
    assert train["metadata"]["fields"] == list(GLOBAL_TARGET_FIELDS)
    assert arrays["physical_target"].shape == (40, 1, 3)
    assert json.loads(Path(manifest).read_text())["diagnostics"]["quadratic_rank"] == 28
    assert "not a platform mesh" in train["metadata"]["scope"]


def test_nasa_fit_predict_fixed_result_and_move(tmp_path):
    paths, _ = nasa_fixture(tmp_path, test_offset=0)
    manifest = preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "prepared")
    _, train = preparation.read_prepared(manifest, "train")
    _, state, _ = fit_predictor("rsm", train["input"], train["target"])
    moved = tmp_path / "moved"
    shutil.move(str(Path(manifest).parent), moved)
    paths["train"].unlink()
    paths["test"].unlink()
    result = predict_prepared(state, moved / "manifest.json", tmp_path / "prediction", batch_size=3)
    _, arrays = read_arrays(result, kind="classic-results-v1")
    np.testing.assert_allclose(arrays["prediction"], arrays["target"], rtol=1e-10, atol=1e-10)


def test_nasa_same_source_or_nonfinite_rejected(tmp_path):
    paths, _ = nasa_fixture(tmp_path)
    with pytest.raises(ValueError, match="同一文件"):
        preparation.prepare_nasa(paths["train"], paths["train"], tmp_path / "same")
    with h5py.File(paths["test"], "r+") as source:
        source["Sample001"].attrs[CONDITION_FIELDS[0]] = np.nan
    with pytest.raises(ValueError, match="非有限"):
        preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "bad")


def cylinder_fixture(root, *, conflict=False, overlap=False):
    rng = np.random.default_rng(321)
    groups = {}
    for split, trajectories, windows in (
        ("train", ("trajectoryA", "trajectoryB"), 5),
        ("test", ("trajectoryA" if overlap else "trajectoryC",), 3),
    ):
        history, target, ids, times = [], [], [], []
        for trajectory in trajectories:
            frames = rng.normal(size=(windows * 3 + 1, 2, 2, 4))
            for start in range(0, windows * 3, 3):
                ids.append(trajectory + f"_{start:04d}")
                history.append(frames[start : start + 3].copy())
                target.append(frames[start + 3].copy())
                times.append(np.arange(start, start + 4))
        groups[split] = {
            "physical_input": np.asarray(history),
            "physical_target": np.asarray(target),
            "times": np.asarray(times),
            "ids": ids,
        }
    if conflict:
        groups["train"]["physical_input"][1, 0, 0, 0, 0] += 1
    mean, scale = (
        groups["train"]["physical_target"].mean((0, 1, 2)),
        groups["train"]["physical_target"].std((0, 1, 2)),
    )
    statistics = {
        "input": {"mean": [999] * 4, "scale": [1] * 4},
        "target": {"mean": mean.tolist(), "scale": scale.tolist()},
        "fit_ids": groups["train"]["ids"],
    }
    paths = {}
    for split, group in groups.items():
        count = len(group["ids"])
        arrays = {name: value for name, value in group.items() if name != "ids"}
        arrays.update(
            {
                "input": arrays["physical_input"],
                "target": arrays["physical_target"],
                "valid": np.ones((count, 2, 2), bool),
                "entity_ids": np.broadcast_to(np.arange(4).reshape(2, 2), (count, 2, 2)),
            }
        )
        path = save_arrays(
            root / split,
            arrays,
            kind="classic-inputs-v1",
            metadata={
                "case": "double_cylinder",
                "ids": group["ids"],
                "split": split,
                "fields": ["velocity_x", "velocity_y", "pressure", "sdf"],
                "units": ["published"] * 4,
                "statistics": statistics,
            },
        )
        paths[split] = str(Path(path).relative_to(root))
    save_json(root / "manifest.json", {"kind": "classic-preparation-v1", "splits": paths})
    return root / "manifest.json", groups, statistics


def test_pod_unique_training_snapshot_and_target_statistics(tmp_path, monkeypatch):
    classic, groups, statistics = cylinder_fixture(tmp_path / "classic")
    fitted = []
    original = preparation.fit_pod

    def spy(values, rank):
        fitted.append(values.copy())
        return original(values, rank)

    monkeypatch.setattr(preparation, "fit_pod", spy)
    path = preparation.prepare_pod_data(classic, tmp_path / "pod", rank=2)
    pod, context = preparation.read_pod(path)
    _, arrays = preparation.read_prepared(path, "test")
    assert len(fitted) == 1 and fitted[0].shape == (32, 16)
    assert len(context["fit_snapshot_ids"]) == 32
    assert all(
        identity[0] in {"trajectoryA", "trajectoryB"} for identity in context["fit_snapshot_ids"]
    )
    mean, scale = (
        np.asarray(statistics["target"]["mean"]),
        np.asarray(statistics["target"]["scale"]),
    )
    expected = pod.encode(((groups["test"]["physical_target"] - mean) / scale).reshape(3, -1))
    np.testing.assert_allclose(arrays["target"], expected)
    # 切断旧目录后新准备仍可读基和物理身份。
    classic.parent.rename(tmp_path / "hidden-classic")
    moved = tmp_path / "moved-pod"
    shutil.move(str(Path(path).parent), moved)
    assert preparation.read_pod(moved / "manifest.json")[1]["field_shape"] == [2, 2, 4]
    assert preparation.read_prepared(moved / "manifest.json", "test")[1]["times"].shape == (3, 4)


@pytest.mark.parametrize(
    "conflict,overlap,reason", [(True, False, "快照内容"), (False, True, "轨迹重叠")]
)
def test_pod_identity_failures(tmp_path, conflict, overlap, reason):
    classic, _, _ = cylinder_fixture(tmp_path / "classic", conflict=conflict, overlap=overlap)
    with pytest.raises(ValueError, match=reason):
        preparation.prepare_pod_data(classic, tmp_path / "pod", rank=2)


def test_pod_fit_prediction_decodes_same_basis(tmp_path):
    classic, _, _ = cylinder_fixture(tmp_path / "classic")
    path = preparation.prepare_pod_data(classic, tmp_path / "pod", rank=2)
    _, train = preparation.read_prepared(path, "train")
    model, state, _ = fit_predictor("rbf", train["input"], train["target"])
    record, test = preparation.read_prepared(path, "test")
    pod, _ = preparation.read_pod(path)
    stats = record["metadata"]["statistics"]["target"]
    expected = pod.decode(model.predict(test["input"])).reshape(3, 2, 2, 4) * np.asarray(
        stats["scale"]
    ) + np.asarray(stats["mean"])
    result = predict_prepared(state, path, tmp_path / "result", batch_size=2)
    _, arrays = read_arrays(result, kind="classic-results-v1")
    np.testing.assert_allclose(arrays["prediction"], expected, rtol=1e-12, atol=1e-12)
    np.testing.assert_array_equal(arrays["times"], test["times"])


def test_configuration_budget_and_stages():
    cfg = {
        "dataset": {"case": "nasa_global"},
        "model": {"family": "rsm", "parameters": {}},
        "train": {"seconds": 10800},
        "pipeline": {"stages": ["train", "infer", "post"]},
    }
    assert validate(cfg) == cfg
    cfg["train"]["seconds"] = float("nan")
    with pytest.raises(ValueError, match="时限"):
        validate(cfg)


@pytest.mark.parametrize("case", ["nasa", "pod"])
def test_kriging_fixed_variance_scale_and_independent_post(tmp_path, case):
    from ai4e_contrib.application.classic_networks.prediction import evaluate

    if case == "nasa":
        paths, _ = nasa_fixture(tmp_path, test_offset=0)
        prepared = preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "prepared")
    else:
        classic, _, _ = cylinder_fixture(tmp_path / "classic")
        prepared = preparation.prepare_pod_data(classic, tmp_path / "prepared", rank=2)
    record, train = preparation.read_prepared(prepared, "train")
    _, test = preparation.read_prepared(prepared, "test")
    model, state, _ = fit_predictor("kriging", train["input"], train["target"])
    _, expected = model.predict(test["input"], return_variance=True)
    result = predict_prepared(state, prepared, tmp_path / "result", batch_size=3)
    saved, arrays = read_arrays(result, kind="classic-results-v1")
    if case == "nasa":
        expected = (
            expected[:, None, :]
            * np.asarray(record["metadata"]["statistics"]["target"]["scale"]) ** 2
        )
        np.testing.assert_allclose(arrays["latent_variance"], expected)
        assert saved["metadata"]["uncertainty"]["units"] == ["(dimensionless)^2"] * 3
    else:
        np.testing.assert_allclose(arrays["coefficient_latent_variance"], expected)
        assert "not joint physical" in saved["metadata"]["uncertainty"]["scope"]
    # 固定结果自包含，评价不需要重新加载训练状态或准备。
    shutil.rmtree(Path(prepared).parent)
    assert (
        len(evaluate(result, tmp_path / "post")["field_metrics"])
        == train["physical_target"].shape[-1]
    )


def test_predict_prepared_accepts_unregistered_ordinary_predictor(tmp_path):
    paths, _ = nasa_fixture(tmp_path, test_offset=0)
    prepared = preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "prepared")
    record, arrays = preparation.read_prepared(prepared, "test")

    class Custom:
        def predict(self, x):
            return np.full((len(x), 3), 2.0)

    result = predict_prepared(
        {"kind": "user-constant"}, prepared, tmp_path / "result", predictor=Custom()
    )
    _, saved = read_arrays(result, kind="classic-results-v1")
    stats = record["metadata"]["statistics"]["target"]
    expected = np.broadcast_to(
        2 * np.asarray(stats["scale"]) + np.asarray(stats["mean"]), arrays["physical_target"].shape
    )
    np.testing.assert_allclose(saved["prediction"], expected)


@pytest.mark.parametrize("case", ["nasa_crm", "double_cylinder"])
def test_copied_surrogate_recipe_public_run_and_independent_post(tmp_path, case):
    import os
    import subprocess
    import sys

    import yaml

    root = Path(__file__).resolve().parents[2]
    code = tmp_path / "copied"
    shutil.copytree(root / "recipes/surrogate_modeling" / case, code)
    cfg = yaml.safe_load((code / "config.yaml").read_text())
    if case == "nasa_crm":
        paths, _ = nasa_fixture(tmp_path, test_offset=0)
        cfg["inputs"]["trainprep"] = {
            "train_h5": str(paths["train"]),
            "test_h5": str(paths["test"]),
        }
    else:
        classic, _, _ = cylinder_fixture(tmp_path / "classic")
        cfg["inputs"]["trainprep"]["dataset"] = str(classic)
    cfg["run_root"], cfg["data_root"] = str(tmp_path / "runs"), str(tmp_path / "data")
    cfg["train"]["snapshot"] = False
    configuration = code / "config.yaml"
    configuration.write_text(yaml.safe_dump(cfg))

    def execute(script):
        return subprocess.run(
            [sys.executable, str(code / script), "--config", str(configuration)],
            cwd=tmp_path,
            env=dict(os.environ),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )

    result = execute("pipeline.py")
    assert result.returncode == 0, result.stdout + result.stderr
    fixed = next((tmp_path / "data").glob("*/infer/fixed/manifest.json"))
    fitted = next((tmp_path / "data").glob("*/train/fitted/manifest.json"))
    prepared = next((tmp_path / "data").glob("*/trainprep/prepared/manifest.json"))
    first = json.loads(next((tmp_path / "data").glob("*/post/metrics.json")).read_text())
    # 同目录中子清单修改也应拒绝，即使顶层 manifest 字节完全没变。
    cfg["pipeline"]["stages"] = ["infer"]
    cfg["inputs"]["infer"] = {"preparation": str(prepared), "checkpoint": str(fitted)}
    cfg["model"]["parameters"]["invalid_changed_setting"] = True
    configuration.write_text(yaml.safe_dump(cfg))
    result = execute("infer.py")
    assert result.returncode != 0 and "不相容" in result.stdout + result.stderr
    # 配置中保留不可用 checkpoint/preparation，post 不能访问它们。
    shutil.rmtree(fitted.parent)
    shutil.rmtree(prepared.parent)
    cfg["pipeline"]["stages"] = ["post"]
    cfg["inputs"]["post"]["results"] = str(fixed)
    configuration.write_text(yaml.safe_dump(cfg))
    result = execute("post.py")
    assert result.returncode == 0, result.stdout + result.stderr
    reports = [
        json.loads(path.read_text()) for path in (tmp_path / "data").glob("*/post/metrics.json")
    ]
    assert len(reports) == 2 and all(report == first for report in reports)


def test_preparation_identity_tracks_children_and_moves(tmp_path):
    paths, _ = nasa_fixture(tmp_path)
    prepared = Path(preparation.prepare_nasa(paths["train"], paths["test"], tmp_path / "prepared"))
    original = preparation.preparation_identity(prepared)
    moved = tmp_path / "moved"
    shutil.move(str(prepared.parent), moved)
    assert preparation.preparation_identity(moved / "manifest.json") == original
    child = moved / "test/manifest.json"
    value = json.loads(child.read_text())
    value["metadata"]["ids"][0] += "-changed"
    child.write_text(json.dumps(value))
    assert preparation.preparation_identity(moved / "manifest.json") != original
