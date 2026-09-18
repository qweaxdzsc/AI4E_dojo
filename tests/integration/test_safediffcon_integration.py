"""控制模型接入的数值、恢复、固定结果与配置交接回归。"""

from pathlib import Path

import numpy as np
import pytest
import torch

from ai4e_contrib.ability.eval.safediffcon.control import metrics
from ai4e_contrib.ability.training.safediffcon.moving_average import MovingAverage
from ai4e_contrib.application.pde_control.safediffcon.configuration import load_configuration
from ai4e_contrib.application.pde_control.safediffcon.stream import BatchStream
from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.applications.pde_control.infer import save_results
from ai4e_core.applications.pde_control.post import analyze

ROOT = Path(__file__).resolve().parents[2]


def test_tail_and_resume():
    stream = BatchStream(7, 3, seed=42)
    first = [stream.next(), stream.next(), stream.next()]
    assert list(map(len, first)) == [3, 3, 1]
    assert sorted(torch.cat(first).tolist()) == list(range(7))
    restored = BatchStream(7, 3, seed=99)
    restored.load_state_dict(stream.state_dict())
    for _ in range(8):
        torch.testing.assert_close(stream.next(), restored.next(), rtol=0, atol=0)
    with pytest.raises(ValueError):
        BatchStream(8, 3).load_state_dict(stream.state_dict())


def test_exact_resume_scheduler_and_ema(tmp_path):
    def objects():
        torch.manual_seed(13)
        model = torch.nn.Linear(2, 1)
        opt = torch.optim.Adam(model.parameters(), lr=0.001)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, 10)
        ema = MovingAverage(model, update_every=1)
        return model, opt, sched, ema, BatchStream(7, 3)

    def batch(i):
        return torch.stack((i.float(), torch.rand(len(i))), dim=1)

    def objective(m, x):
        return m(x).square().mean()

    m, o, s, e, st = objects()
    expected = fit_iterations(
        m, o, st, batch, objective, updates=5, scheduler=s, after_update=lambda i, m: e.update()
    )
    m2, o2, s2, e2, st2 = objects()
    losses = fit_iterations(
        m2,
        o2,
        st2,
        batch,
        objective,
        updates=2,
        scheduler=s2,
        after_update=lambda i, m: e2.update(),
    )
    checkpoint = tmp_path / "resume.pt"
    torch.save(
        capture_iteration(
            m2,
            o2,
            updates=2,
            stream=st2,
            contract={"test": 1},
            history=losses,
            ema=e2,
            scheduler=s2,
        ),
        checkpoint,
    )
    m3, o3, s3, e3, st3 = objects()
    saved = restore_iteration(
        checkpoint, m3, o3, stream=st3, contract={"test": 1}, ema=e3, scheduler=s3
    )
    actual = fit_iterations(
        m3,
        o3,
        st3,
        batch,
        objective,
        updates=5,
        start=2,
        history=saved["history"],
        scheduler=s3,
        after_update=lambda i, m: e3.update(),
    )
    assert expected == actual
    for key, value in m.state_dict().items():
        torch.testing.assert_close(value, m3.state_dict()[key], rtol=0, atol=0)
    for key, value in e.state.items():
        torch.testing.assert_close(value, e3.state[key], rtol=0, atol=0)
    assert s.state_dict() == s3.state_dict()


def test_update_order_and_cancel():
    model = torch.nn.Linear(1, 1)
    opt = torch.optim.SGD(model.parameters(), lr=0.1)
    order = []
    opt.register_step_post_hook(lambda *args: order.append("optimizer"))

    class Scheduler:
        def step(self):
            order.append("scheduler")

    saved = []
    with pytest.raises(TimeoutError):
        fit_iterations(
            model,
            opt,
            BatchStream(2, 1),
            lambda i: torch.ones(1, 1),
            lambda m, x: m(x).square().mean(),
            updates=2,
            scheduler=Scheduler(),
            max_grad_norm=None,
            after_update=lambda *a: order.append("ema"),
            cancelled=lambda: bool(order),
            checkpoint=lambda i, h, status: saved.append((i, status)),
        )
    assert order == ["optimizer", "scheduler", "ema"]
    assert saved == [(1, "interrupted")]


