"""保留尾批的可恢复数据流；GenCP 固定整批流不受影响。"""

import torch


class BatchStream:
    """使用独立 CPU 排列随机流，明确保存轮次末的不完整批次。"""

    def __init__(self, count: int, batch_size: int, *, seed: int = 42):
        if count < 1 or batch_size < 1:
            raise ValueError("样本数和批量必须为正")
        self.count, self.batch_size, self.offset = count, batch_size, count
        self.generator = torch.Generator().manual_seed(seed)
        self.order = torch.arange(count)

    def next(self) -> torch.Tensor:
        """返回下一批索引，尾部不丢弃也不补重复样本。"""
        if self.offset == self.count:
            self.order = torch.randperm(self.count, generator=self.generator)
            self.offset = 0
        end = min(self.offset + self.batch_size, self.count)
        result = self.order[self.offset : end]
        self.offset = end
        return result

    def state_dict(self) -> dict:
        """记录下一批之前的排列与随机状态。"""
        return {
            "count": self.count,
            "batch_size": self.batch_size,
            "offset": self.offset,
            "order": self.order.clone(),
            "rng": self.generator.get_state(),
        }

    def load_state_dict(self, state: dict) -> None:
        """严格恢复相同样本空间，拒绝无效排列或游标。"""
        if (state["count"], state["batch_size"]) != (self.count, self.batch_size):
            raise ValueError("数据流契约不一致")
        offset = state["offset"]
        if sorted(state["order"].tolist()) != list(range(self.count)) or not (
            offset == self.count or 0 <= offset < self.count and offset % self.batch_size == 0
        ):
            raise ValueError("数据流游标或排列损坏")
        self.order, self.offset = state["order"].clone(), offset
        self.generator.set_state(state["rng"])
