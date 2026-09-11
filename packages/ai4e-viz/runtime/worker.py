"""独立预览进程，兼容旧请求并提供版本化逐行事件协议。"""

import contextlib
import json
import sys
from pathlib import Path

from ..inspect.dispatch import inspect_file
from ..preview.mesh import preview_mesh
from ..preview.tensor import preview_tensor
from ..preview.text import preview_text


def execute(request: dict) -> dict:
    """执行服务已解析的文件检查、切片或有限显示管线。"""
    modern = request.get("protocol_version") == 1
    path = Path(request["source"]["path"] if modern else request["path"])
    options = request.get("options", {})
    operation = request.get("operation")
    if operation == "inspect":
        return inspect_file(path)
    if operation == "transform":
        from ..inspect.mesh import read_mesh
        from ..pipeline import execute_pipeline
        from ..serialization import write_display

        source = request["source"].get("asset_ref", {"revision": request["source"].get("revision")})
        geometry = options.get("geometry")
        if geometry:
            from ..pipeline.tensor_points import read_tensor_points

            dataset = read_tensor_points(path, geometry)
        else:
            dataset = read_mesh(path, options.get("block"))
        data, generated = execute_pipeline(dataset, options.get("pipeline", []))
        return write_display(
            data,
            Path(request["output_dir"]),
            source=source,
            pipeline=options.get("pipeline", []),
            generated=generated,
            field_metadata=geometry,
        )
    if operation == "summarize":
        from ..preview.fields import summarize

        return summarize(path, **options)
    info = inspect_file(path)
    return {"mesh": preview_mesh, "tensor": preview_tensor, "text": preview_text}[info["kind"]](
        path, **options
    )


def main() -> None:
    """协议独占 stdout，第三方读取器输出隔离到 stderr。"""
    request = json.load(sys.stdin)
    modern = request.get("protocol_version") == 1
    if modern:
        print(json.dumps({"type": "progress", "phase": "reading"}), flush=True)
    try:
        with contextlib.redirect_stdout(sys.stderr):
            result = execute(request)
        event = {"type": "result", "result": result} if modern else {"result": result}
    except Exception as exc:  # noqa: BLE001 - 独立进程隔离第三方读取异常
        event = (
            {"type": "error", "error": {"code": "visualization_failed", "message": str(exc)}}
            if modern
            else {"error": str(exc)}
        )
    print(json.dumps(event, ensure_ascii=False, allow_nan=False), flush=True)
