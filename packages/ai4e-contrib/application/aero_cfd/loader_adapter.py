"""旧外流加载器的显式适配；通用 run 不解释业务配置。"""

from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from omegaconf import OmegaConf

from ai4e_core.applications.aero_cfd.rawprep import resolved_workers
from ai4e_core.base.config import load_config
from ai4e_core.run.session import bind_adapted_workers


def load_user_configuration(config_loader, path, overrides=None):
    """只为旧外流案例隔离新增并行参数，保留配置文件相对目录。"""
    merged = OmegaConf.to_container(OmegaConf.create(load_config(path, overrides)), resolve=False)
    raw = merged.get("rawprep")
    if not isinstance(raw, dict) or not ({"workers", "formats"} & raw.keys()):
        bind_adapted_workers(None)
        return config_loader(path, overrides)
    workers = resolved_workers({"workers": raw.get("workers", 1)})
    stripped = deepcopy(merged)
    stripped["rawprep"].pop("workers", None)
    formats = stripped["rawprep"].pop("formats", None)
    if formats is not None:
        if (
            not isinstance(formats, list)
            or not formats
            or any(x not in {"pt", "zarr"} for x in formats)
        ):
            raise ValueError("rawprep.formats 必须为非空 PT/Zarr 列表")
        stripped["rawprep"]["format"] = formats[0]
    origin = Path(path).resolve()
    temporary = origin.with_name(f".dojo-load-{origin.stem}-{uuid4().hex}.yaml")
    try:
        OmegaConf.save(OmegaConf.create(stripped), temporary)
        loaded = config_loader(str(temporary), None)
    finally:
        temporary.unlink(missing_ok=True)
    bind_adapted_workers(workers)
    loaded = OmegaConf.create(loaded)
    if formats is not None:
        loaded.rawprep.pop("format", None)
        loaded.rawprep.formats = formats
    return loaded
