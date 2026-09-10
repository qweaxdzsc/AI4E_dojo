"""训练周期回调：普通可调用对象，不要求继承框架基类。"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class PeriodicCallback:
    """按有效更新或完整轮次触发，零次不触发。"""

    callback: Callable
    unit: str = "epoch"
    every: int = 1

    def __post_init__(self):
        if self.unit not in {"update", "epoch"} or type(self.every) is not int or self.every < 1:
            raise ValueError("回调周期必须是正整数，单位为 update/epoch")

    def __call__(self, event: str, *, epoch: int, updates: int, result: dict):
        """仅在对应生命周期边界执行用户回调，异常交由循环统一收尾。"""
        count = updates if self.unit == "update" else epoch
        if event == self.unit and count > 0 and count % self.every == 0:
            self.callback(epoch=epoch, updates=updates, result=result)
