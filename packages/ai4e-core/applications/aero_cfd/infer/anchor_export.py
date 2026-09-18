"""按样本提交锚点预测张量，并按开关附加点云。"""

from pathlib import Path

from ai4e_core.abilities.data.save.store import write_named_tensors, write_tensor_file
from ai4e_core.abilities.postproc.export.pointcloud import write_pointcloud

ANCHOR_FILEMAP = {
    "surface_pressure": "surface_pressure.pt",
    "volume_velocity": "volume_velocity.pt",
    "surface_anchor_position": "surface_anchor_position.pt",
    "volume_anchor_position": "volume_anchor_position.pt",
}


def save_anchor_sample(
    dest: str | Path,
    payloads: dict,
    *,
    overwrite: bool = False,
    export_vtk: bool = False,
    on_commit=None,
):
    """把一个样本的物理预测和归一化锚点坐标写入数据目录。

    点云写入同目录的 ``surface.vtp`` / ``volume.vtp``，没有原始网格单元。
    """
    extra = {}
    if export_vtk:
        extra["surface.vtp"] = lambda path, data=payloads: write_pointcloud(
            path,
            data["surface_anchor_position"],
            {
                key: data[key]
                for key in ("surface_pressure", "surface_pressure.prediction", "surface_pressure.truth")
                if key in data
            }
            or {"surface_pressure": data["surface_pressure"]},
        )
        extra["volume.vtp"] = lambda path, data=payloads: write_pointcloud(
            path,
            data["volume_anchor_position"],
            {
                key: data[key]
                for key in ("volume_velocity", "volume_velocity.prediction", "volume_velocity.truth")
                if key in data
            }
            or {"volume_velocity": data["volume_velocity"]},
        )
    result = write_named_tensors(
        dest, payloads, ANCHOR_FILEMAP, overwrite=overwrite, extra_writers=extra
    )

    if on_commit:
        on_commit(dest)
    return result


def save_reference_sample(
    root, index: int, payloads: dict, *, overwrite=False, export_vtk=False, on_commit=None
):
    """按测试顺序交付兼容的单样本张量包与 VTK 路径，编号由流程生成。"""
    root = Path(root)
    stem = f"sample_{index:04d}"
    path = root / f"{stem}.pt"
    if export_vtk:
        for domain in ("surface", "volume"):
            target = root / "vtk" / f"{stem}_{domain}.vtp"
            if target.exists() and not overwrite:
                raise FileExistsError(str(target))
    write_tensor_file(path, payloads, overwrite=overwrite)
    if on_commit:
        on_commit(path)
    if export_vtk:
        for domain in ("surface", "volume"):
            key = f"{domain}_anchor_position"
            write_pointcloud(
                root / "vtk" / f"{stem}_{domain}.vtp",
                payloads[key],
                {k: v for k, v in payloads.items() if k.startswith(domain + "_") and k != key},
            )
            if on_commit:
                on_commit(root / "vtk" / f"{stem}_{domain}.vtp")
    return path
