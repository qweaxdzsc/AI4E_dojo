"""格式转换请求的纯领域对象。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConversionRequest:
    """描述一次确定的文件转换，不包含进程或存储实现。"""

    source_path: str
    output_path: str
    target_format: str
