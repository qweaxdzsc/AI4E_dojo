"""阶段管道：按配置打开已装配的阶段盒子。"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from typing import Any

from ai4e_core.applications.base.stage import Stage


class Pipeline:
    """按 ``pipeline.stages`` 顺序执行已选阶段，不管日志目录。"""

    def __init__(self, stages: Sequence[Stage]) -> None:
        self.stages = list(stages)
        self._by_name = {stage.name: stage for stage in self.stages}
        if len(self._by_name) != len(self.stages):
            raise ValueError("阶段名不能重复")

    @classmethod
    def from_config(
        cls,
        config: Mapping[str, Any],
        builders: Mapping[str, Callable[[Mapping[str, Any]], Stage]],
    ) -> Pipeline:
        """只构造配置里声明的阶段。

        Args:
            config: 含 ``pipeline.stages`` 的案例配置。
            builders: 阶段名到装配函数。

        Returns:
            只含已选阶段的管道。

        Raises:
            KeyError: 声明了未注册的阶段。
            TypeError: ``pipeline.stages`` 不是名称列表。
        """
        selected = _selected_stage_names(config, builders)
        stages = []
        for name in selected:
            if name not in builders:
                raise KeyError(f"未注册阶段: {name}")
            stages.append(builders[name](config))
        return cls(stages)

    def run(self, ctx: Any) -> Any:
        """依次执行已选阶段。

        Args:
            ctx: 作业上下文。

        Returns:
            最后一个阶段返回的上下文。
        """
        current = ctx
        for stage in self.stages:
            current = stage.run(current)
        return current


def _selected_stage_names(
    config: Mapping[str, Any],
    builders: Mapping[str, Callable[[Mapping[str, Any]], Stage]],
) -> list[str]:
    """读取 ``pipeline.stages``；缺省按 builders 的插入顺序。"""
    pipeline = config.get("pipeline")
    if pipeline is None:
        return list(builders)
    if not isinstance(pipeline, Mapping):
        raise TypeError("pipeline 必须是映射")
    names = pipeline.get("stages")
    if names is None:
        return list(builders)
    if not isinstance(names, Sequence) or isinstance(names, (str, bytes)):
        raise TypeError("pipeline.stages 必须是名称列表")
    return [str(name) for name in names]
