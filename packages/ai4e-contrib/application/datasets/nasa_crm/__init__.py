"""NASA CRM 来源、分片与按需读取适配。"""

from .adapter import RawDataset, View, manifest_digest
from .topology import reconstruct_surface_topology

SOURCE_PATH_FIELDS = ("train_h5", "test_h5", "connectivity_h5")

__all__ = [
    "SOURCE_PATH_FIELDS",
    "RawDataset",
    "View",
    "manifest_digest",
    "reconstruct_surface_topology",
]

from .physical import LAYOUT, comparison_mesh, open_physical, physical_fields

__all__ += ["LAYOUT", "comparison_mesh", "open_physical", "physical_fields"]


def prepare_physical(cfg, *, executor, session):
    """NASA 原始数据按共享物理提交装配。"""
    import sys

    from omegaconf import OmegaConf

    from ai4e_core.applications.aero_cfd.rawprep.physical import execute

    return execute(
        OmegaConf.to_container(cfg, resolve=True), sys.modules[__name__], executor, session
    )


__all__ += ["prepare_physical"]

from .inspection import inspect_dataset

__all__ += ["inspect_dataset"]

from .physical import read_physical_field

__all__ += ["read_physical_field"]

from .physical import comparison_metadata

__all__ += ["comparison_metadata"]

from .descriptor import describe_rawprep

__all__ += ["describe_rawprep"]

from .physical import inference_fields

__all__ += ["inference_fields"]
