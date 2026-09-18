"""WDNO 数值抽取、数据流、恢复和固定结果的圈定验收。"""

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path

import pytest
import torch

from ai4e_contrib.ability.training.moving_average import MovingAverage
from ai4e_contrib.ability.transform.wdno.burgers import conditions, decode, prepare, scale
from ai4e_contrib.application.spatiotemporal_pde.wdno.configuration import (
    load_configuration,
    validate,
)
from ai4e_contrib.application.spatiotemporal_pde.wdno.model import diffusion
from ai4e_contrib.application.spatiotemporal_pde.wdno.stream import SourceStream
from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iterations import fit_iterations

ROOT = Path(__file__).resolve().parents[2]
FROZEN = Path(
    "/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/frozen/source/burgers"
)
OPTIONS = {"dim": 8, "dim_mults": [1, 2], "groups": 1, "ddim_steps": 2}


def original():
    if not FROZEN.exists():
        pytest.skip("缺少冻结原源码，独立原版数值验收未运行")
    sys.path.insert(0, str(FROZEN))
    sys.path.insert(0, str(FROZEN / "ddpm_burgers"))
    from ddpm_burgers.diffusion_1d import GaussianDiffusion
    from ddpm_burgers.unet import Unet2D

    return GaussianDiffusion, Unet2D


def test_source_ast():
    if not FROZEN.exists():
        pytest.skip("缺少冻结原源码，AST对照未运行")
    base = ROOT / "packages/ai4e-contrib/ability"
    record = json.loads((base / "model/wdno/source.json").read_text())

    def definitions(path):
        out = {}
        for n in ast.parse(path.read_text()).body:
            if isinstance(n, ast.FunctionDef):
                out[n.name] = ast.dump(n, include_attributes=False)
            elif isinstance(n, ast.ClassDef):
                for method in n.body:
                    if isinstance(method, ast.FunctionDef):
                        out[
                            (n.name if n.name != "DenoisingObjective" else "GaussianDiffusion")
                            + "."
                            + method.name
                        ] = ast.dump(method, include_attributes=False)
        return out

    for name, entry in record["files"].items():
        path = base / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"]
        upstream = FROZEN / entry["source"]
        assert hashlib.sha256(upstream.read_bytes()).hexdigest() == entry["original_sha256"]
        a, b = definitions(upstream), definitions(path)
        for key in b:
            assert a[key] == b[key], (name, key)


def test_stream_matches_torch_loader_across_epochs():
    torch.manual_seed(19)
    loader = torch.utils.data.DataLoader(torch.arange(7), batch_size=3, shuffle=True, num_workers=0)
    expected = [batch for _ in range(3) for batch in loader]
    torch.manual_seed(19)
    stream = SourceStream(7, 3)
    actual = [stream.next() for _ in expected]
    assert all(torch.equal(a, b) for a, b in zip(expected, actual))


def test_transform_and_conditions_reference():
    original()
    from types import SimpleNamespace

    from ddpm_burgers import test_util
    from ddpm_burgers.data_burgers_1d import get_wavelet_super_preprocess
    from pytorch_wavelets import DWTForward
    from wave_trans import coef_to_tensor

    torch.manual_seed(13)
    u, f = torch.randn(2, 81, 120), torch.randn(2, 80, 120)
    fields = torch.stack((u, torch.nn.functional.pad(f, (0, 0, 0, 1))), 1)
    coefficients = coef_to_tensor(*DWTForward(J=1, mode="periodization", wave="bior2.4")(fields))
    expected, _, _ = get_wavelet_super_preprocess(
        rescaler=scale(),
        mode="periodization",
        wave_type="bior2.4",
        is_condition_u0=True,
        is_condition_uT=False,
    )({"coef": [coefficients], "ori_shape": [81, 120]})
    actual = prepare(u, f)
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    torch.testing.assert_close(decode(actual), fields, rtol=0, atol=3e-6)

    class Targets:
        def __init__(self, *a, **kw):
            self.ori_shape = [81, 120]

        def get(self, ids):
            return fields[ids]

    old = test_util.DiffusionDataset
    test_util.DiffusionDataset = Targets
    args = SimpleNamespace(
        dataset="1d",
        pad_mode="periodization",
        wave_type="bior2.4",
        is_condition_u0=True,
        is_condition_uT=False,
    )
    try:
        expected_u = test_util.get_target(args, True, [0, 1], device="cpu")[:, :32] / 10
        expected_f = (
            test_util.get_target(args, True, [0, 1], f=True, device="cpu") / scale()[:, 4:8]
        )
    finally:
        test_util.DiffusionDataset = old
    a, b = conditions(u, f)
    torch.testing.assert_close(a, expected_u, rtol=0, atol=0)
    torch.testing.assert_close(b, expected_f, rtol=0, atol=0)


