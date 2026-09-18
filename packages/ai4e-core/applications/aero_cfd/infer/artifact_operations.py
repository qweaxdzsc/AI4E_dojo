"""固定物理产物的检查连接；仅此适配器解释既有物理 schema。"""


def inspect_artifacts(request: dict):
    """解析已固定的产物，不重跑推理；未知操作明确失败。"""
    from ai4e_core.applications.aero_cfd.infer import (
        available_devices,
        inspect_checkpoint,
        inspect_inputs,
    )

    if request["operation"] == "metadata":
        result = []
        for path in request["paths"]:
            try:
                result.append({"path": path, "metadata": inspect_checkpoint(path)})
            except Exception as exc:  # noqa: BLE001 - 单个失效候选不能隐藏其他候选
                result.append({"path": path, "error": str(exc)})
    elif request["operation"] == "inputs":
        result = inspect_inputs(**request["arguments"])
    elif request["operation"] == "devices":
        result = available_devices()
    elif request["operation"] == "compare":
        from ai4e_core.applications.aero_cfd.infer import compare_results

        result = compare_results(request["reports"])
    elif request["operation"] == "statistics":
        from ai4e_core.applications.aero_cfd.infer import summarize_records

        result = summarize_records(request["records"], include_all=True)
    elif request["operation"] == "result_views":
        from ai4e_core.applications.aero_cfd.infer import result_views

        result = result_views(request["records"])
    elif request["operation"] == "export":
        from ai4e_core.applications.aero_cfd.infer.exports import export_results

        result = export_results(**request["arguments"])
    elif request["operation"] == "metric_catalog":
        from ai4e_core.applications.aero_cfd.post import metric_catalog

        result = metric_catalog()
    elif request["operation"] == "result_fields":
        from ai4e_core.applications.aero_cfd.post import describe_result_fields

        result = describe_result_fields(request["manifests"])
    else:
        raise ValueError("unknown_inference_inspection")
    return result
