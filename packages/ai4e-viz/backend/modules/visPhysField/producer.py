"""物理场输出生产器，只在显式请求时写入分配的暂存目录。"""

import csv
from pathlib import Path

import vtk

from .scene import Scene


def csv_value(value):
    """单分量字段写数值单元格，矢量保留分量列表，缺失保持空值。"""
    return value[0] if isinstance(value, list) and len(value) == 1 else value


def capture(scene, path: Path, width=1280, height=720, transparent=False):
    """从同一 VTK 场景捕获固定尺寸 PNG。"""
    if not 64 <= width <= 8192 or not 64 <= height <= 8192:
        raise ValueError("export_size_out_of_range")
    scene.window.SetSize(width, height)
    scene.window.SetAlphaBitPlanes(1 if transparent else 0)
    for renderer in scene.renderers:
        renderer.SetBackgroundAlpha(0 if transparent else 1)
    scene.window.Render()
    image = vtk.vtkWindowToImageFilter()
    image.SetInput(scene.window)
    if transparent:
        image.SetInputBufferTypeToRGBA()
    image.ReadFrontBufferOff()
    image.Update()
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(str(path))
    writer.SetInputConnection(image.GetOutputPort())
    writer.Write()
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError("image_export_failed")


def produce(bindings: list, spec: dict, options: dict, output: Path, progress=None) -> list[Path]:
    """固定配置/时间/相机轨迹生成 PNG、CSV、PNG 序列或 MP4。"""
    scene = Scene(bindings, spec)
    try:

        def select_view():
            """时间更新会重装 renderer，每帧重新选择固定视图。"""
            scene.window.SetSize(int(options.get("width", 1280)), int(options.get("height", 720)))
            if options.get("view") is None:
                scene.add_annotations()
                return
            view_id = options["view"]
            indices = [i for i, v in enumerate(scene.spec["views"]) if v["id"] == view_id]
            if not indices:
                raise ValueError("export_view_missing")
            index = indices[0]
            for i, renderer in enumerate(scene.renderers):
                renderer.SetDraw(i == index)
                if i == index:
                    renderer.SetViewport(0, 0, 1, 1)
            scene.add_annotations()

        kind = options["format"]
        transparent = options.get("transparent_background", False)
        if not isinstance(transparent, bool):
            raise ValueError("invalid_transparent_background")  # noqa: TRY004 - 请求校验沿用业务 ValueError 协议。
        if transparent and kind not in ("png", "png_sequence"):
            raise ValueError("transparent_format_not_supported")
        if kind == "csv":
            chart = options.get("chart") or {}
            if options.get("operation") == "plot_over_line" or options.get("kind") == "plot_over_line":
                path = output / "line_chart.csv"
                headers = chart.get("headers")
                body = chart.get("body")
                if not headers:
                    from .modules.dataOverview.lineChart import line_chart_table

                    rows = scene.command(
                        {
                            "operation": "plot_over_line",
                            "input": options["input"],
                            "point1": options.get("point1") or options.get("start"),
                            "point2": options.get("point2") or options.get("end"),
                            "resolution": int(options.get("resolution", 1000)),
                            "fields": options.get("fields"),
                        }
                    )["rows"]
                    headers, body = line_chart_table(
                        rows,
                        options.get("x_array") or "arc_length",
                        list(options.get("y_arrays") or []),
                    )
                with path.open("w", newline="", encoding="utf-8") as stream:
                    writer = csv.writer(stream)
                    writer.writerow(headers)
                    for row in body:
                        writer.writerow(["" if cell is None else cell for cell in row])
                return [path]
            rows = scene.command(
                {
                    "operation": options.get("operation", "probe"),
                    "input": options["input"],
                    "positions": options["positions"],
                }
            )["rows"]
            fields = sorted(
                {key for row in rows for key in (row.get("fields") or row.get("values") or {})}
            )
            path = output / "probe.csv"
            with path.open("w", newline="", encoding="utf-8") as stream:
                writer = csv.writer(stream)
                writer.writerow(["time", "x", "y", "z", "valid", *fields])
                for row in rows:
                    writer.writerow(
                        [
                            row.get("time"),
                            *row["position"],
                            row["valid"],
                            *(
                                csv_value((row.get("fields") or row.get("values") or {}).get(key))
                                for key in fields
                            ),
                        ]
                    )
            return [path]
        width, height = int(options.get("width", 1280)), int(options.get("height", 720))
        if kind == "png":
            path = output / "view.png"
            select_view()
            capture(scene, path, width, height, transparent)
            return [path]
        if kind not in ("png_sequence", "mp4"):
            raise ValueError("unsupported_export_format")
        times = options.get("times") or scene.times or [None]
        if scene.times and any(t not in scene.times for t in times):
            raise ValueError("export_time_not_in_dataset")
        cameras = options.get("cameras", [])
        total = max(len(times), len(cameras))
        if total > 10000:
            raise ValueError("too_many_export_frames")
        paths = []
        for i in range(total):
            time = times[min(i, len(times) - 1)]
            if time is not None:
                scene.command({"operation": "time", "value": time})
            if cameras:
                scene.command({"operation": "camera", "camera": cameras[min(i, len(cameras) - 1)]})
            path = output / f"frame-{i:06d}.png"
            select_view()
            capture(scene, path, width, height, transparent)
            paths.append(path)
            if progress:
                progress(i + 1, total)
        if kind == "mp4":
            import imageio.v2 as imageio

            fps = int(options.get("fps", 24))
            if not 1 <= fps <= 120:
                raise ValueError("invalid_export_fps")
            video = output / "animation.mp4"
            with imageio.get_writer(video, fps=fps, codec="libx264", macro_block_size=2) as writer:
                for path in paths:
                    writer.append_data(imageio.imread(path))
            for path in paths:
                path.unlink()
            return [video]
        return paths
    finally:
        scene.close()
