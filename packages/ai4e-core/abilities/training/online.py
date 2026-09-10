"""在线损失窗口：每批记账，冲刷得到窗口平均。"""

import torch


def _mean(values):
    stacked = torch.stack([item.detach().reshape(()).float() for item in values])
    mean = stacked.mean()
    if not torch.isfinite(mean):
        raise ValueError("在线损失非有限")
    return float(mean)


class OnlineLoss:
    """逐步收集总损失与分项，冲刷后清空。"""

    def __init__(self):
        self._total = []
        self._named = {}

    def empty(self) -> bool:
        """窗口是否还没有记账。"""
        return not self._total

    def record(self, result: dict) -> None:
        """记下一批总损失和分项；非有限值立即失败。"""
        total = result["loss"].detach()
        if not torch.isfinite(total).all():
            raise ValueError("在线损失非有限")
        self._total.append(total)
        for name, value in (result.get("losses") or {}).items():
            item = value.detach()
            if not torch.isfinite(item).all():
                raise ValueError("在线损失非有限")
            self._named.setdefault(name, []).append(item)

    def flush(self) -> dict:
        """返回窗口平均并清空；空窗口或非有限均值失败。"""
        if not self._total:
            raise ValueError("在线损失窗口为空")
        means = {"loss": _mean(self._total)}
        for name, values in self._named.items():
            means[name] = _mean(values)
        self._total.clear()
        self._named.clear()
        return means
