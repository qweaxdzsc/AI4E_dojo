"""结构化JSON日志配置，不记录上传内容、密钥或机器绝对路径。"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from infrastructure.config import runtime_paths


class JsonFormatter(logging.Formatter):
    """把标准日志记录转换为稳定JSON对象，便于后续检索和关联请求。"""

    def format(self, record: logging.LogRecord) -> str:
        """输出包含服务、模块、事件和关联ID的单行JSON。"""

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("service", "module", "event", "request_id", "trace_id", "resource_id", "duration_ms", "error_code"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging(service: str, level: int = logging.INFO) -> logging.Logger:
    """为单个运行服务配置控制台和20MB×5轮转文件日志。"""

    log_dir = runtime_paths().ensure().logs / service
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(service)
    logger.setLevel(level)
    if logger.handlers:
        return logger
    handler = RotatingFileHandler(log_dir / f"{service}.jsonl", maxBytes=20 * 1024 * 1024, backupCount=5, encoding="utf-8")
    handler.setFormatter(JsonFormatter())
    logger.addHandler(handler)
    return logger
