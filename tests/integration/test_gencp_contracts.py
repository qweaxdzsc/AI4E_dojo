"""耦合准备身份、检查点组合、参数和原后处理归约验收。"""

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.postproc.gencp.reference import fsi_reference
from ai4e_core.abilities.eval.trajectory import trajectory_metrics
from ai4e_core.abilities.inference.coupled_steps import sequential_euler_step
from ai4e_core.abilities.inference.integration import integrate
from ai4e_core.applications.coupled_physics.model import (
    bind_checkpoint_group,
    load_checkpoint_group,
)
from ai4e_core.applications.coupled_physics.trainprep import prepare


def test_group_replacement_and_incompatible_normalization(tmp_path):
    model = torch.nn.Linear(2, 1)

    def checkpoint(field, system, updates):
        path = tmp_path / f"{field}_{system}_{updates}.pt"
        torch.save(
            {
                "model": model.state_dict(),
                "updates": updates,
                "contract": {"field": field, "system_id": system, "model": {}},
            },
            path,
        )
        return path

    a, b = checkpoint("a", "same", 2), checkpoint("b", "same", 7)
    group = bind_checkpoint_group(
        {"a": a, "b": b}, tmp_path / "group.json", required_fields=("a", "b")
    )
    models, record = load_checkpoint_group(
        group, system_id="same", construct=lambda settings: torch.nn.Linear(2, 1), device="cpu"
    )
    assert set(models) == {"a", "b"}
    b2 = checkpoint("b", "same", 9)
    new = bind_checkpoint_group(
        {"a": a, "b": b2}, tmp_path / "replacement.json", required_fields=("a", "b")
    )
    assert new != group and record["fields"]["b"]["updates"] == 7
    with pytest.raises(ValueError, match="缺场"):
        bind_checkpoint_group({"a": a}, tmp_path / "bad.json", required_fields=("a", "b"))
    with pytest.raises(ValueError, match="不兼容"):
        bind_checkpoint_group(
            {"a": a, "b": checkpoint("b", "different", 9)},
            tmp_path / "bad.json",
            required_fields=("a", "b"),
        )
    a.write_bytes(b"changed")
    with pytest.raises(ValueError, match="发生变化"):
        load_checkpoint_group(
            group, system_id="same", construct=lambda settings: None, device="cpu"
        )


def test_prepare_rejects_coupled_identity_and_time(tmp_path):
    first = {"records": [{"id": "0", "index": 0}], "time_indices": [0, 1]}
    second = {"records": [{"id": "1", "index": 1}], "time_indices": [0, 1]}
    with pytest.raises(ValueError, match="不配对"):
        prepare({"a/couple": first, "b/couple": second}, tmp_path / "p.json", dataset="test")
    second = {"records": first["records"], "time_indices": [0, 2]}
    with pytest.raises(ValueError, match="时间"):
        prepare({"a/couple": first, "b/couple": second}, tmp_path / "p.json", dataset="test")


def test_reference_mask_smoothing_and_axis_metrics():
    from scipy.ndimage import gaussian_filter

    rng = np.random.default_rng(3)
    prediction = rng.random((2, 3, 4, 5, 4)).astype("float32")
    target = rng.random(prediction.shape).astype("float32")
    frozen = prediction.copy()
    masked, truth, smoothed, _mask = fsi_reference(prediction, target)
    np.testing.assert_array_equal(prediction, frozen)
    np.testing.assert_allclose(smoothed[0, 1, :, :, 3], gaussian_filter(frozen[0, 1, :, :, 3], 0.8))
    np.testing.assert_array_equal(smoothed[..., :3], frozen[..., :3])
    np.testing.assert_array_equal(truth, target * (target[..., 3:4] > 0.04))
    expected = []
    for c in range(4):
        p, t = torch.from_numpy(masked[..., c]), torch.from_numpy(truth[..., c])
        expected.append(float(((p - t).flatten(1).norm(dim=1) / t.flatten(1).norm(dim=1)).mean()))
    metrics = trajectory_metrics(
        torch.from_numpy(masked).permute(0, 4, 1, 2, 3),
        torch.from_numpy(truth).permute(0, 4, 1, 2, 3),
        axes=("B", "C", "T", "H", "W"),
    )
    np.testing.assert_allclose(metrics["component_relative_l2"], expected, rtol=1e-6)


