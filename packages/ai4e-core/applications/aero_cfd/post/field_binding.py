"""固定物理结果的单样本绑定；数组评价不加载网格或绘图库。"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from ai4e_core.abilities.data.validate.fingerprint import file_fingerprint, fingerprint
from ai4e_core.applications.aero_cfd.infer.results import read_sample


def _array(value):
    if hasattr(value, "detach"):
        value = value.detach().cpu().numpy()
    return np.array(value, copy=True)


def read_fields(reference: Any) -> dict:
    """读回一个固定样本或拷贝内存快照，验证身份、形状及有效性。"""
    if isinstance(reference, (str, Path)):
        reference = {"manifest": str(reference)}
    if "manifest" in reference:
        path = Path(reference["manifest"]).resolve()
        metadata = json.loads(path.read_text())
        files = [path]
        for name in metadata["filemap"].values():
            if Path(name).name != name:
                raise ValueError("结果成员路径越界")
            files.append(path.parent / name)
        for mesh in metadata.get("meshes", {}).values():
            name = mesh["path"]
            if Path(name).name != name:
                raise ValueError("网格成员路径越界")
            # 纯指标不读取网格内容，网格摘要在实际绑定时才登记。
        revisions = {str(p): file_fingerprint(p) for p in files}
        loaded = read_sample(path)
        result = {**loaded, "root": path.parent, "revisions": revisions}
        result["origin"] = reference.get(
            "origin", {"id": fingerprint({"manifest": str(path), "revision": revisions[str(path)]})}
        )
    else:
        from copy import deepcopy

        result = {**reference, "metadata": deepcopy(reference["metadata"])}
        result.setdefault("revisions", {})
        result.setdefault("origin", {"id": fingerprint(result["metadata"])})
    result["fields"] = {name: _array(value) for name, value in result["fields"].items()}
    arrays = result["fields"]
    for domain in result["metadata"]["domains"].values():
        ids = arrays[domain["ids"]]
        position = arrays[domain["position"]]
        if (
            ids.ndim != 1
            or not np.issubdtype(ids.dtype, np.integer)
            or len(np.unique(ids)) != len(ids)
            or position.shape != (len(ids), 3)
            or not np.isfinite(position).all()
        ):
            raise ValueError("实体身份必须唯一且与有限三维坐标对应")
        if domain.get("truth_ids") and not np.array_equal(ids, arrays[domain["truth_ids"]]):
            raise ValueError("预测与真值实体身份顺序不同")
        valid = (
            arrays[domain["validity"]] if domain.get("validity") else np.ones(len(ids), dtype=bool)
        )
        if valid.dtype != np.bool_ or valid.shape != (len(ids),):
            raise ValueError("有效性必须是逐实体布尔数组")
        for key in domain.get("targets", {}).values():
            prediction = arrays[key + ".prediction"]
            truth = arrays.get(key + ".truth")
            if (
                prediction.ndim != 2
                or len(prediction) != len(ids)
                or prediction.shape[1] < 1
                or not np.isfinite(prediction[valid]).all()
            ):
                raise ValueError("物理预测与实体或有效性不匹配")
            if truth is not None and (
                truth.shape != prediction.shape or not np.isfinite(truth[valid]).all()
            ):
                raise ValueError("预测与真值形状或有效性不匹配")
    verify_source(result)
    return result


def verify_source(sample: dict) -> None:
    """写出前再次验证固定来源，防止读写期间来源发生变化。"""
    for path, revision in sample.get("revisions", {}).items():
        if file_fingerprint(path) != revision:
            raise ValueError("固定结果来源发生变化: " + path)


def select_field(sample: dict, selection: Any) -> tuple:
    """解析领域、字段和显示类型；返回已绑定的实际数组名。"""
    parts = selection.split(":")
    if len(parts) != 3:
        raise ValueError("字段选择必须为 域:字段:类型")
    domain, field, variant = parts
    declaration = sample["metadata"]["domains"][domain]
    key = declaration["targets"][field]
    return domain, declaration, key, variant


def bind_mesh(sample: dict, *, domain: str, source_mesh: Any = None) -> Any:
    """使用已交付网格或显式原拓扑回贴，不构建模型或猜测拓扑。"""
    from ai4e_core.abilities.postproc.comparison import attach_valid_mesh
    from ai4e_core.abilities.postproc.visualization.fields import pyvista

    pv = pyvista()
    declaration = sample["metadata"]["domains"][domain]
    arrays = sample["fields"]
    ids = arrays[declaration["ids"]]
    positions = arrays[declaration["position"]]
    valid = (
        arrays[declaration["validity"]]
        if declaration.get("validity")
        else np.ones(len(ids), dtype=bool)
    )
    saved = sample["metadata"].get("meshes", {}).get(domain)
    if saved and sample.get("root"):
        mesh_path = sample["root"] / saved["path"]
        revision = file_fingerprint(mesh_path)
        mesh = pv.read(mesh_path)
        sample.setdefault("revisions", {})[str(mesh_path)] = revision
        verify_source(sample)
        if "original_point_id" not in mesh.point_data:
            raise ValueError("保存网格缺少原始点身份")
        mesh_ids = np.asarray(mesh.point_data["original_point_id"])
        lookup = {int(identity): row for row, identity in enumerate(ids)}
        if any(int(identity) not in lookup for identity in mesh_ids):
            raise ValueError("保存网格与预测身份不匹配")
        rows = np.asarray([lookup[int(identity)] for identity in mesh_ids])
        if not np.array_equal(np.asarray(mesh.points, dtype=positions.dtype), positions[rows]):
            raise ValueError("保存网格坐标与预测不一致")
        # 在副本中以固定数组为真源；仅保留全部顶点有效的单元。
        if not valid[rows].all():
            cells = [
                i for i in range(mesh.n_cells) if valid[rows[mesh.get_cell(i).point_ids]].all()
            ]
            mesh = mesh.extract_cells(cells)
            rows = np.asarray([lookup[int(i)] for i in mesh["original_point_id"]])
        for key in declaration["targets"].values():
            for suffix in (".prediction", ".truth"):
                if key + suffix in arrays:
                    mesh.point_data[key + suffix] = arrays[key + suffix][rows]
    else:
        source_mesh = (
            source_mesh if source_mesh is not None else sample.get("source_meshes", {}).get(domain)
        )
        if source_mesh is None:
            raise ValueError(f"{domain} 缺少完整拓扑；请显式交付网格")
        selected = {
            key + suffix: arrays[key + suffix][valid]
            for key in declaration["targets"].values()
            for suffix in (".prediction", ".truth")
            if key + suffix in arrays
        }
        mesh = pv.wrap(
            attach_valid_mesh(
                source_mesh,
                positions[valid],
                selected,
                source_ids=ids[valid] if declaration.get("identity_basis") == "source" else None,
            )
        )
        if domain == "surface":
            mesh = mesh.extract_surface()
    if not mesh.n_cells:
        raise ValueError("没有有效拓扑单元")
    mesh.field_data["post_domain"] = [domain]
    mesh.field_data["post_units"] = [json.dumps(declaration.get("units", {}))]
    mesh.field_data["post_coordinate_space"] = [json.dumps(declaration.get("coordinate_space"))]
    for key in declaration["targets"].values():
        if key + ".truth" not in mesh.point_data:
            continue
        p, t = np.asarray(mesh[key + ".prediction"]), np.asarray(mesh[key + ".truth"])
        mesh[key + ".difference"] = p - t
        if p.ndim == 2 and p.shape[1] > 1:
            mesh[key + ".vector_error"] = np.linalg.norm(p - t, axis=1)
            mesh[key + ".magnitude_difference"] = np.linalg.norm(p, axis=1) - np.linalg.norm(
                t, axis=1
            )
        else:
            mesh[key + ".absolute_error"] = np.abs(p - t)
    return mesh
