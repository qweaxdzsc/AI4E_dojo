"""外流独立推理公开步骤及管理进程使用的只读检查入口。"""

from . import stage
from .configuration import inference_parameters, resolve_infer
from .inspection import available_devices, inspect_checkpoint, inspect_inputs


def open_inference(config, *, dataset_component, model_component, session, trained=None):
    """使用独立 infer 参数打开完整物理推理，不改变调用者的训练配置。"""
    job = stage.open_post(
        inference_parameters(config),
        dataset_component=dataset_component,
        model_component=model_component,
        session=session,
        trained=trained,
    )
    job.phase = "infer"
    job.config["infer"] = job.config["post"].copy()
    # 选择在步骤登记结束后解析，以允许用户先登记派生字段。
    return job


configure_restore = stage.configure_restore
configure_prediction = stage.configure_prediction
configure_physical_output = stage.configure_physical_output
configure_evaluation = stage.configure_evaluation
configure_save = stage.configure_save
configure_mesh_export = stage.configure_mesh_export
check_report = stage.check_report
execute = stage.execute

from .fields import configure_derived_fields
from .results import compare_results, open_results, read_sample

__all__ = [
    "available_devices",
    "check_report",
    "compare_results",
    "configure_derived_fields",
    "configure_evaluation",
    "configure_mesh_export",
    "configure_physical_output",
    "configure_prediction",
    "configure_restore",
    "configure_save",
    "execute",
    "inspect_checkpoint",
    "inspect_inputs",
    "open_inference",
    "open_results",
    "read_sample",
    "resolve_infer",
]

from .catalog import describe_catalog, describe_fields
from .evaluation import summarize_records
from .selection import configure_selection

__all__ += ["configure_selection", "describe_catalog", "describe_fields", "summarize_records"]
