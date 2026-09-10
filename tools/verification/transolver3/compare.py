"""固定容差逐元素比较；不允许非有限值或以平均值掩盖局部超差。"""

import numpy as np

RTOL = 1e-5
ATOL = 1e-6


def compare(actual, expected, *, identity):
    """报告形状、类型、最大误差、全部超差数量及首个位置。"""
    actual, expected = np.asarray(actual), np.asarray(expected)
    report = {
        "identity": identity,
        "rtol": RTOL,
        "atol": ATOL,
        "actual_shape": list(actual.shape),
        "expected_shape": list(expected.shape),
    }
    if actual.shape != expected.shape or actual.dtype != expected.dtype:
        return {**report, "passed": False, "reason": "shape_or_dtype"}
    if actual.dtype.kind not in "biufc":
        close = actual == expected
        error = np.zeros(actual.shape)
    elif actual.dtype.kind in "biu":
        close = actual == expected
        error = np.abs(actual.astype(np.float64) - expected.astype(np.float64))
    else:
        finite = np.isfinite(actual) & np.isfinite(expected)
        close = finite & np.isclose(actual, expected, rtol=RTOL, atol=ATOL, equal_nan=False)
        with np.errstate(invalid="ignore"):
            error = np.abs(actual.astype(np.complex128) - expected.astype(np.complex128))
    bad = np.argwhere(~close)
    maximum = float(error.max()) if error.size else 0.0
    return {
        **report,
        "passed": bool(close.all()),
        "mismatch_count": int((~close).sum()),
        "max_absolute_error": maximum if np.isfinite(maximum) else None,
        "first_mismatch": bad[0].tolist() if len(bad) else None,
    }


def require(actual, expected, *, identity):
    """比较失败即拒绝该项验收。"""
    report = compare(actual, expected, identity=identity)
    if not report["passed"]:
        raise AssertionError(report)
    return report
