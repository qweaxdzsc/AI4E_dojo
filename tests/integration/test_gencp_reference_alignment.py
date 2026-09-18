"""锁定原函数与真实样本的 GenCP 数值对照。"""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest
import torch

from ai4e_contrib.ability.constraint.gencp.objective import objective
from ai4e_contrib.ability.transform.gencp.conditions import (
    fluid_condition,
    neutron_condition,
    solid_condition,
)
from ai4e_contrib.ability.transform.gencp.normalization import nt_normalize
from ai4e_core.abilities.training.checkpoint import capture_iteration, restore_iteration
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.iterations import fit_iterations
from ai4e_core.abilities.training.moving_average import MovingAverage
from tools.verification.gencp.reference import load_reference

SOURCE = Path("/Users/zonghui/work/new_code_project/GenCP/GenCP")


@pytest.fixture(scope="module")
def original():
    if not SOURCE.is_dir():
        pytest.skip("需要显式原仓库；缺环境不计参考验收")
    return load_reference(SOURCE)


def test_condition_maps_match_source_and_boundary_is_local(original):
    torch.manual_seed(2)
    values = [torch.randn(2, 16, 64, w, c) for w, c in [(20, 1), (8, 1), (12, 4)]]
    states = dict(zip(("neutron", "solid", "fluid"), values))
    boundary = {"neutron": torch.rand(2, 16, 64, 1, 1), "solid": torch.rand(2, 16, 64, 1, 1)}
    for ours, theirs in zip(
        (neutron_condition, solid_condition, fluid_condition),
        original["default_ntcouple_updates"](),
    ):
        torch.testing.assert_close(
            ours(states, boundary),
            theirs(values, list(boundary.values()), None, None),
            rtol=0,
            atol=0,
        )
    perturbed = {**states, "fluid": states["fluid"].clone()}
    perturbed["fluid"][..., 1:] += 100
    assert torch.equal(solid_condition(states, boundary), solid_condition(perturbed, boundary))


@pytest.mark.parametrize("field,channels", [("neutron", 1), ("solid", 1), ("fluid", 4)])
def test_normalizers_match_source(original, field, channels):
    from data.ntcouple_normalizer import NTcoupleNormalizer

    value = torch.rand(2, channels, 3, 4, 5) * 10
    expected = NTcoupleNormalizer.normalize(value, field)
    actual = nt_normalize(value.permute(0, 2, 3, 4, 1), field).permute(0, 4, 1, 2, 3)
    torch.testing.assert_close(actual, expected, rtol=0, atol=0)
    torch.testing.assert_close(
        nt_normalize(actual.permute(0, 2, 3, 4, 1), field, inverse=True).permute(0, 4, 1, 2, 3),
        NTcoupleNormalizer.renormalize(expected, field),
        rtol=0,
        atol=0,
    )


@pytest.mark.parametrize(
    "dataset,field,in_channels,out_channels",
    [
        ("ntcouple", "neutron", 3, 1),
        ("ntcouple", "solid", 4, 1),
        ("ntcouple", "fluid", 5, 4),
        ("turek_hron", "fluid", 4, 3),
        ("turek_hron", "structure", 4, 1),
    ],
)
def test_objective_and_update_match_original(original, dataset, field, in_channels, out_channels):
    class Probe(torch.nn.Module):
        def __init__(self):
            super().__init__()
            self.linear = torch.nn.Linear(in_channels, out_channels)

        def forward(self, x, t, x0=None, cond=None):
            return self.linear(x) + t.reshape(-1, 1, 1, 1, 1) * 0.001

    torch.manual_seed(7)
    model = Probe()
    reference = deepcopy(model)
    nt = dataset == "ntcouple"
    condition = torch.randn(2, 4, 3, 2, in_channels - out_channels if nt else 4)
    target = torch.randn(2, 4, 3, 2, out_channels if nt else 4)
    settings = SimpleNamespace(
        use_torchcfm=True,
        dataset_name=dataset if nt else dataset + "_data",
        x0_is_use_noise=True,
        use_clean_bc=True,
        use_clean_left_bc_for_solid=True,
        stage=field,
        out_channels=out_channels,
        log_every=1,
        is_use_tb=False,
    )
    trainer = SimpleNamespace(
        model=reference,
        ema=deepcopy(reference),
        optimizer=torch.optim.Adam(reference.parameters(), lr=0.001),
        args=settings,
        use_accelerator=False,
        data_normalizer=SimpleNamespace(preprocess=lambda x, y: (x, y)),
        cfm=original["ConditionalFlowMatcher"](sigma=0.01),
        train_steps=0,
        log_info=lambda message: None,
    )
    torch.manual_seed(99)
    value, _ = original["train_step"](
        trainer,
        condition.permute(0, 4, 1, 2, 3) if nt else condition,
        target.permute(0, 4, 1, 2, 3) if nt else target,
        {},
    )
    torch.manual_seed(99)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss = objective(
        model, {"input": condition, "target": target}, dataset=dataset, field=field, sigma=0.01
    )
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    assert float(loss.detach()) == value
    for a, b in zip(model.parameters(), reference.parameters()):
        torch.testing.assert_close(a, b, rtol=0, atol=0)


