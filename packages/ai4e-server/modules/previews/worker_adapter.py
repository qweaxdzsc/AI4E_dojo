"""独立预览进程适配，不导入可视化实现。"""

import hashlib
import json
import subprocess
import sys

from ...infrastructure.content_access import revision


def inspect_preview(service, path, operation, options):
    """内容摘要键缓存；失败或进程超时不返回伪造结果。"""
    content = revision(path)
    key = hashlib.sha256(
        json.dumps([path.suffix.lower(), content, operation, options], sort_keys=True).encode()
    ).hexdigest()
    cache = service.settings.root / "previews" / f"{key}.json"
    if cache.exists():
        return json.loads(cache.read_text())
    proc = subprocess.run(
        [sys.executable, "-m", "ai4e_viz"],
        input=json.dumps({"path": str(path), "operation": operation, "options": options}),
        text=True,
        capture_output=True,
        timeout=90,
        check=False,
    )
    if proc.returncode:
        raise ValueError("preview_worker_failed: " + proc.stderr[-1000:])
    value = json.loads(proc.stdout)
    if "error" in value:
        raise ValueError(value["error"])
    if revision(path) != content:
        raise ValueError("file_changed_during_preview")
    result = {**value["result"], "revision": content}
    cache.parent.mkdir(parents=True, exist_ok=True)
    from uuid import uuid4

    temp = cache.with_suffix("." + uuid4().hex + ".tmp")
    temp.write_text(json.dumps(result, allow_nan=False))
    temp.replace(cache)
    return result
