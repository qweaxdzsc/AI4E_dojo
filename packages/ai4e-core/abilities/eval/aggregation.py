"""逐样本等权统计；不改变历史全元素累计指标。"""

import numpy as np


def summarize(values: list[float | None], *, expected: int, failed: int = 0) -> dict:
    """保留有效、不可定义和缺失数量，P90采用线性插值。"""
    valid = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=np.float64)
    return {
        "mean": float(valid.mean()) if len(valid) else None,
        "median": float(np.median(valid)) if len(valid) else None,
        "p90": float(np.quantile(valid, 0.9, method="linear")) if len(valid) else None,
        "max": float(valid.max()) if len(valid) else None,
        "valid": len(valid),
        "undefined": len(values) - len(valid),
        "failed": failed,
        "expected": expected,
        "completed": len(values),
        "complete": len(values) == expected and failed == 0,
        "statistic": "equal_sample_distribution",
        "algorithm": "sample-statistics-v1",
    }
