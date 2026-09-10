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
