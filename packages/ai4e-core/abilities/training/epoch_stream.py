"""有限轮次记录的可恢复收批；抽样与排列规则由普通用户函数提供。"""

from collections.abc import Callable, Sequence
from math import isfinite
from typing import Any

import numpy as np


def _copy_record(value: Any) -> Any:
    """先限定安全值类型，再复制；不调用用户对象的复制或反序列化方法。"""
    if value is None or type(value) in (bool, int, str):
        return value
    if type(value) is float and isfinite(value):
        return value
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return _copy_record(float(value))
    if type(value) in (list, tuple):
        return type(value)(_copy_record(item) for item in value)
    if type(value) is dict and all(type(key) is str for key in value):
        return {key: _copy_record(item) for key, item in value.items()}
    raise ValueError("记录只允许有限数值、字符串及普通 list/tuple/字符串键 dict")


class EpochBatchStream:
    """保留用户有序记录、PCG64 和轮内游标，支持尾批或显式丢尾。

    epoch_items(rng, epoch) 接收独立 NumPy Generator 和从零开始的轮次，
    返回有限 list/tuple。它应只使用传入 rng 抽样，来源与语义由调用者通过
    source_contract 声明。构造、快照与恢复均不调用它；下一轮首批才生成记录。
    不负责读取数据、设备搬运、额外打乱、多 worker 预取或外部函数状态恢复。
    """

    def __init__(
        self,
        epoch_items: Callable[[np.random.Generator, int], Sequence[Any]],
        batch_size: int,
        *,
        seed: int = 42,
        drop_last: bool = False,
        source_contract: dict[str, Any],
    ) -> None:
        if not callable(epoch_items):
            raise TypeError("epoch_items 必须可调用")
        if type(batch_size) is not int or batch_size < 1 or type(drop_last) is not bool:
            raise ValueError("batch_size 必须为正整数，drop_last 必须为布尔值")
        if type(source_contract) is not dict:
            raise ValueError("source_contract 必须为显式字典")
        self._epoch_items = epoch_items
        self._batch_size, self._drop_last = batch_size, drop_last
        self._contract = _copy_record(source_contract)
        self._rng = np.random.Generator(np.random.PCG64(seed))
        self._epoch, self._offset, self._items = -1, 0, []

    @property
    def epoch(self) -> int:
        """当前零基轮次；尚未取批时为 -1。"""
        return self._epoch

    @property
    def offset(self) -> int:
        """当前轮已交付的记录数；丢弃尾项不计入。"""
        return self._offset

    @property
    def epoch_end(self) -> bool:
        """取批后是否已到轮末，可连接 fit_iterations 的 epoch_end 回调。"""
        return self._epoch >= 0 and self._offset == self._limit(self._items)

    def _limit(self, items: list) -> int:
        return len(items) // self._batch_size * self._batch_size if self._drop_last else len(items)

    def next(self) -> list[Any]:
        """交付独立的下一批记录；空轮或丢尾后零批即失败，不自动跳过。"""
        if self._epoch < 0 or self.epoch_end:
            rng = np.random.Generator(np.random.PCG64())
            rng.bit_generator.state = self._rng.bit_generator.state
            items = self._epoch_items(rng, self._epoch + 1)
            if type(items) not in (list, tuple):
                raise ValueError("epoch_items 必须返回有限 list 或 tuple，不接受惰性迭代器")
            items = list(_copy_record(items))
            if not items or self._limit(items) == 0:
                raise ValueError("本轮记录为空，或 drop_last 后没有可交付批次")
            self._items, self._rng = items, rng
            self._epoch, self._offset = self._epoch + 1, 0
        end = min(self._offset + self._batch_size, self._limit(self._items))
        batch = _copy_record(self._items[self._offset : end])
        self._offset = end
        return batch

    def state_dict(self) -> dict[str, Any]:
        """捕获下一批之前的独立状态，不保存函数或读取下一轮。"""
        return _copy_record(
            {
                "version": 1,
                "batch_size": self._batch_size,
                "drop_last": self._drop_last,
                "source_contract": self._contract,
                "epoch": self._epoch,
                "offset": self._offset,
                "items": self._items,
                "rng": self._rng.bit_generator.state,
            }
        )

    def _validated(self, state: dict[str, Any]) -> tuple[dict, np.random.Generator]:
        saved = _copy_record(state)
        if type(saved) is not dict or set(saved) != set(self.state_dict()):
            raise ValueError("轮次数据流状态字段不完整")
        if (
            type(saved["version"]) is not int
            or saved["version"] != 1
            or type(saved["batch_size"]) is not int
            or saved["batch_size"] != self._batch_size
            or type(saved["drop_last"]) is not bool
            or saved["drop_last"] != self._drop_last
            or saved["source_contract"] != self._contract
        ):
            raise ValueError("轮次数据流版本、收批设置或来源契约不兼容")
        epoch, offset, items = saved["epoch"], saved["offset"], saved["items"]
        if (
            type(epoch) is not int
            or epoch < -1
            or type(offset) is not int
            or type(items) is not list
        ):
            raise ValueError("轮次、记录或游标非法")
        limit = self._limit(items)
        if epoch == -1:
            valid = not items and offset == 0
        else:
            valid = (
                limit > 0
                and 0 < offset <= limit
                and (offset % self._batch_size == 0 or offset == limit)
            )
        if not valid:
            raise ValueError("轮次与批次游标不一致")
        rng = np.random.Generator(np.random.PCG64())
        try:
            rng.bit_generator.state = saved["rng"]
        except (ValueError, TypeError, KeyError, OverflowError) as exc:
            raise ValueError("PCG64 随机状态非法") from exc
        if rng.bit_generator.state != saved["rng"]:
            raise ValueError("PCG64 随机状态不规范")
        return saved, rng

    def validate_state_dict(self, state: dict[str, Any]) -> None:
        """只校验恢复声明，不修改本流、不取样；非法输入抛 ValueError。"""
        self._validated(state)

    def load_state_dict(self, state: dict[str, Any]) -> None:
        """先验证完整副本再恢复；拒绝时保持当前流不变。"""
        saved, rng = self._validated(state)
        self._epoch, self._offset, self._items = saved["epoch"], saved["offset"], saved["items"]
        self._rng = rng
