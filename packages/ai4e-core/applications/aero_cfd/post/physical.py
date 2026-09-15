"""历史完整物理后处理入口；委托独立推理步骤，保留原参数和产物语义。"""

from ai4e_core.applications.aero_cfd.infer.stage import (
    PhysicalPost,
    PostSample,
    check_report,
    configure_evaluation,
    configure_mesh_export,
    configure_physical_output,
    configure_prediction,
    configure_restore,
    configure_save,
    execute,
    open_post,
)

__all__ = [
    "PhysicalPost",
    "PostSample",
    "check_report",
    "configure_evaluation",
    "configure_mesh_export",
    "configure_physical_output",
    "configure_prediction",
    "configure_restore",
    "configure_save",
    "execute",
    "open_post",
]
