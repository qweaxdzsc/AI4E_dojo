"""固定预测 FP64 独立复算与六场误差保存；本地科学后处理组件。"""

import numpy as np
from local_data import read_record

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays


def fixed_errors(results, output):
    """数组读回后独立核验主指标，不调用候选代码。"""
    record = read_record(results)
    _, arrays = read_arrays(record["arrays"], kind="rmhd-validation-predictions-v1")
    prediction = np.asarray(arrays["prediction"], dtype=np.float64)
    target = np.asarray(arrays["target"], dtype=np.float64)
    denominator = np.sqrt((target * target).sum(axis=(1, 3, 4)))
    if not np.all(denominator > 0):
        raise ValueError("存在零真值范数")
    error = np.sqrt(((prediction - target) ** 2).sum(axis=(1, 3, 4))) / denominator
    np.testing.assert_allclose(error, record["rows"], rtol=1e-12, atol=1e-14)
    path = save_arrays(
        output / "field-errors",
        {"relative_l2": error},
        kind="rmhd-diagnostics-v1",
        metadata={"source": str(results)},
    )
    return {
        "arrays": path,
        "recomputed_mean_relative_l2": float(error.mean()),
        "windows": len(error),
    }
