"""外流训练：训练执行与旧只读阶段的兼容导出。"""

from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    ALLOWED_MODEL,
    open_preprocessed_sample,
    open_splits_step,
    read_probe_sample_step,
    resolve_preprocessed_root,
    select_abupt_step,
)
from ai4e_core.applications.aero_cfd.trainprep.dataset import (
    read_probe_stage as standard,
)

__all__ = [
    "ALLOWED_MODEL",
    "open_preprocessed_sample",
    "open_splits_step",
    "read_probe_sample_step",
    "resolve_preprocessed_root",
    "select_abupt_step",
    "standard",
]

from ai4e_core.applications.aero_cfd.trainprep.dataset import open_manifest_sample

__all__ += ["open_manifest_sample"]
