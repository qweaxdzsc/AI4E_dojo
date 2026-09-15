"""当前 aero_cfd 的公开配置描述，仅做数据映射，不导入案例或算法。"""

SOURCES = {"surface": "quadpress_smpl.vtk", "volume": "hexvelo_smpl.vtk"}
OUTPUTS = {
    "surface_pressure": ("surface", "point:point_scalars"),
    "surface_position": ("surface", "geometry:points"),
    "surface_normals": ("surface", "derived:normals"),
    "volume_velocity": ("volume", "point:point_vectors"),
    "volume_position": ("volume", "geometry:points"),
    "volume_sdf": ("volume", "derived:nearest_distance"),
    "volume_normals": ("volume", "derived:nearest_direction"),
}


def partition_for(config):
    """读取已安装案例的公开 YAML 元数据；不加载其 Python 算法。"""
    from importlib.metadata import distribution

    import yaml

    dataset = config.get("dataset", {})
    if dataset.get("manifest") is not None:
        raise ValueError("dataset.manifest: 当前页面映射仅支持默认 ShapeNet-Car manifest")
    partition = dataset.get("partition", "official")
    if partition == "official":
        path = distribution("ai4e-contrib").locate_file(
            "ai4e_contrib/application/datasets/shapenet_car/partition.yaml"
        )
        partition = yaml.safe_load(path.read_text())
        partition.pop("expected", None)
    if (
        not isinstance(partition, dict)
        or not partition
        or set(partition) - {"train", "eval", "test"}
    ):
        raise ValueError("dataset.partition: 首期支持官方名单或任务已有显式分片映射")
    seen = set()
    for group, names in partition.items():
        if not isinstance(names, list):
            raise ValueError("dataset.partition." + group + ": 需要列表")  # noqa: TRY004 - 统一业务输入错误
        for name in names:
            if not isinstance(name, str) or name in seen:
                raise ValueError("dataset.partition: 非法或重复样本")
            seen.add(name)
    return partition


def require_profile(service, project, identity):
    """校验已登记脚本的处理语义，兼容格式整理和已审定的旧默认加载入口。"""
    from pathlib import Path

    import ai4e_task as task

    from .recipe_profile import compatible_file

    record = task.get_task(service.project(project), identity)
    folder = Path(record["directory"]) / "recipe"
    if record.get("entry", {}).get("platform_case"):
        from ..tasks.templates import case_files

        files = case_files(service, record["entry"]["platform_case"])
    else:
        source = service.settings.template
        files = {
            str(path.relative_to(source)): path.read_bytes()
            for path in source.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
    expected = {name for name in files if Path(name).suffix == ".py" or name == "task-entry.json"}
    actual = {
        str(path.relative_to(folder))
        for path in folder.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and (path.suffix == ".py" or path.name == "task-entry.json")
    }
    import json

    from .recipe_profile import compatible_legacy, compatible_native

    if compatible_legacy(
        folder,
        actual,
        service.settings.template / "legacy-profile.json",
        record.get("entry", {}).get("platform_case"),
        json.loads(files["task-entry.json"]).get("components"),
    ):
        return
    if compatible_native(folder, actual, service.settings.template / "inference-profile.json",
                         record.get("entry", {}).get("platform_case"), json.loads(files["task-entry.json"]).get("components")):
        return
    changed = sorted(expected ^ actual)
    for name in sorted(expected & actual):
        target = folder / name
        if not compatible_file(name, files[name], target.read_bytes()):
            changed.append(name)
    if changed:
        raise ValueError(
            "recipe_profile_changed: 以下文件的处理逻辑或入口与已支持版本不同，需要核对页面配置映射："
            + ", ".join(sorted(changed))
        )