def test_forward_loss_gradient_update_and_sample_reference():
    cls, net = original()
    torch.set_num_threads(4)
    torch.manual_seed(17)
    migrated = diffusion(OPTIONS)
    reference = cls(
        net(dim=8, dim_mults=(1, 2), channels=9, out_dim=9, resnet_block_groups=1),
        seq_length=(64, 64),
        padded_shape=[41, 60],
        ori_shape=[81, 120],
        pad_mode="periodization",
        wave_type="bior2.4",
        upsample_t=0,
        upsample_x=0,
        sampling_timesteps=2,
        ddim_sampling_eta=1,
        loss_layer_weight=scale(),
        is_condition_pad=True,
        is_condition_u0=True,
        is_condition_uT=False,
        is_condition_f=True,
    )
    reference.load_state_dict(migrated.state_dict())
    x = torch.randn(2, 9, 64, 64)
    t = torch.tensor([11, 250])
    noise = torch.randn_like(x)
    loss_a = migrated.p_losses(x.clone(), t, noise.clone())
    loss_b = reference.p_losses(x.clone(), t, noise.clone())
    assert torch.equal(loss_a, loss_b)
    loss_a.backward()
    loss_b.backward()
    for a, b in zip(migrated.parameters(), reference.parameters()):
        torch.testing.assert_close(a.grad, b.grad, rtol=0, atol=0)
    for m in (migrated, reference):
        opt = torch.optim.Adam(m.parameters(), lr=0.0001, betas=(0.9, 0.99))
        torch.nn.utils.clip_grad_norm_(m.parameters(), 1)
        opt.step()
    for a, b in zip(migrated.parameters(), reference.parameters()):
        torch.testing.assert_close(a, b, rtol=0, atol=0)
    kwargs = {"batch_size": 2, "u_init": torch.zeros(2, 32, 64), "f": torch.zeros(2, 4, 64, 64)}
    torch.manual_seed(25)
    a = migrated.sample(**kwargs)
    torch.manual_seed(25)
    b = reference.sample(**kwargs)
    torch.testing.assert_close(a, b, rtol=0, atol=0)


def test_full_resume_and_ema(tmp_path):
    torch.set_num_threads(4)

    def objects():
        torch.manual_seed(12)
        model = diffusion(OPTIONS)
        opt = torch.optim.Adam(model.parameters(), lr=0.0001, betas=(0.9, 0.99))
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(opt, 10000)
        ema = MovingAverage(model)
        return model, opt, sched, ema, SourceStream(7, 2)

    values = torch.zeros(7, 9, 64, 64)

    def execute(objects, updates, start=0, history=None):
        m, o, s, e, st = objects
        return fit_iterations(
            m,
            o,
            st,
            lambda ids: values[ids],
            lambda m, x: m(x),
            updates=updates,
            start=start,
            scheduler=s,
            after_update=lambda i, m: e.update(),
            history=history,
        )

    expected = objects()
    expected_loss = execute(expected, 4)
    first = objects()
    history = execute(first, 2)
    m, o, s, e, st = first
    path = tmp_path / "resume.pt"
    torch.save(
        capture_iteration(
            m, o, updates=2, stream=st, contract={"x": 1}, history=history, ema=e, scheduler=s
        ),
        path,
    )
    second = objects()
    m, o, s, e, st = second
    state = restore_iteration(path, m, o, stream=st, contract={"x": 1}, ema=e, scheduler=s)
    actual = execute(second, 4, state["updates"], state["history"])
    assert actual == expected_loss
    for name, p in expected[0].state_dict().items():
        assert torch.equal(p, m.state_dict()[name])
    for name, p in expected[3].state.items():
        assert torch.equal(p, e.state[name])
    assert s.state_dict() == expected[2].state_dict()
    with pytest.raises(ValueError, match="语义冲突"):
        restore_iteration(path, m, o, stream=st, contract={"x": 2}, ema=e, scheduler=s)


