"""按内容哈希保存原始上传文件的对象存储原语。"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

from infrastructure.config import runtime_paths
from infrastructure.storage.pathResolver import storage_key_for


def put_dataset(source: str | Path, original_name: str) -> tuple[str, str]:
    """原子保存数据集并返回 ``(storage_key, sha256)``。

    相同内容复用同一对象目录；展示文件名经过 ``Path.name`` 处理，不能注入父级路径。
    """

    source_path = Path(source)
    digest = hashlib.sha256(source_path.read_bytes()).hexdigest()
    paths = runtime_paths().ensure()
    target = paths.objects / "datasets" / digest[:2] / digest / "source" / Path(original_name).name
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        temporary = paths.temporary / "visDatasets" / f"{digest}.part"
        temporary.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_bytes(source_path.read_bytes())
        os.replace(temporary, target)
    return storage_key_for(target), digest
