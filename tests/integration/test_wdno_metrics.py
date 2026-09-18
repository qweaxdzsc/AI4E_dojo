"""固定数组重算保护初帧排除、身份和不完整结果门禁。"""

import numpy as np
import pytest

from tools.verification.wdno.report import check_arrays


def test_original_mse_excludes_first_frame_and_rejects_missing_identity():
    truth = np.zeros((2, 81, 120), dtype=np.float32)
    prediction = np.ones_like(truth)
    prediction[:, 0] = 100
    arrays = {
        "ids": np.array([3, 7]),
        "target": truth,
        "prediction": prediction,
        "forcing": np.zeros((2, 80, 120)),
        "mse": np.ones(2),
    }
    assert check_arrays(arrays, [3, 7])["mse"] == 1
    with pytest.raises(ValueError, match="名单"):
        check_arrays(arrays, [7, 3])
    arrays["mse"] = np.array([2, 2])
    with pytest.raises(ValueError, match="MSE"):
        check_arrays(arrays, [3, 7])


def test_nonfinite_fixed_prediction_is_not_a_successful_metric():
    values = np.zeros((1, 81, 120), dtype=np.float32)
    values[0, 1, 0] = np.nan
    arrays = {
        "ids": np.array([1]),
        "target": np.zeros_like(values),
        "prediction": values,
        "forcing": np.zeros((1, 80, 120)),
        "mse": np.zeros(1),
    }
    with pytest.raises(ValueError, match="非有限"):
        check_arrays(arrays, [1])