def test_calibration_product_and_rank(monkeypatch):
    from ai4e_contrib.ability.constraint.safediffcon import calibration as c

    states = torch.zeros(3, 3, 16, 128)
    states[:, 2, :11] = torch.tensor([0.02, 0.07, 0.1])[:, None, None]

    def sample(model, state, target, **kwargs):
        result = state.clone()
        result[:, 2, :11] += 0.02
        return result

    monkeypatch.setattr(c, "sample", sample)
    target = torch.zeros(3, 11, 128)
    result = c.calibrate(
        torch.nn.Identity(),
        states,
        target,
        case="burgers",
        q=0.1,
        weight=2.0,
        alpha=0.5,
        previous_q=0.2,
        previous_weight=3.0,
    )
    cost1 = torch.relu(torch.tensor([0.2, 0.7, 1.0]) + 0.1 - 0.64) * 2
    cost2 = torch.relu(torch.tensor([0.2, 0.7, 1.0]) + 0.2 - 0.64) * 3
    weights = torch.exp(-cost1) * torch.exp(-cost2)
    weights = 3 * weights / weights.sum()
    assert result == pytest.approx(float((weights * 0.2).sort().values[1]), abs=1e-6)


def test_results_readback_and_tamper(tmp_path):
    target = np.zeros((2, 11, 128), dtype=np.float32)
    response = target.copy()
    response[1, -1, 0] = 1.0
    score = metrics(response, target, case="burgers")
    assert score["J"] == 1 / 256 and score["R_sample"] == 0.5
    checkpoint = tmp_path / "weights"
    checkpoint.write_bytes(b"weights")
    result = save_results(
        tmp_path / "results",
        case="burgers",
        ids=[7, 8],
        target=target,
        paper_target=target,
        controls=np.zeros((2, 10, 128)),
        prediction=response,
        response=response,
        checkpoint=checkpoint,
        q=0.1,
        metrics=score,
        derived={
            "energy": {
                "values": (response**2).mean(-1),
                "valid": np.ones((2, 11), dtype=bool),
                "units": "u^2",
                "axes": "B,T",
            }
        },
    )
    checkpoint.unlink()  # 固定结果独立于模型权重文件，post不能重建模型。
    report = analyze(result, tmp_path / "post", evaluate=metrics)
    import json

    payload = json.loads(Path(report).read_text())
    assert payload["metrics"] == score
    assert payload["derived"]["energy"]["maximum"] == 1 / 128
    array = Path(result).parent / "response.npy"
    with array.open("ab") as f:
        f.write(b"tamper")
    with pytest.raises(ValueError, match="内容改变"):
        analyze(result, tmp_path / "badpost", evaluate=metrics)


def test_tokamak_separate_target():
    target = np.ones((2, 3, 122)) * 5
    dataset = target.copy()
    dataset[:, 0] += 1
    score = metrics(target, target, case="tokamak", paper_target=dataset)
    assert score["J_source_outputs"] == 0 and score["J_dataset_targets"] == 1
    assert score["R_sample"] == 0


def test_configuration_overrides_and_unknown(tmp_path):
    source = ROOT / "examples/safediffcon/burgers/quick.yaml"
    config = tmp_path / "config.yaml"
    config.write_text(source.read_text())
    cfg = load_configuration(config, ["model.dim=32", "data_root=./newdata", "train.updates=3"])
    assert cfg["model"]["dim"] == 32 and cfg["data_root"] == str(tmp_path / "newdata")
    for override in ["train.updates=200000", "train.typo=2", "old=2", "posttrain.rounds=8"]:
        with pytest.raises(ValueError):
            load_configuration(config, [override])


