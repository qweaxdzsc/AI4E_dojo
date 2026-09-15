"""PNG/JPG图片预览用例。"""

from pathlib import Path

from .domain import FigureMetadata, supported_figure_format


def describe_figure(path: str) -> FigureMetadata:
    """读取图片的文件级元数据；像素解码继续复用现有解析链路。"""

    source = Path(path)
    extension = source.suffix.lower()
    if not supported_figure_format(extension):
        raise ValueError(f"不支持的图片格式: {extension}")
    return FigureMetadata(name=source.name, extension=extension, byte_size=source.stat().st_size)
