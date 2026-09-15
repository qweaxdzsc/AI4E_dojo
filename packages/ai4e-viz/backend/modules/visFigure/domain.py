"""图片预览领域值对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FigureMetadata:
    """图片预览所需的最小文件元数据。"""

    name: str
    extension: str
    byte_size: int


def supported_figure_format(extension: str) -> bool:
    """判断扩展名是否属于当前图片预览范围。"""

    return extension.lower() in {".png", ".jpg", ".jpeg"}