def test_recipe_imports_outside_repository(tmp_path):
    """复制后的阶段导入不依赖仓库根或源码路径。"""
    import shutil
    import subprocess
    import sys

    destination = tmp_path / "copied"
    shutil.copytree(ROOT / "recipes/safediffcon", destination)
    code = "import rawprep,trainprep,train,posttrain,infer,post,pipeline; from configuration import component,load_configuration; print('ok')"
    result = subprocess.run(
        [sys.executable, "-c", code], cwd=destination, capture_output=True, text=True, check=False
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "ok"


def test_derived_requires_units_and_validity(tmp_path):
    x = np.zeros((1, 11, 128))
    weight = tmp_path / "weights"
    weight.write_bytes(b"w")
    with pytest.raises(ValueError, match="values/valid/units/axes"):
        save_results(
            tmp_path / "results",
            case="burgers",
            ids=[0],
            target=x,
            paper_target=x,
            controls=np.zeros((1, 10, 128)),
            prediction=x,
            response=x,
            checkpoint=weight,
            q=0.0,
            metrics={},
            derived={"margin": np.zeros((1, 11))},
        )


def test_stage_refuses_interrupted_checkpoint(tmp_path):
    from ai4e_core.applications.pde_control.model import restore_model

    path = tmp_path / "stopped.pt"
    torch.save(
        {
            "version": 2,
            "contract": {"case": "burgers", "model": {"dim": 8}},
            "status": "interrupted",
        },
        path,
    )
    with pytest.raises(ValueError, match="已完成"):
        restore_model(
            path, construct=lambda **k: None, settings={"dim": 8}, case="burgers", device="cpu"
        )


def test_stage_rejects_wrong_phase_before_data_read(tmp_path):
    from ai4e_contrib.application.pde_control.safediffcon.training import posttrain_round

    path = tmp_path / "wrong.pt"
    torch.save(
        {
            "version": 2,
            "contract": {"case": "burgers", "model": {"dim": 8}, "phase": "adapt"},
            "status": "complete",
            "model": {},
        },
        path,
    )
    cfg = {
        "seed": 42,
        "case": "burgers",
        "model": {"dim": 8},
        "train": {"device": "cpu"},
        "posttrain": {},
    }
    with pytest.raises(ValueError, match="轮次"):
        posttrain_round(
            cfg,
            {},
            str(path),
            round_index=0,
            q=0.0,
            construct=lambda **k: torch.nn.Identity(),
            objective=None,
            session=None,
        )


@pytest.mark.parametrize("case,expected", [("burgers", 0.3), ("tokamak", 5.0)])
def test_inference_product_preserves_case_weight_semantics(tmp_path, monkeypatch, case, expected):
    from ai4e_contrib.application.pde_control.safediffcon import inference as module
    from ai4e_core.applications.pde_control.contracts import digest

    path = tmp_path / "prepared"
    path.write_text("frozen")
    prior = {
        "contract": {"phase": "posttrain", "prepared": digest(path)},
        "algorithm_state": {"round": 1, "q": 0.2},
    }
    monkeypatch.setattr(module, "restore_model", lambda *a, **k: (torch.nn.Identity(), prior))
    monkeypatch.setattr(module, "calibration_inputs", lambda *a: (None, None))
    calls = []
    monkeypatch.setattr(module, "calibrate", lambda *a, **k: calls.append(k) or 0.1)
    cfg = {
        "seed": 42,
        "case": case,
        "model": {},
        "infer": {"device": "cpu", "weight": 0.3, "adaptation_updates": 0},
        "posttrain": {"weight": 5.0, "alpha": 0.9},
    }
    module.adapt(cfg, {"train": str(path)}, "weights", {}, construct=None, guide=None, session=None)
    assert calls[0]["previous_weight"] == expected


def test_tokamak_duplicate_sources_rejected(tmp_path):
    import zipfile

    from ai4e_contrib.application.datasets.safediffcon.arrays import read_tokamak

    name = "data-00003-of-00004.arrow"
    (tmp_path / name).write_bytes(b"first")
    with zipfile.ZipFile(tmp_path / "copy.zip", "w") as z:
        z.writestr(name, b"other")
    with pytest.raises(ValueError, match="副本内容冲突"):
        read_tokamak(tmp_path, "test")


def test_safety_cost_preserves_original_tie_gradient():
    """maximum在精确安全边界取半梯度，不能用ReLU改变原算法。"""
    from ai4e_contrib.ability.constraint.safediffcon.objective import cost

    x = torch.full((1, 3, 122), 4.98, dtype=torch.float64, requires_grad=True)
    value = cost(x, None, case="tokamak").sum()
    value.backward()
    assert value.item() == 0
    assert x.grad[:, 1].sum().item() == pytest.approx(-0.5)


@pytest.mark.parametrize(
    "failure", ["nan_target", "wrong_time", "unknown_case", "bad_paper_target"]
)
def test_metric_invalid_inputs_rejected(failure):
    response = np.zeros((1, 3, 122))
    target = response.copy()
    case = "tokamak"
    paper = None
    if failure == "nan_target":
        target[0, 0, 0] = np.nan
    if failure == "wrong_time":
        response = response[:, :, :10]
        target = target[:, :, :10]
    if failure == "unknown_case":
        case = "other"
    if failure == "bad_paper_target":
        paper = np.zeros((1, 3, 1))
    with pytest.raises(ValueError):
        metrics(response, target, case=case, paper_target=paper)


def test_continuation_total_updates_and_same_configuration_contract():
    from pathlib import Path

    from ai4e_contrib.application.pde_control.safediffcon.configuration import (
        load_configuration,
        validate,
    )

    path = Path(__file__).resolve().parents[2] / "examples/safediffcon/burgers/quick.yaml"
    cfg = load_configuration(path, ["train.updates=12000"])
    assert cfg["train"]["updates"] == 12000
    assert cfg["model"]["dim"] == 64
    cfg["train"]["updates"] = 20001
    with pytest.raises(ValueError, match="总更新"):
        validate(cfg)
    for value in ["true", "3.5", "0"]:
        with pytest.raises(ValueError, match="总更新"):
            load_configuration(path, [f"train.updates={value}"])
