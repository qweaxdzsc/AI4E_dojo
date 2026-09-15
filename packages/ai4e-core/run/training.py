"""训练与现有运行会话的公开桥接，不创建新的启动生命周期。"""

from copy import deepcopy
from pathlib import Path

from .session import CURRENT


class TrainingRun:
    """向业务交付执行意图和报告接口，隐藏会话状态。"""

    def __init__(self):
        """仅在既有 launch 会话中创建桥接。"""
        self._state = CURRENT.get()
        if self._state is None:
            raise RuntimeError("训练必须通过 session.launch 启动")

    @property
    def entrypoint(self) -> str:
        """实际启动脚本，仅用于运行来源记录。"""
        return self._state["script"]

    @property
    def dry_run(self) -> bool:
        """检查模式不更新模型或数据。"""
        return bool(self._state["flags"]["dry_run"])

    @property
    def run_dir(self) -> Path:
        """本次会话运行目录，供后处理解析本 run 的检查点。"""
        return Path(self._state["writer"].run_dir)

    def report(self, value: dict, *, stage: str = "train") -> None:
        """将轻量报告交给现有 writer 的最终摘要。"""
        from copy import deepcopy

        self._state.setdefault("reports", {})[stage] = deepcopy(value)

    def checkpoint(self, label: str, payload: dict):
        """检查点提交委托现有唯一 writer，检查模式禁止写入。"""
        if self.dry_run:
            raise RuntimeError("检查模式不能保存检查点")
        return self._state["writer"].write_checkpoint(
            label, {**payload, "effective_config": deepcopy(self._state["config"])}
        )

    def artifact(self, name: str, value: dict) -> Path:
        """将阶段交付交给唯一 writer；检查模式不发布成功产物。"""
        if self.dry_run:
            raise RuntimeError("检查模式不能发布阶段交付")
        return self._state["writer"].write_artifact(name, value)

    def record_config(self, config: dict) -> None:
        """兼容幂等确认；不同配置明确拒绝，运行事实使用报告或产物。"""
        if config != self._state["config"]:
            raise ValueError(
                "运行配置已冻结；业务调用参数不得覆盖输入快照，请通过 report/artifact 记录运行事实"
            )

    def execute_samples(self, samples, process, *, stage: str):
        """复用 run 批量执行；业务提供单样本函数，首错保留已提交摘要。"""
        from ai4e_core.applications.base import Stage

        from .execute import execute_many

        def execute_one(context):
            context["result"] = process(context["sample"])
            return context

        summary = execute_many(samples, Stage(stage, [execute_one]), context=self._state)
        return summary["results"]
