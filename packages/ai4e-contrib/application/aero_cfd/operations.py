"""可选领域操作公开模块；普通 recipe 执行不依赖平台操作。"""

__all__ = ["evaluate", "export", "infer", "inspect"]


def evaluate(*args, **kwargs):
    """按既有公开签名评价固定结果，按需加载计算依赖。"""
    from ai4e_core.applications.aero_cfd.post import run_evaluation

    return run_evaluation(*args, **kwargs)


def export(*args, **kwargs):
    """按既有公开签名导出评价记录。"""
    from ai4e_core.applications.aero_cfd.post import export_evaluation

    return export_evaluation(*args, **kwargs)


def inspect(request: dict) -> dict:
    """在领域边界转换公共配置，并隔离检查进程的临时输出。"""
    if request.get("operation") == "describe_task":
        from .task_description import describe_task

        return describe_task(request["config"])
    if request.get("operation") == "dataset_conflict":
        from .task_datasets import conflict_detail

        return conflict_detail(request["existing"], request["incoming"])
    if request.get("operation") in {"dataset_copy_plan", "migration_candidates"}:
        from .task_datasets import dataset_copy_plan, migration_candidates

        return (
            dataset_copy_plan(request["manifest"])
            if request["operation"] == "dataset_copy_plan"
            else migration_candidates(request["runs"])
        )
    if request.get("operation") == "convert_configuration":
        from .configuration import convert_configuration

        return convert_configuration(request["config"])
    if request.get("operation") in {"dataset_identity", "validate_dataset"}:
        from .task_datasets import describe_dataset, processed_claim

        return (
            processed_claim(request["config"])
            if request["operation"] == "dataset_identity"
            else describe_dataset(request["manifest"])
        )
    from copy import deepcopy
    from pathlib import Path

    from ai4e_core.applications.aero_cfd.inspection import execute
    from ai4e_core.base.config.conventions import normalize_recipe_config

    from .inputs import bind_inputs, public_inputs

    value = deepcopy(request)
    config = value.get("config")
    if config:
        output = Path(value["output_dir"]).resolve() if value.get("output_dir") else None
        output_dirs = (
            {
                stage: output / "workspace" / stage
                for stage in ("rawprep", "trainprep", "infer", "post")
            }
            if output is not None
            else None
        )
        bound = bind_inputs(
            normalize_recipe_config(config, base=value.get("config_dir", ".")),
            output_dirs=output_dirs,
        )
        value["config"] = bound
    result = execute(value)
    if value.get("operation") == "trace_model":
        from .model_inspection import export_platform_views

        return export_platform_views(
            result["network"],
            result["inputs"],
            Path(value["output_dir"]),
            revision=result["revision"],
            input_source=result["input_source"],
            predict=result.get("predict"),
        )
    if isinstance(result.get("configuration"), dict):
        result["configuration"] = public_inputs(result["configuration"])
    return result


def infer(request: dict) -> dict:
    """推理检查消费同一公共配置连接，Task不解读模型输入树。"""
    from . import task_inference

    operation = request.get("operation")
    if operation == "checkpoint_candidates":
        return task_inference.checkpoint_candidates(request["run"])
    if operation == "describe_checkpoint":
        return task_inference.describe_checkpoint(request["path"], request["run"])
    if operation == "plan_execution":
        return task_inference.plan_execution(request["request"])
    if operation == "read_progress":
        return task_inference.read_progress(request["run"])
    if operation == "run_metrics":
        from .task_post import run_metrics

        return run_metrics(request["run"])
    if operation == "read_results":
        from .task_results import read_results

        return read_results(request["payload"])
    if operation in {"post_catalog", "dataset_samples"}:
        from .task_post import describe_run, describe_samples

        return (
            describe_run(request["run"])
            if operation == "post_catalog"
            else describe_samples(request["item"])
        )
    from copy import deepcopy

    from ai4e_core.applications.aero_cfd.infer import inspect_artifacts
    from ai4e_core.base.config.conventions import normalize_recipe_config

    from .inputs import bind_inputs

    value = deepcopy(request)
    arguments = value.get("arguments", {})
    if "config" in arguments:
        arguments["config"] = bind_inputs(
            normalize_recipe_config(arguments["config"], base=arguments.get("config_dir", "."))
        )
    result = inspect_artifacts(value)
    if operation == "inputs":
        return {**result, "selection_supported": True}
    return result
