"""独立标量验证选优状态；模型评价和检查点写入由调用方负责。"""

from math import isfinite
from numbers import Real
from typing import Any, Literal


def _metric(value: float) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError("选优指标必须为有限实数")  # noqa: TRY004 - 指标域校验统一报告 ValueError
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError("选优指标必须可表示为有限 float") from exc
    if not isfinite(result):
        raise ValueError("选优指标必须为有限实数")
    return result


class BestMetric:
    """在同一评价口径内选优；保存成功后显式提交状态。

    mode 为 min/max；tie=first 保留先到者，tie=last 接受相等的新候选。
    source 是不透明非空字符串，可标识普通、EMA 或其他权重来源。
    本对象不复制权重、不写文件，也不验证指标单位或候选模型身份。
    调用者须冻结真正受评权重，在 writer 保存成功后 commit，并将最佳快照
    与本状态共同纳入恢复检查点。多个线程或进程不能共享一次判断/提交事务。
    """

    def __init__(
        self, *, mode: Literal["min", "max"] = "min", tie: Literal["first", "last"] = "first"
    ) -> None:
        if mode not in ("min", "max") or tie not in ("first", "last"):
            raise ValueError("mode 须为 min/max，tie 须为 first/last")
        self._mode, self._tie = mode, tie
        self._best: float | None = None
        self._step: int | None = None
        self._source: str | None = None

    def improves(self, value: float) -> bool:
        """校验并判断候选，不修改状态；NaN/Inf 不作为落选静默忽略。"""
        value = _metric(value)
        if self._best is None:
            return True
        if value == self._best:
            return self._tie == "last"
        return value < self._best if self._mode == "min" else value > self._best

    def commit(self, value: float, *, step: int, source: str) -> None:
        """保存成功后提交胜出候选；非法元信息或不胜出的值抛 ValueError。"""
        value = _metric(value)
        if type(step) is not int or step < 0 or type(source) is not str or not source.strip():
            raise ValueError("step 须为非负整数，source 须为非空字符串")
        if not self.improves(value):
            raise ValueError("候选未胜出，不能覆盖选优状态")
        self._best, self._step, self._source = value, step, source

    def state_dict(self) -> dict[str, Any]:
        """返回普通标量状态；尚未选优时 best/step/source 均为 None。"""
        return {
            "version": 1,
            "mode": self._mode,
            "tie": self._tie,
            "best": self._best,
            "step": self._step,
            "source": self._source,
        }

    def validate_state_dict(self, state: dict[str, Any]) -> None:
        """核对政策和选择元信息；不读取文件或修改当前选择。"""
        if type(state) is not dict or set(state) != set(self.state_dict()):
            raise ValueError("选优状态字段不完整")
        if (
            type(state["version"]) is not int
            or state["version"] != 1
            or state["mode"] != self._mode
            or state["tie"] != self._tie
        ):
            raise ValueError("选优版本或政策不兼容")
        if state["best"] is None:
            if state["step"] is not None or state["source"] is not None:
                raise ValueError("未选优状态不能带权重来源")
        else:
            _metric(state["best"])
            if (
                type(state["step"]) is not int
                or state["step"] < 0
                or type(state["source"]) is not str
                or not state["source"].strip()
            ):
                raise ValueError("选优位置或来源非法")

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """校验通过后恢复标量状态；失败不改变当前选择。"""
        self.validate_state_dict(state)
        self._best = None if state["best"] is None else _metric(state["best"])
        self._step, self._source = state["step"], state["source"]