def test_mid_permutation_resume_matches_continuous(tmp_path):
    x = torch.arange(16, dtype=torch.float32).reshape(8, 2) / 16

    def setup():
        torch.manual_seed(14)
        model = torch.nn.Linear(2, 1)
        opt = torch.optim.Adam(model.parameters(), lr=0.01)
        stream = IterationStream(8, 2, seed=42)
        ema = MovingAverage(model, 0.995, buffer_policy="copy")
        return model, opt, stream, ema

    model, opt, stream, ema = setup()

    def objective(model, batch):
        return (model(batch) + torch.randn_like(batch[:, :1]) * 0.1).square().mean()

    fit_iterations(model, opt, stream, lambda i: x[i], objective, updates=7, ema=ema)
    expected = deepcopy(model.state_dict())
    model, opt, stream, ema = setup()
    history = fit_iterations(model, opt, stream, lambda i: x[i], objective, updates=3, ema=ema)
    torch.save(
        capture_iteration(
            model, opt, updates=3, stream=stream, contract={}, history=history, ema=ema
        ),
        tmp_path / "resume.pt",
    )
    model, opt, stream, ema = setup()
    state = restore_iteration(
        tmp_path / "resume.pt", model, opt, stream=stream, contract={}, ema=ema
    )
    fit_iterations(
        model,
        opt,
        stream,
        lambda i: x[i],
        objective,
        updates=7,
        start=state["updates"],
        ema=ema,
        history=state["history"],
    )
    for key, value in model.state_dict().items():
        torch.testing.assert_close(value, expected[key], rtol=0, atol=0)


@pytest.mark.parametrize("dataset", ["turek_hron", "double_cylinder"])
@pytest.mark.parametrize("split", ["train", "val"])
def test_fsi_reader_matches_original_real_window(original, dataset, split):
    from data.data_normalizer import RangeNormalizer
    from data.double_cylinder_dataset import DoubleCylinderDataset
    from data.turek_hron_dataset import TurekHronDataset

    from ai4e_contrib.application.datasets.gencp.fsi import coordinates, describe, read_sample

    root = Path("/Users/zonghui/work/project_simulation/dojo_train/gencp/raw")
    if not (root / dataset).is_dir():
        pytest.skip("需要 Turek 原始数据")
    reference = (TurekHronDataset if dataset == "turek_hron" else DoubleCylinderDataset)(
        str(root),
        length=999,
        input_size=3,
        output_size=12,
        stride=1,
        mode=split,
        stage="fluid",
        num_delta_t=0,
        dt=5 if dataset == "turek_hron" else 10,
    )
    normalizer = RangeNormalizer(reference, device="cpu")
    description = describe(root, dataset, "fluid", split, 16)
    grid = coordinates(description)
    assert len(grid["axes"]["H"]) == (108 if dataset == "turek_hron" else 128)
    assert len(grid["physical_times"][description["records"][0]["id"]]["prediction"]) == 12
    assert (
        grid["physical_times"][description["records"][0]["id"]]["prediction"][0]
        > grid["physical_times"][description["records"][0]["id"]]["history"][-1]
    )
    for index in (0, 15):
        x, y, *_ = reference[description["sample_indices"][index]]
        nx, ny = normalizer.preprocess(x, y)
        actual = read_sample(description["records"][index], description)
        torch.testing.assert_close(actual["input"], nx, rtol=0, atol=0)
        torch.testing.assert_close(actual["target"], ny, rtol=0, atol=0)


@pytest.mark.parametrize("field", ["neutron", "solid", "fluid"])
@pytest.mark.parametrize("split", ["decouple_val", "couple_val"])
def test_nt_native_reader_matches_reference(original, field, split):
    from ai4e_contrib.application.datasets.gencp.ntcouple import describe, read_sample
    from tools.verification.gencp.reference import nt_dataset

    root = Path("/Users/zonghui/work/project_simulation/dojo_train/gencp/raw/NTcouple")
    if not root.is_dir():
        pytest.skip("缺少原始核热数据")
    reference = nt_dataset(SOURCE, root, field, split)
    description = describe(root, "ntcouple", field, split, 16)
    for i in (0, 15):
        sample = read_sample(description["records"][i], description)
        torch.testing.assert_close(
            sample["input"], reference.cond[i].permute(1, 2, 3, 0), rtol=0, atol=0
        )
        torch.testing.assert_close(
            sample["target"], reference.target[i].permute(1, 2, 3, 0), rtol=0, atol=0
        )
