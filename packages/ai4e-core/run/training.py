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

    @property
    def data_dir(self) -> Path:
        """本次运行科学数据目录；托管目录与独立运行采用相同交接。"""
        return Path(self._state["data_dir"])

    def output_dir(self, stage: str) -> Path:
        """分配阶段数据目录；检查模式只返回位置，不创建目录。"""
        if not isinstance(stage, str) or not stage.isidentifier():
            raise ValueError("阶段目录必须为标识符")
        from .provenance import MANAGED

        managed = MANAGED.get()
        locations = managed["context"].stage_outputs if managed is not None else {}
        target = Path(locations[stage]) if stage in locations else self.data_dir / stage
        if not self.dry_run:
            target.mkdir(parents=True, exist_ok=True)
        return target

    def record_asset(
        self, name: str, path: str | Path, *, kind: str, stage: str,
        dependencies=(), semantics: dict | None = None, bundle_root: str | Path | None = None,
    ) -> Path:
        """登记已落盘的数据及依赖；不替代领域产物保存。"""
        if self.dry_run:
            raise RuntimeError("检查模式不能发布资产")
        return self._state["writer"].record_asset(
            name, path, kind=kind, stage=stage,
            dependencies=dependencies, semantics=semantics, bundle_root=bundle_root,
        )

    def record_metric(
        self, name: str, value: float, *, stage: str, semantics: dict, assets,
    ) -> Path:
        """提交具有明确口径和来源的科学指标。"""
        if self.dry_run:
            raise RuntimeError("检查模式不能发布指标")
        return self._state["writer"].record_metric(
            name, value, stage=stage, semantics=semantics, assets=assets,
        )

    def report(self, value: dict, *, stage: str = "train") -> None:
        """将轻量报告交给现有 writer 的最终摘要。"""
        from copy import deepcopy

        self._state.setdefault("reports", {})[stage] = deepcopy(value)

    def checkpoint(self, label: str, payload: dict, *, namespace: str | None = None):
        """检查点提交委托现有唯一 writer，检查模式禁止写入。"""
        if self.dry_run:
            raise RuntimeError("检查模式不能保存检查点")
        return self._state["writer"].write_checkpoint(
            label,
            {**payload, "effective_config": deepcopy(self._state["config"])},
            namespace=namespace,
            semantics=getattr(self, "_checkpoint_semantics", None),
        )

    def with_checkpoint_labels(self, semantics: dict):
        """返回同一运行的带标签写入视图；标签由调用应用显式提供。"""
        from copy import copy
        from ai4e_spec.artifacts.task_operations import json_record

        result = copy(self)
        result._checkpoint_semantics = json_record(semantics)
        return result

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
