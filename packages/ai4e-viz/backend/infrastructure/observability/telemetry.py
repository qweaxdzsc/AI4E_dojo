"""失败不影响业务的本地埋点写入器。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from infrastructure.config import runtime_paths


def emit_event(event_name: str, module: str, *, result: str, attributes: dict[str, Any] | None = None) -> None:
    """追加白名单业务事件；任何I/O错误都会被吞掉以保护主业务。"""

    try:
        now = datetime.now(timezone.utc)
        target = runtime_paths().ensure().telemetry / f"events-{now.date().isoformat()}.jsonl"
        payload = {"event_name": event_name, "event_version": 1, "occurred_at": now.isoformat(), "module": module, "result": result, "attributes": attributes or {}}
        with target.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        return
