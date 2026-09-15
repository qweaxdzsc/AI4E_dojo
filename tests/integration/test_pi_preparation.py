"""物理点集、边界条件、配置拒绝和恢复链路的联合测试。"""

import pytest
import torch

from ai4e_contrib.application.datasets.parametric import Dataset, component
from ai4e_core.abilities.constraint.physical import boundary_residual
from ai4e_core.abilities.sampling.physical import periodic_points, sample_points
from tests.integration.test_pibsnet_training import configuration, configuration_for, run_stages


def test_sampling_identity_normals_and_pairing(tmp_path):
    path = component("neumann_diffusion").generate(
        {"output": str(tmp_path / "data"), "train": 1, "test": 1, "nx": 11, "nt": 9}
    )
    dataset = Dataset(path)
    sample = dataset.read(dataset.records("train")[0])
    cfg = {"method": "random_without_replacement", "num_points": 12}
    first = sample_points(sample, cfg, seed=7, name="data", supervised=True)
    second = sample_points(sample, cfg, seed=7, name="data", supervised=True)
    torch.testing.assert_close(first["target"], sample["u"].flatten()[first["indices"]])
    torch.testing.assert_close(first["points"], second["points"])
    left = sample_points(
        sample, {"method": "uniform", "num_points": 7}, seed=7, name="left", boundary="left"
    )
    assert torch.all(left["normals"] == -1)
    assert torch.all(left["points"][:, 1] == 0)
    pair = periodic_points(
        sample,
        {"method": "uniform", "num_pairs": 7},
        seed=7,
        name="periodic",
        boundaries=["left", "right"],
    )
    torch.testing.assert_close(pair["points"][:, 0], pair["paired_points"][:, 0])
    assert torch.all(pair["paired_points"][:, 1] == 1)
    with pytest.raises(ValueError, match="监督采样"):
        sample_points(
            sample, {"method": "uniform", "num_points": 7}, seed=7, name="bad", supervised=True
        )


def test_boundary_sign_and_target_shape():
    u = torch.ones(3)
    residual = boundary_residual(
        value=u,
        gradient=torch.ones(3, 1) * 2,
        normals=-torch.ones(3, 1),
        condition={"type": "fixed_gradient", "gradient": -2.0},
    )
    assert torch.all(residual == 0)
    with pytest.raises(ValueError, match="形状"):
        boundary_residual(
            value=u,
            gradient=None,
            normals=None,
            condition={"type": "fixed_value", "value": torch.zeros(3, 1)},
        )


def test_formal_pde_sampling_includes_original_full_grid():
    import numpy as np

    sample = component("neumann_diffusion").make_sample(
        np.random.default_rng(42), {"nx": 9, "nt": 7}, index=0, split="train"
    )
    sample.update(id="train-0", case="neumann_diffusion")
    full = sample_points(
        sample, {"method": "all", "include_boundary": True}, seed=42, name="interior"
    )
    interior = sample_points(sample, {"method": "all"}, seed=42, name="interior")
    assert len(full["points"]) == 9 * 7
    assert len(interior["points"]) == 7 * 6


@pytest.mark.parametrize("case", ["neumann_diffusion", "advection"])
def test_resume_and_stale_preparation(tmp_path, case):
    component(case).generate(
        {"output": str(tmp_path / "data"), "train": 2, "test": 1, "nx": 9, "nt": 7}
    )
    cfg = configuration_for(case, tmp_path)
    cfg["train"]["max_epochs"] = 1
    assert run_stages(cfg, ["trainprep", "train"]) == 0
    first = next((tmp_path / "runs").glob("*/checkpoints/last.pt"))
    cfg["train"].update(max_epochs=2, resume=str(first))
    assert run_stages(cfg, ["train"]) == 0
    resumed = max(
        (tmp_path / "runs").glob("*/checkpoints/last.pt"), key=lambda p: p.stat().st_mtime_ns
    )
    actual = torch.load(resumed, weights_only=False)["model"]
    cfg["train"]["resume"] = None
    assert run_stages(cfg, ["train"]) == 0
    uninterrupted = max(
        (tmp_path / "runs").glob("*/checkpoints/last.pt"), key=lambda p: p.stat().st_mtime_ns
    )
    expected = torch.load(uninterrupted, weights_only=False)["model"]
    for key in actual:
        torch.testing.assert_close(actual[key], expected[key], rtol=0, atol=0)
    cfg["model"]["sampling"]["seed"] = 123
    assert run_stages(cfg, ["train"]) == 1


@pytest.mark.parametrize(
    "override",
    [
        "sampling.seed=5",
        "trainprep.sampling.seed=5",
        "model.boundary_conditions.left.u.value=2",
        "train.gradient_clip=0",
        "model.unknown=1",
    ],
)
def test_all_overrides_validated(tmp_path, override):
    file = tmp_path / "config.yaml"
    file.write_text("case: neumann_diffusion\n")
    with pytest.raises(ValueError):
        configuration.load_configuration(file, [override])