def test_integration_cancel_and_nonfinite():
    states = {"a": torch.zeros(1)}
    velocities = {"a": lambda states, t: torch.ones(1)}
    with pytest.raises(InterruptedError):
        integrate(
            states,
            [0.0, 1.0],
            step=sequential_euler_step,
            velocities=velocities,
            order=("a",),
            cancelled=lambda: True,
        )
    with pytest.raises(FloatingPointError):
        integrate(
            states,
            [0.0, 1.0],
            step=sequential_euler_step,
            velocities={"a": lambda states, t: torch.full((1,), float("nan"))},
            order=("a",),
        )


def test_iteration_resume_all_state_and_completed_budget(tmp_path):
    from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
    from ai4e_core.abilities.training.iteration_stream import IterationStream
    from ai4e_core.abilities.training.iterations import fit_iterations
    from ai4e_core.abilities.training.moving_average import MovingAverage

    def setup():
        torch.manual_seed(7)
        model = torch.nn.Linear(2, 1)
        optimizer = torch.optim.Adam(model.parameters(), lr=0.02)
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 7)
        return (
            model,
            optimizer,
            scheduler,
            IterationStream(8, 2, seed=3),
            MovingAverage(model, 0.995, buffer_policy="copy"),
        )

    data = torch.arange(16).float().reshape(8, 2) / 10

    def objective(model, batch):
        return (model(batch) - torch.randn(len(batch), 1)).square().mean()

    def fit(parts, stop, start=0, history=None):
        model, opt, schedule, stream, ema = parts
        return fit_iterations(
            model,
            opt,
            stream,
            lambda ids: data[ids],
            objective,
            updates=stop,
            start=start,
            history=history,
            ema=ema,
            scheduler=schedule,
        )

    whole = setup()
    expected_history = fit(whole, 7)
    expected = capture_iteration(
        whole[0],
        whole[1],
        updates=7,
        stream=whole[3],
        contract={},
        history=expected_history,
        ema=whole[4],
        scheduler=whole[2],
    )
    split = setup()
    history = fit(split, 3)
    torch.save(
        capture_iteration(
            split[0],
            split[1],
            updates=3,
            stream=split[3],
            contract={},
            history=history,
            ema=split[4],
            scheduler=split[2],
        ),
        tmp_path / "state.pt",
    )
    split = setup()
    state = restore_iteration(
        tmp_path / "state.pt",
        split[0],
        split[1],
        stream=split[3],
        contract={},
        ema=split[4],
        scheduler=split[2],
    )
    history = fit(split, 7, 3, state["history"])
    actual = capture_iteration(
        split[0],
        split[1],
        updates=7,
        stream=split[3],
        contract={},
        history=history,
        ema=split[4],
        scheduler=split[2],
    )
    for key in ("model", "optimizer", "scheduler", "ema", "stream", "history", "torch_rng"):
        torch.testing.assert_close(actual[key], expected[key], rtol=0, atol=0)
    assert fit(split, 7, 7, history) == history


def test_nonboundary_truth_cannot_change_coupled_inputs(monkeypatch):
    from types import SimpleNamespace

    from ai4e_contrib.ability.transform.gencp.conditions import (
        fluid_condition,
        neutron_condition,
        solid_condition,
    )
    from ai4e_contrib.application.coupled_physics.gencp import cases

    fields = {"neutron": (20, 1, 2), "solid": (8, 1, 3), "fluid": (12, 4, 1)}
    changed = [False]

    def reader(record, description):
        width, channels, conditions = fields[description["field"]]
        target = torch.ones(2, 3, width, channels)
        condition = torch.ones(2, 3, width, conditions)
        if changed[0]:
            target[:, :, 1:, :] += 100
            if description["field"] == "neutron":
                condition[..., 0] += 100
        return {"input": condition, "target": target, "physical": target, "id": "0"}

    monkeypatch.setattr(
        cases, "dataset_adapter", lambda dataset: SimpleNamespace(read_sample=reader)
    )
    prepared = {
        "dataset": "ntcouple",
        "content_id": "test",
        "descriptions": {
            field + "/couple": {"field": field, "records": [{"id": "0"}], "time_indices": [0, 1]}
            for field in fields
        },
    }
    torch.manual_seed(2)
    before, context_a, _ = cases.inference_inputs(prepared, fields, device="cpu", flow_steps=3)
    changed[0] = True
    torch.manual_seed(2)
    after, context_b, _ = cases.inference_inputs(prepared, fields, device="cpu", flow_steps=3)
    for field in fields:
        torch.testing.assert_close(before.states[field], after.states[field], rtol=0, atol=0)
    for operation in (neutron_condition, solid_condition, fluid_condition):
        torch.testing.assert_close(
            operation(before.states, context_a["boundary"]),
            operation(after.states, context_b["boundary"]),
            rtol=0,
            atol=0,
        )


