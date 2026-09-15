"""平台公共能力目录；数据集字段由任务的真实检查提供。"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/capabilities")
def capabilities():
    """描述平台已接入能力；具体任务的字段和限制从任务接口查询。"""
    return {
        "stages": ["rawprep", "trainprep", "model", "train", "infer", "post"],
        "execution_stages": ["rawprep", "trainprep", "train", "infer", "post"],
        "inference": {"batch": True, "scope": "task", "max_active_children_per_task": 1},
        "parallelism": 1,
        "output_formats": ["pt", "zarr"],
        "additional_outputs": ["vtkhdf"],
        "sources": {},
        "outputs": {},
        "field_catalog_scope": "task_dataset",
        "formats": [
            "vtk",
            "vtp",
            "vtu",
            "vtkhdf",
            "vtkh5",
            "vti",
            "vts",
            "vtr",
            "vtm",
            "h5",
            "hdf5",
            "npy",
            "pt",
            "zarr",
            "txt",
            "csv",
            "json",
            "yaml",
            "yml",
            "log",
            "md",
            "py",
        ],
        "unsupported": ["batch", "queue", "parallel_execution", "remote_execution"],
    }
