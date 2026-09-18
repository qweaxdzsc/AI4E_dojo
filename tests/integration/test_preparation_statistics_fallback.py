"""原生物理清单无统计文件时，沿用按训练样本拟合的数值口径。"""

from pathlib import Path
from typing import ClassVar

import pytest
import torch

from ai4e_core.applications.aero_cfd.trainprep.normalization import bind_normalization


class Index:
    partitions: ClassVar[dict] = {"train": ["first", "second"]}
    path = Path("/unused/manifest.json")

    def read(self, split, row, fields):
        assert split == "train"
        return {name: torch.tensor([[1., 3.], [5., 7.]]) + row * 8 for name in fields}


def test_fit_missing_statistics_and_preserve_explicit_failure(tmp_path):
    import json

    cfg = {"normalization": {"execute": True, "fields": {
        "positions": {"method": "coordinate"}, "velocity": {"method": "zscore"},
    }}}
    result = bind_normalization(cfg, {}, Index()).record["fields"]
    assert result["positions"]["parameters"]["minimum"] == [1.]
    assert result["positions"]["parameters"]["maximum"] == [15.]
    assert result["positions"]["parameters"]["check_range"] is False
    expected = torch.tensor([[1., 3.], [5., 7.], [9., 11.], [13., 15.]], dtype=torch.float64)
    torch.testing.assert_close(torch.tensor(result["velocity"]["parameters"]["mean"], dtype=torch.float64), expected.mean(0))
    torch.testing.assert_close(torch.tensor(result["velocity"]["parameters"]["std"], dtype=torch.float64), expected.std(0, correction=0))
    stats = tmp_path / "stats.json"
    stats.write_text(json.dumps({"unrelated": 1}))
    cfg["normalization"]["statistics"] = str(stats)
    with pytest.raises(KeyError):
        bind_normalization(cfg, {}, Index())
