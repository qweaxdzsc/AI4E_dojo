"""与数据集内容无关的取回与多包解压。"""

from ai4e_core.abilities.data.source.download.archives import extract_archives
from ai4e_core.abilities.data.source.download.huggingface import (
    download_huggingface_file,
    download_huggingface_snapshot,
)
from ai4e_core.abilities.data.source.download.url import download_url

__all__ = [
    "download_huggingface_file",
    "download_huggingface_snapshot",
    "download_url",
    "extract_archives",
]
