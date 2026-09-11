"""读取 HDF5 字段目录；不把多样本重复场展开成整表，也不加载数组。"""

from pathlib import Path

from .mesh import inspect_mesh


def is_vtkhdf(path: Path) -> bool:
    """仅根据根组判断 VTKHDF，不根据扩展名猜测。"""
    import h5py

    with h5py.File(path, "r") as source:
        return "VTKHDF" in source


def _field(name: str, dataset) -> dict:
    shape = list(dataset.shape)
    return {
        "id": name,
        "name": name.rsplit("/", 1)[-1],
        "association": "array",
        "shape": shape,
        "dtype": str(dataset.dtype),
        "components": int(shape[-1]) if len(shape) > 1 else 1,
    }


def _datasets(group):
    return sorted(
        name
        for name, item in group.items()
        if hasattr(item, "shape") and not hasattr(item, "keys")
    )


def inspect_hdf5(path: Path) -> dict:
    """列出数据集元数据。VTKHDF 走网格检查；同构样本组只报告一份字段。"""
    import h5py

    if is_vtkhdf(path):
        return inspect_mesh(path, reader="vtkhdf")
    with h5py.File(path, "r") as source:
        children = list(source)
        groups = [source[name] for name in children if hasattr(source[name], "keys")]
        if children and len(groups) == len(children):
            first = _datasets(groups[0])
            if first and all(_datasets(group) == first for group in groups):
                return {
                    "kind": "tensor",
                    "fields": [_field(name, groups[0][name]) for name in first],
                }
        fields = []

        def visit(name, item):
            if hasattr(item, "shape") and not hasattr(item, "keys"):
                fields.append(_field(name, item))

        source.visititems(visit)
    if not fields:
        raise ValueError("empty_tensor_store")
    return {"kind": "tensor", "fields": fields}


def read_hdf5_array(path: Path, field: str | None = None):
    """只读取一个数据集；同构样本组缺路径时取第一个样本。"""
    import h5py
    import numpy as np

    with h5py.File(path, "r") as source:
        if field and field in source and hasattr(source[field], "shape"):
            return np.asarray(source[field])
        children = [name for name in source if hasattr(source[name], "keys")]
        groups = [source[name] for name in children]
        if children and all(_datasets(group) == _datasets(groups[0]) for group in groups):
            name = field or _datasets(groups[0])[0]
            if name in groups[0]:
                return np.asarray(groups[0][name])
        if field:
            raise ValueError("unknown_field")
        datasets = []

        def visit(name, item):
            if hasattr(item, "shape") and not hasattr(item, "keys"):
                datasets.append(name)

        source.visititems(visit)
        if not datasets:
            raise ValueError("empty_tensor_store")
        return np.asarray(source[datasets[0]])
