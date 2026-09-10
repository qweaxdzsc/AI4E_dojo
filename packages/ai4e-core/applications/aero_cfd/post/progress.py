"""外流后处理的部分交付账本；所有运行文件仍由注入的 run writer 写入。"""

from contextlib import contextmanager
from copy import deepcopy

from ai4e_core.base.events import LOGGER, sample_context


class PostProgress:
    """记录操作、样本和已提交路径，失败不抹去已完成交付。"""

    def __init__(self, run, enabled):
        self.run = run
        self.report = {
            "mode": "post",
            "status": "running",
            "operations": {
                name: {
                    "status": "pending" if active else "skipped",
                    "completed": 0,
                    "samples": [],
                    "artifacts": [],
                    "error": None,
                }
                for name, active in enabled.items()
            },
        }
        self.protocol = None
        self.active = None
        self.current = None

    def publish(self):
        """先更新最终摘要的内存副本，再原子写出最后一次可恢复进度。"""
        value = deepcopy(self.report)
        self.run.report(value, stage="post")
        if self.protocol is not None:
            self.run.artifact("comparison-protocol.json", self.protocol)
        self.run.artifact("post-progress.json", value)

    @contextmanager
    def operation(self, name):
        """开始一个已启用分支，捕获错误时保留本分支已完成样本。"""
        self.active = name
        record = self.report["operations"][name]
        record["status"] = "running"
        try:
            self.publish()
            yield
            record["status"] = "succeeded"
            self.publish()
        except Exception as exc:
            record["status"] = "failed"
            record["error"] = self.error(exc)
            raise
        finally:
            self.active = None

    @contextmanager
    def unit(self, samples, *, operation=None):
        """标记一个实际执行单位；批次级错误不猜测是其中哪个样本失败。"""
        record = self.report["operations"][self.active]
        unit = {"samples": deepcopy(samples), "status": "running", "artifacts": []}
        record["samples"].append(unit)
        self.current = unit
        try:
            with sample_context(operation or self.active, samples):
                yield
            unit["status"] = "succeeded"
            record["completed"] += len(samples)
            self.publish()
        except Exception as exc:
            unit["status"] = "failed"
            unit["error"] = self.error(exc)
            raise
        finally:
            self.current = None

    def committed(self, path):
        """仅在保存函数已成功返回后登记交付，不扫描历史文件推断成功。"""
        path = str(path)
        record = self.report["operations"][self.active]
        record["artifacts"].append(path)
        if self.current is not None:
            self.current["artifacts"].append(path)
        self.publish()

    def finish(self, error=None):
        """发布最终状态；收尾写入失败不得覆盖原始计算异常。"""
        self.report["status"] = "failed" if error is not None else "succeeded"
        if error is not None:
            for record in self.report["operations"].values():
                if (
                    record["status"] == "succeeded"
                    and record.get("expected", record["completed"]) > record["completed"]
                ):
                    record["status"] = "partial"
            self.report["error"] = self.error(error)
        try:
            self.publish()
        except Exception:
            if error is None:
                raise
            LOGGER.exception("后处理进度收尾写入失败，保留原始异常")

    @staticmethod
    def error(exc):
        """生成不含数组内容的失败记录。"""
        return {"type": type(exc).__name__, "message": str(exc), **getattr(exc, "dojo_context", {})}
