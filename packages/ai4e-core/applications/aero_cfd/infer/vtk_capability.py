"""推理 VTK 导出能力：点云始终可写，网格化取决于当次是否真有来源拓扑。"""

from __future__ import annotations

from pathlib import Path

VTK_MESH_SUFFIXES = {".vtk", ".vtp", ".vtu", ".vtkhdf", ".vtkh5", ".vts", ".vti", ".vtr"}
STRUCTURED_SUFFIXES = {".vts", ".vti", ".vtr"}
VTKHDF_SUFFIXES = {".vtkhdf", ".vtkh5"}
MESH_UNAVAILABLE = "训练集没有可还原的 VTK 网格"


def describe_vtk_exports(config: dict | None = None, *, dataset_component=None) -> dict:
    """告诉页面和装配：点云能否写、网格化能否还原，默认都带真值。

    点云只需要已保存的锚点坐标和场，不依赖原始拓扑。网格化只认清单里的
    VTK/VTKHDF 来源文件名，或配置里已经绑定的连接关系路径；空槽位和原始
    处理 VTKHDF 输出开关不能单独让网格化可勾。
    """
    config = config if isinstance(config, dict) else {}
    pointcloud = {"available": True, "include_truth": True, "reason": None}
    mesh = _mesh_restore(config, dataset_component)
    return {"pointcloud": pointcloud, "mesh": mesh}


def mesh_export_available(config: dict | None = None, *, dataset_component=None) -> bool:
    """网格化导出是否可用；页面置灰和装配跳过共用这一判断。"""
    return bool(
        describe_vtk_exports(config, dataset_component=dataset_component)["mesh"]["available"]
    )


def _mesh_restore(config: dict, dataset_component) -> dict:
    profile = _profile(config, dataset_component)
    files = profile.get("source_files") if isinstance(profile.get("source_files"), dict) else {}
    suffixes = {Path(str(name)).suffix.lower() for name in files.values() if name}
    dataset = config.get("dataset") if isinstance(config.get("dataset"), dict) else {}
    connectivity = dataset.get("connectivity_h5") or dataset.get("connectivity")
    bound = isinstance(connectivity, str) and bool(connectivity.strip())
    sources: list[str] = []
    if suffixes & VTK_MESH_SUFFIXES:
        sources.append("source_vtk")
    if suffixes & VTKHDF_SUFFIXES:
        sources.append("vtkhdf")
    if bound:
        sources.append("connectivity")
    has_comparison = dataset_component is not None and callable(
        getattr(dataset_component, "comparison_mesh", None)
    )
    if has_comparison and sources:
        sources.append("comparison_mesh")
    structured = bool(suffixes & STRUCTURED_SUFFIXES)
    if sources:
        return {
            "available": True,
            "include_truth": True,
            "structured": structured,
            "reason": None,
            "sources": sources,
        }
    return {
        "available": False,
        "include_truth": True,
        "structured": False,
        "reason": MESH_UNAVAILABLE,
        "sources": [],
    }


def _profile(config: dict, dataset_component) -> dict:
    if dataset_component is not None and hasattr(dataset_component, "describe_rawprep"):
        try:
            profile = dataset_component.describe_rawprep(config)
        except (OSError, ValueError, TypeError, KeyError):
            profile = {}
        return profile if isinstance(profile, dict) else {}
    return {}
