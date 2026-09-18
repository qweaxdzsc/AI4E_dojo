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
    if config.get("inputs", {}).get("rawprep", {}).get("manifest") is not None:
        raise ValueError("dataset.manifest: 当前页面映射仅支持默认 ShapeNet-Car manifest")
    partition = dataset.get("partitions", "official")
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
    """确认任务已接入页面描述操作；不限制用户脚本或新增能力文件。"""
    from pathlib import Path

    import ai4e_task as task

    record = task.get_task(service.project(project), identity)
    task.operation_target(Path(record["directory"]) / "recipe", "inspect")
