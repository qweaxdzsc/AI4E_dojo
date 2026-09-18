"""两骨干真实前向、梯度与单场生成的独立源码对照。"""

from pathlib import Path
from types import SimpleNamespace

import pytest
import torch
import yaml

from ai4e_contrib.ability.inference.gencp.velocity import single_field
from ai4e_contrib.ability.model.gencp.adapters import construct
from tools.verification.gencp.reference import construct as original_construct
from tools.verification.gencp.reference import load_reference

SOURCE = Path("/Users/zonghui/work/new_code_project/GenCP/GenCP")
ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize("backbone", ["cno", "sit_fno"])
@pytest.mark.parametrize(
    "dataset,field",
    [
        ("ntcouple", "neutron"),
        ("ntcouple", "solid"),
        ("ntcouple", "fluid"),
        ("turek_hron", "fluid"),
        ("turek_hron", "structure"),
        ("double_cylinder", "fluid"),
        ("double_cylinder", "structure"),
    ],
)
def test_forward_gradient_and_single_source(backbone, dataset, field):
    if not SOURCE.is_dir():
        pytest.skip("原仓库缺失不算对照通过")
    torch.set_num_threads(4)
    original = load_reference(SOURCE)
    cfg = yaml.safe_load((ROOT / f"examples/gencp/{dataset}_{backbone}/config.yaml").read_text())
    ours = construct(cfg["fields"][field]["model"])
    theirs = original_construct(original, dataset, backbone, field)
    theirs.load_state_dict(ours.state_dict())
    nt = dataset == "ntcouple"
    height, width = (
        (64, {"neutron": 20, "solid": 8, "fluid": 12}[field])
        if nt
        else ((108, 88) if dataset == "turek_hron" else (128, 128))
    )
    channels = {"neutron": 3, "solid": 4, "fluid": 5}[field] if nt else 4
    frames = 16 if nt else 12
    x = torch.randn(1, frames, height, width, channels)
    condition = None if nt else torch.randn(1, 3, height, width, 4)
    t = torch.tensor([0.4])
    a = ours(x, t, condition)
    b = theirs(x, t, condition)
    torch.testing.assert_close(a, b, rtol=1e-4, atol=1e-6)
    a.square().mean().backward()
    b.square().mean().backward()
    for pa, pb in zip(ours.parameters(), theirs.parameters()):
        if pa.grad is not None:
            torch.testing.assert_close(pa.grad, pb.grad, rtol=1e-4, atol=1e-6)
    outputs = {"neutron": 1, "solid": 1, "fluid": 4}[field] if nt else 4
    target = x[..., -outputs:] if nt else x
    condition = x[..., :-outputs] if nt else condition
    settings = SimpleNamespace(
        use_torchcfm=True,
        dataset_name=dataset if nt else dataset + "_data",
        stage=field,
        num_sampling_steps=3,
        use_clean_bc=True,
        use_clean_left_bc_for_solid=False,
        out_channels=outputs if nt else (3 if field == "fluid" else 1),
    )
    trainer = SimpleNamespace(model=theirs, args=settings, device="cpu")
    ours.eval()
    theirs.eval()
    with torch.no_grad():
        torch.manual_seed(43)
        expected = original["sample"](
            trainer, torch.randn_like(x), target, {"x0": condition, "cond": {}}, theirs
        )
        torch.manual_seed(43)
        actual = single_field(
            ours, condition, target, dataset=dataset, field=field, points=3, clean_solid=False
        )
    torch.testing.assert_close(actual, expected, rtol=1e-4, atol=1e-6)
