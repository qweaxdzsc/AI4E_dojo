"""五案例真实阶段短训、独立预测及更新恢复，不替代正式精度验收。"""

import importlib.util
from pathlib import Path

import pytest
import torch

from ai4e_contrib.application.datasets.parametric import CASES, component
from ai4e_core.applications import parametric_pde
from ai4e_core.run.session import run_recipe
from ai4e_core.run.training import TrainingRun

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "pde_configuration", ROOT / "recipes/parametric_pde/configuration.py"
)
configuration = importlib.util.module_from_spec(spec)
spec.loader.exec_module(configuration)


def configuration_for(case, root):
    cfg = configuration.defaults(case)
    cfg["dataset"]["manifest"] = str(root / "data/manifest.json")
    cfg["run_root"] = str(root / "runs")
    cfg["trainprep"]["output"] = str(root / "prepared")
    cfg["post"]["output"] = str(root / "predictions")
    cfg["model"].update(
        control_points=[5] * (3 if case == "diffusion_trapezoid" else 2), degree=3, hidden_dim=8
    )
    cfg["train"].update(max_epochs=2, device="cpu", precision="fp64", log_every=1, snapshot=False)
    return cfg


def run_stages(cfg, names):
    components = configuration.components(cfg)

    def stage(name, config):
        if name == "infer":
            cfg["post"]["checkpoint"] = str(
                max(
                    Path(cfg["run_root"]).glob("*/checkpoints/last.pt"),
                    key=lambda p: p.stat().st_mtime_ns,
                )
            )
        result = getattr(parametric_pde, name)(cfg, **components, session=TrainingRun())
        if name == "infer":
            cfg["post"]["results"] = result["results"]
        return result

    return run_recipe(
        cfg,
        stages={name: lambda c, name=name: stage(name, c) for name in names},
        only=names,
        script=str(ROOT / "recipes/parametric_pde/pipeline.py"),
    )


@pytest.mark.parametrize("case", list(CASES))
def test_five_cases_real_short_training(case, tmp_path):
    gen = {"output": str(tmp_path / "data"), "train": 2, "test": 1, "nx": 9, "nt": 7}
    if case == "diffusion_trapezoid":
        gen["nt"] = 201
        gen["ny"] = 7
    component(case).generate(gen)
    cfg = configuration_for(case, tmp_path)
    assert run_stages(cfg, ["rawprep", "trainprep", "train", "infer", "post"]) == 0
    assert (tmp_path / "predictions/predictions.json").exists()
    ckpt = next((tmp_path / "runs").glob("*/checkpoints/last.pt"))
    state = torch.load(ckpt, weights_only=False)
    assert state["updates"] == (2 if cfg["train"]["update_group"] == "epoch_sum" else 4)


def test_native_no_clip_sum_accumulation_matches_one_update():
    from copy import deepcopy

    from ai4e_core.abilities.training.optimization import update

    torch.manual_seed(9)
    reference = torch.nn.Linear(2, 1).double()
    actual = deepcopy(reference)
    batches = [torch.randn(4, 2, dtype=torch.float64) for _ in range(3)]
    a = torch.optim.Adam(reference.parameters(), lr=0.001)
    b = torch.optim.Adam(actual.parameters(), lr=0.001)
    a.zero_grad()
    sum(reference(x).square().mean() for x in batches).backward()
    a.step()
    for i, batch in enumerate(batches):
        update(
            actual,
            b,
            lambda m, x: {"loss": m(x).square().mean()},
            batch,
            clip=None,
            accumulate=3,
            accumulation_reduction="sum",
            accum_index=i,
        )
    for p, q in zip(reference.parameters(), actual.parameters()):
        torch.testing.assert_close(p, q, rtol=1e-13, atol=1e-14)