def test_real_mps_model_resume_matches_continuous(tmp_path):
    if not torch.backends.mps.is_available():
        pytest.skip("本机 MPS 精确恢复专项")
    from pathlib import Path

    import yaml

    from ai4e_contrib.ability.constraint.gencp.objective import objective
    from ai4e_contrib.ability.model.gencp.adapters import construct
    from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
    from ai4e_core.abilities.training.iteration_stream import IterationStream
    from ai4e_core.abilities.training.iterations import fit_iterations
    from ai4e_core.abilities.training.moving_average import MovingAverage

    root = Path(__file__).resolve().parents[2]
    cfg = yaml.safe_load((root / "examples/gencp/ntcouple_sit_fno/config.yaml").read_text())
    values = {
        "input": torch.ones(4, 16, 64, 20, 2, device="mps"),
        "target": torch.ones(4, 16, 64, 20, 1, device="mps") * 0.25,
    }

    def setup():
        torch.manual_seed(42)
        model = construct(cfg["fields"]["neutron"]["model"]).to("mps")
        optimizer = torch.optim.Adam(model.parameters(), lr=0.0001, betas=(0.9, 0.99))
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, 6)
        return (
            model,
            optimizer,
            scheduler,
            IterationStream(4, 2),
            MovingAverage(model, 0.995, buffer_policy="copy"),
        )

    def fit(parts, updates, start=0, history=None):
        return fit_iterations(
            parts[0],
            parts[1],
            parts[3],
            lambda ids: {k: v[ids] for k, v in values.items()},
            lambda model, batch: objective(model, batch, **cfg["fields"]["neutron"]["objective"]),
            updates=updates,
            start=start,
            history=history,
            scheduler=parts[2],
            ema=parts[4],
        )

    full = setup()
    history = fit(full, 6)
    expected = capture_iteration(
        full[0],
        full[1],
        updates=6,
        stream=full[3],
        contract={},
        history=history,
        ema=full[4],
        scheduler=full[2],
    )
    parts = setup()
    history = fit(parts, 3)
    torch.save(
        capture_iteration(
            parts[0],
            parts[1],
            updates=3,
            stream=parts[3],
            contract={},
            history=history,
            ema=parts[4],
            scheduler=parts[2],
        ),
        tmp_path / "mps.pt",
    )
    parts = setup()
    state = restore_iteration(
        tmp_path / "mps.pt",
        parts[0],
        parts[1],
        stream=parts[3],
        contract={},
        ema=parts[4],
        scheduler=parts[2],
    )
    history = fit(parts, 6, 3, state["history"])
    actual = capture_iteration(
        parts[0],
        parts[1],
        updates=6,
        stream=parts[3],
        contract={},
        history=history,
        ema=parts[4],
        scheduler=parts[2],
    )
    for key in ("model", "optimizer", "scheduler", "ema", "stream", "history", "mps_rng"):
        torch.testing.assert_close(actual[key], expected[key], rtol=0, atol=0)


def test_configuration_paths_overrides_and_sampling_limits(tmp_path):
    from pathlib import Path

    import yaml

    from ai4e_contrib.application.coupled_physics.gencp.configuration import load_configuration

    source = Path(__file__).resolve().parents[2] / "examples/gencp/ntcouple_sit_fno/config.yaml"
    config = yaml.safe_load(source.read_text())
    config["inputs"]["train"]["resume"] = "weights/group.json"
    config["inputs"]["rawprep"]["source"] = "raw"
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(config))
    result = load_configuration(
        path, ["fields.neutron.lr=0.0002", "inputs.train.preparation=preparation.json"]
    )
    assert result["inputs"]["train"]["resume"] == str(tmp_path / "weights/group.json")
    assert result["inputs"]["rawprep"]["source"] == str(tmp_path / "raw")
    assert result["inputs"]["train"]["preparation"] == str(tmp_path / "preparation.json")
    with pytest.raises(ValueError, match="至少"):
        load_configuration(path, ["train.single_points=1"])
    with pytest.raises(ValueError, match="场 fluid"):
        load_configuration(path, ["fields.fluid.updates=1001"])
