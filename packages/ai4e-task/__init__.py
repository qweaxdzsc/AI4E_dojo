"""AI4E 项目、版本和本地执行的公开 Python API；管理操作不加载训练栈。"""

from .projects.project import create_project, open_project, recover_project
from .projects.shared import get_shared, list_shared, register_shared, share_run_asset
from .tasks.create import fork_task, new_task
from .tasks.execution import resume_run, stop_run, submit_run, wait_run
from .tasks.execution import start_captured_run
from .tasks.query import get_run, get_task, import_run, list_runs, list_tasks, read_log
from .templates.catalog import list_templates, register_template
from .versions.compare import compare_runs, compare_versions, compare_worktree
from .versions.tree import get_lineage

__all__ = [
    "compare_runs",
    "compare_versions",
    "compare_worktree",
    "create_project",
    "fork_task",
    "get_lineage",
    "get_run",
    "get_shared",
    "get_task",
    "import_run",
    "list_runs",
    "list_shared",
    "list_tasks",
    "list_templates",
    "new_task",
    "open_project",
    "read_log",
    "recover_project",
    "register_shared",
    "register_template",
    "resume_run",
    "share_run_asset",
    "stop_run",
    "submit_run",
    "wait_run",
]

from .projects.project import update_project
from .tasks.configuration import read_configuration, save_configuration
from .tasks.management import update_task

__all__ += ["read_configuration", "save_configuration", "update_project", "update_task"]

from .tasks.inspections import inspect_task

__all__ += ["inspect_task"]

from .tasks.artifacts import list_stage_artifacts
from .storage.processed_datasets import (
    check_processed_name,
    describe_processed_dataset,
    list_processed_datasets,
    manifest_digest,
    processed_claim,
    publish_processed_from_run,
    register_processed_dataset,
    validate_processed_name,
)

__all__ += ["list_stage_artifacts"]
__all__ += [
    "check_processed_name",
    "describe_processed_dataset",
    "list_processed_datasets",
    "manifest_digest",
    "processed_claim",
    "publish_processed_from_run",
    "register_processed_dataset",
    "validate_processed_name",
]

from .tasks.artifacts import read_run_metrics

__all__ += ["read_run_metrics"]

from .versions.details import read_version_details

__all__ += ["read_version_details"]

from .tasks.query import get_stage_summary

__all__ += ["get_stage_summary"]

from .tasks.visualizations import visualization_storage

__all__ += ["visualization_storage"]
from .tasks.rawprep import describe_rawprep, initialize_rawprep, validate_rawprep_configuration

__all__ += ["describe_rawprep", "initialize_rawprep", "validate_rawprep_configuration"]
__all__ += ["start_captured_run"]

from .tasks.checkpoints import list_inference_checkpoints, inference_samples, freeze_checkpoint
from .tasks.inference import (
    check_inference, submit_inference, list_inference_batches, read_inference_batch,
    cancel_inference, retry_inference, recover_inference, inference_devices,
)
from .tasks.inference_results import inference_results
from .tasks.inference_exports import export_inference

__all__ += [
    "list_inference_checkpoints", "inference_samples", "freeze_checkpoint", "check_inference",
    "submit_inference", "list_inference_batches", "read_inference_batch", "cancel_inference",
    "retry_inference", "recover_inference", "inference_devices", "inference_results", "export_inference",
]

# 固定结果后处理：管理层只交付身份，计算在独立core进程执行。
from .tasks.post_results import freeze_result_item, list_post_result_files, post_results
from .tasks.post_metrics import (submit_post_metrics, read_post_metrics, list_post_metrics,
                                cancel_post_metrics, export_post_metrics, metric_catalog)
__all__ += ["post_results", "list_post_result_files", "freeze_result_item", "submit_post_metrics",
            "read_post_metrics", "list_post_metrics", "cancel_post_metrics", "export_post_metrics",
            "metric_catalog"]
