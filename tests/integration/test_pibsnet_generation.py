"""五生成器的独立生产、完整清单及解析/积分交叉验证。"""

import numpy as np
import pytest
from scipy.integrate import quad

from ai4e_contrib.application.datasets.convection_diffusion.generate import truth
from ai4e_contrib.application.datasets.parametric import CASES, Dataset, component


@pytest.mark.parametrize("case", list(CASES))
def test_independent_generation(case, tmp_path):
    cfg = {"output": str(tmp_path / case), "train": 1, "test": 1, "nx": 9, "nt": 5}
    if case == "diffusion_trapezoid":
        cfg["nt"] = 201
        cfg["ny"] = 9
    manifest = component(case).generate(cfg)
    dataset = Dataset(manifest)
    assert dataset.read(dataset.records("train")[0])["case"] == case
    assert len(dataset.records("test")) == 1
    with pytest.raises(FileExistsError):
        component(case).generate(cfg)


def test_first_passage_cdf_matches_source_integral():
    for x, t, a, lam in [(-1.0, 0.4, 1.0, 0.5), (-3.0, 4.0, 2.0, 1.5), (0.0, 2.0, 2.0, 0.0)]:
        expected = quad(
            lambda s, a=a, x=x, lam=lam: (
                (a - x) / np.sqrt(2 * np.pi * s**3) * np.exp(-(((a - x) - lam * s) ** 2) / (2 * s))
            ),
            0,
            t,
        )[0]
        assert truth(x, t, a=a, lam=lam) == pytest.approx(expected, abs=1e-10)
