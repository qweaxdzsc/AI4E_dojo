"""推理检查子进程：只调用 core 公开门面，管理进程不导入训练栈。"""

import contextlib
import json
import sys


def main() -> None:
    """从受控父进程接收固定请求；不允许指定任意函数路径。"""
    request = json.load(sys.stdin)
    with contextlib.redirect_stdout(sys.stderr):
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

            result = summarize_records(request["records"])
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
    print(json.dumps(result, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
