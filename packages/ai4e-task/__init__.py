"""AI4E 项目、版本和本地执行的公开 Python API；管理操作不加载训练栈。"""

from .projects.project import create_project, open_project, recover_project
from .projects.shared import get_shared, list_shared, register_shared, share_run_asset
from .tasks.create import fork_task, new_task
from .tasks.execution import resume_run, start_captured_run, stop_run, submit_run, wait_run
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
from .tasks.configuration import read_configuration, replace_configuration, save_configuration
from .tasks.management import update_task

__all__ += [
    "read_configuration",
    "replace_configuration",
    "save_configuration",
    "update_project",
    "update_task",
]

from .tasks.inspections import inspect_task

__all__ += ["inspect_task"]

from .storage.processed_datasets import (
    check_processed_name,
    describe_processed_dataset,
    describe_processed_name,
    list_processed_datasets,
    manifest_digest,
    processed_claim,
    publish_processed_from_run,
    register_processed_dataset,
    validate_processed_name,
)
from .tasks.artifacts import list_stage_artifacts

__all__ += ["list_stage_artifacts"]
__all__ += [
    "check_processed_name",
    "describe_processed_dataset",
    "describe_processed_name",
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

from .tasks.checkpoints import freeze_checkpoint, inference_samples, list_inference_checkpoints
from .tasks.inference import (
    cancel_inference,
    check_inference,
    inference_devices,
    list_inference_batches,
    read_inference_batch,
    recover_inference,
    retry_inference,
    submit_inference,
)
from .tasks.inference_exports import export_inference
from .tasks.inference_results import inference_results

__all__ += [
    "cancel_inference",
    "check_inference",
    "export_inference",
    "freeze_checkpoint",
    "inference_devices",
    "inference_results",
    "inference_samples",
    "list_inference_batches",
    "list_inference_checkpoints",
    "read_inference_batch",
    "recover_inference",
    "retry_inference",
    "submit_inference",
]

# 固定结果后处理：管理层只交付身份，计算在独立core进程执行。
from .tasks.post_metrics import (
    cancel_post_metrics,
    export_post_metrics,
    list_post_metrics,
    metric_catalog,
    read_post_metrics,
    submit_post_metrics,
)
from .tasks.post_results import freeze_result_item, list_post_result_files, post_results

__all__ += [
    "cancel_post_metrics",
    "export_post_metrics",
    "freeze_result_item",
    "list_post_metrics",
    "list_post_result_files",
    "metric_catalog",
    "post_results",
    "read_post_metrics",
    "submit_post_metrics",
]

from .tasks.operations import operation_target

__all__ += ["operation_target"]

from .projects.datasets import (
    bind_shared_dataset,
    describe_shared_name,
    get_shared_dataset,
    list_shared_datasets,
    run_physical_manifest,
)

__all__ += [
    "bind_shared_dataset",
    "describe_shared_name",
    "get_shared_dataset",
    "list_shared_datasets",
    "run_physical_manifest",
]

from .projects.dataset_migration import migrate_shared_datasets
from .templates.materialize import recipe_entry
from .tasks.official_scripts import (
    is_old_official_stage,
    migrate_official_aero_scripts,
    verified_old_sources,
)

__all__ += ["migrate_shared_datasets", "recipe_entry"]
__all__ += ["is_old_official_stage", "migrate_official_aero_scripts", "verified_old_sources"]