def test_config_paths_and_rejected_keys(tmp_path):
    cfg = load_configuration(ROOT / "recipes/wdno/config.yaml", ["train.updates=3"])
    assert cfg["train"]["updates"] == 3
    assert cfg["seed"] == 0  # 原训练seed与数据划分seed=42分开。
    assert Path(cfg["data_root"]).is_absolute()
    bad = copy.deepcopy(cfg)
    bad["model"]["unknown"] = 1
    with pytest.raises(ValueError):
        validate(bad)
    bad = copy.deepcopy(cfg)
    bad["inputs"]["train"] = {"preparation": "x"}
    with pytest.raises(ValueError):
        validate(bad)
    with pytest.raises(ValueError):
        load_configuration(ROOT / "recipes/wdno/config.yaml", ["train.learning_rate=1"])


def test_signal_restores_handler_and_cancellation_saves_boundary():
    import signal

    from ai4e_core.abilities.training.cancellation import cancellation

    previous = signal.getsignal(signal.SIGINT)
    with cancellation() as stopped:
        assert not stopped()
        signal.raise_signal(signal.SIGINT)
        assert stopped()
    assert signal.getsignal(signal.SIGINT) == previous
    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.Adam(model.parameters())
    saved = []
    with pytest.raises(TimeoutError):
        fit_iterations(
            model,
            optimizer,
            SourceStream(2, 1),
            lambda ids: ids.float().view(-1, 1),
            lambda m, x: m(x).square().mean(),
            updates=3,
            cancelled=lambda: True,
            checkpoint=lambda *args: saved.append(args),
        )
    assert saved == [(0, [], "interrupted")]


def test_original_ddpm_loop():
    from ai4e_contrib.ability.inference.wdno.diffusion import GaussianDiffusion
    from ai4e_contrib.application.spatiotemporal_pde.wdno.model import network

    cls, net = original()
    torch.set_num_threads(4)
    options = {
        "seq_length": (64, 64),
        "padded_shape": [41, 60],
        "ori_shape": [81, 120],
        "pad_mode": "periodization",
        "wave_type": "bior2.4",
        "upsample_t": 0,
        "upsample_x": 0,
        "timesteps": 4,
        "sampling_timesteps": 4,
        "loss_layer_weight": scale(),
        "is_condition_pad": True,
        "is_condition_u0": True,
        "is_condition_uT": False,
        "is_condition_f": True,
    }
    migrated = GaussianDiffusion(network(OPTIONS), **options)
    reference = cls(
        net(dim=8, dim_mults=(1, 2), channels=9, out_dim=9, resnet_block_groups=1), **options
    )
    reference.load_state_dict(migrated.state_dict())
    kwargs = {"batch_size": 1, "u_init": torch.zeros(1, 32, 64), "f": torch.zeros(1, 4, 64, 64)}
    torch.manual_seed(83)
    expected = reference.sample(**kwargs)
    torch.manual_seed(83)
    actual = migrated.sample(**kwargs)
    assert torch.isfinite(actual).all()
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)


def test_shared_training_preserves_legacy_iterator_keywords(tmp_path):
    from ai4e_core.applications.pde_control.train import train_model

    def legacy(
        model,
        optimizer,
        stream,
        batch,
        objective,
        *,
        updates,
        start,
        scheduler,
        ema,
        after_update,
        checkpoint,
        evaluate_every,
        deadline,
        history,
        max_grad_norm,
    ):
        return fit_iterations(
            model,
            optimizer,
            stream,
            batch,
            objective,
            updates=updates,
            start=start,
            scheduler=scheduler,
            ema=ema,
            after_update=after_update,
            checkpoint=checkpoint,
            evaluate_every=evaluate_every,
            deadline=deadline,
            history=history,
            max_grad_norm=max_grad_norm,
        )

    class Session:
        def checkpoint(self, label, payload, *, namespace):
            return tmp_path / "latest.pt"

        def report(self, value, *, stage):
            pass

    model = torch.nn.Linear(1, 1)
    result = train_model(
        model,
        torch.optim.Adam(model.parameters()),
        SourceStream(2, 1),
        lambda ids: ids.float().view(-1, 1),
        lambda m, x: m(x).square().mean(),
        updates=1,
        session=Session(),
        contract={},
        namespace="old",
        iterate=legacy,
    )
    assert result["updates"] == 1 and result["status"] == "complete"
