"""固定数组指标数值与失败语义，不用模型烟测代替。"""

import numpy as np
import pytest

from ai4e_core.abilities.eval.result_metrics import evaluate_arrays


def test_scalar_five_metrics():
    value = evaluate_arrays([[2], [4], [6]], [[1], [2], [3]])
    assert value["values"] == pytest.approx(
        {"mse": 14 / 3, "rmse": np.sqrt(14 / 3), "mae": 2, "relative_l2": 1, "r2": -6}
    )
    assert value["count"] == 3 and value["excluded"] == 0


def test_vector_component_magnitude_and_validity():
    p, t = [[3, 4], [np.nan, 1]], [[0, 5], [1, 2]]
    valid = np.array([True, False])
    assert evaluate_arrays(p, t, component="magnitude", mask=valid)["values"]["mse"] == 0
    assert evaluate_arrays(p, t, component="0", mask=valid)["values"]["mse"] == 9
    assert evaluate_arrays(p, t, component="1", mask=valid)["excluded"] == 1


@pytest.mark.parametrize(
    "p,t,kw",
    [
        ([[1]], [[1], [2]], {}),
        ([[float("nan")]], [[1]], {}),
        ([], [], {}),
        ([[1, 2]], [[1, 2]], {"component": "8"}),
        ([[1]], [[1]], {"mask": np.array([False])}),
        ([[1]], [[1]], {"mask": np.array([1])}),
        ([[1]], [[1]], {"metrics": ["fake"]}),
    ],
)
def test_invalid_inputs(p, t, kw):
    with pytest.raises((ValueError, TypeError)):
        evaluate_arrays(p, t, **kw)


def test_undefined_zero_denominators():
    value = evaluate_arrays([[0], [0]], [[0], [0]])
    assert value["values"]["relative_l2"] is None and value["values"]["r2"] is None
    assert value["undefined"] == {"relative_l2": "真值范数为零", "r2": "真值恒定"}


def test_tensor_headers_preserve_vector_without_old_metrics(tmp_path, monkeypatch):
    import json

    import torch

    from ai4e_core.applications.aero_cfd.post import describe_result_fields

    for name in ("prediction", "truth"):
        torch.save(torch.ones(4, 3), tmp_path / (name + ".pt"))
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "filemap": {"v.prediction": "prediction.pt", "v.truth": "truth.pt"},
                "domains": {"surface": {"targets": {"velocity": "v"}}},
            }
        )
    )
    load = torch.load

    def inspect(*args, **kwargs):
        value = load(*args, **kwargs)
        assert value.untyped_storage().device.type == "meta"
        return value

    monkeypatch.setattr(torch, "load", inspect)
    assert describe_result_fields([str(manifest)])[str(manifest)]["components"] == {"v": 3}


def test_constant_decimal_truth_r2_is_undefined():
    """小数常量的求和舍入不能形成虚假真值方差。"""
    import numpy as np

    from ai4e_core.abilities.eval.result_metrics import evaluate_arrays

    result = evaluate_arrays(np.ones((1331, 1)), np.full((1331, 1), 0.9), metrics=["r2"])
    assert result["values"]["r2"] is None and result["undefined"]["r2"] == "真值恒定"
