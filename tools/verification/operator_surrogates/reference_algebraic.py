"""独立上游代数参考：SciPy 分解/插值与 sklearn 回归，不导入 Dojo 数值实现。

POD 是本地独立装配的中心化加权数学参考，不冒称已复现 EZyRB 完整工程。
来源和运行时文件摘要由 source_identity 提供；这些函数不安排真实训练矩阵。
"""

import hashlib
import inspect
from importlib.metadata import version

import numpy as np
from scipy import linalg
from scipy.interpolate import RBFInterpolator as ScipyRBF
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import PolynomialFeatures


def source_identity() -> dict:
    """记录实际依赖版本、文件摘要和许可，避免将浮动分支当冻结版本。"""
    objects = {
        "scipy_svd": linalg.svd,
        "scipy_rbf": ScipyRBF,
        "sklearn_polynomial": PolynomialFeatures,
        "sklearn_regression": LinearRegression,
    }
    sources = {}
    for name, item in objects.items():
        path = inspect.getsourcefile(item)
        with open(path, "rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        sources[name] = {"path": path, "sha256": digest}
    return {
        "numpy": version("numpy"),
        "scipy": version("scipy"),
        "scikit_learn": version("scikit-learn"),
        "licenses": {
            "numpy": "BSD-3-Clause",
            "scipy": "BSD-3-Clause",
            "scikit-learn": "BSD-3-Clause",
        },
        "sources": sources,
        "pod_scope": "independent centered weighted SciPy SVD assembly, not EZyRB reproduction",
        "paper_reproduction": False,
    }


class ReferencePOD:
    """用上游 SciPy 分解独立构造固定的加权 POD 表示。"""

    def __init__(self, snapshots, rank, *, weights=None):
        x = np.asarray(snapshots, dtype=np.float64)
        self.weights = (
            np.ones(x.shape[1]) if weights is None else np.array(weights, dtype=np.float64)
        )
        self.mean = np.mean(x, axis=0)
        _, self.singular_values, right = linalg.svd(
            np.multiply(np.subtract(x, self.mean), np.sqrt(self.weights)),
            full_matrices=False,
            lapack_driver="gesvd",
        )
        self.basis = right[:rank].T / np.sqrt(self.weights)[:, None]

    def encode(self, values):
        """按独立拟合的均值/度量投影。"""
        return np.einsum(
            "...d,dr,d->...r", np.asarray(values) - self.mean, self.basis, self.weights
        )

    def decode(self, values):
        """独立重建；基方向可能与其他 SVD 实现符号或退化旋转不同。"""
        return np.einsum("...r,dr->...d", values, self.basis) + self.mean

    def reconstruct(self, values):
        """直接交付可比较的物理重建，避免误比奇异向量符号。"""
        return self.decode(self.encode(values))


class ReferenceRSM:
    """用 sklearn 特征及回归实现独立拟合，不消费 Dojo 基或系数。"""

    def __init__(self, inputs, targets, *, degree=2, ridge=0.0):
        self.polynomial = PolynomialFeatures(degree=degree, include_bias=True)
        features = self.polynomial.fit_transform(inputs)
        self.regression = (
            LinearRegression(fit_intercept=False)
            if ridge == 0
            else Ridge(alpha=ridge, fit_intercept=False, solver="svd")
        )
        self.regression.fit(features, np.asarray(targets).reshape(len(inputs), -1))

    def predict(self, inputs):
        """独立生成多项式后预测。"""
        return self.regression.predict(self.polynomial.transform(inputs))


def fit_pod(snapshots, rank, *, weights=None):
    """返回独立 POD 参考对象。"""
    return ReferencePOD(snapshots, rank, weights=weights)


def fit_rsm(inputs, targets, *, degree=2, ridge=0.0):
    """返回独立响应面参考对象。"""
    return ReferenceRSM(inputs, targets, degree=degree, ridge=ridge)


def fit_rbf(inputs, targets, *, smoothing=0.0, degree=1, kernel="cubic"):
    """返回上游 SciPy 插值器；调用对象直接预测，与生产方法名无需统一。"""
    return ScipyRBF(
        inputs,
        np.asarray(targets).reshape(len(inputs), -1),
        kernel=kernel,
        degree=degree,
        smoothing=smoothing,
    )
