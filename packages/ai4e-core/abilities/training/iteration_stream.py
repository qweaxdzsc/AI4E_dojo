"""可恢复的固定大小批次流；排列随机性独立于模型随机性。"""

import torch


class IterationStream:
    """保存排列、批次游标和发生器状态，恢复时不重复或跳过样本。"""

    def __init__(self, count, batch_size, *, seed=42):
        if count < batch_size or batch_size < 1 or count % batch_size:
            raise ValueError("固定批次流要求样本数是批量的正整数倍")
        self.count, self.batch_size, self.offset = count, batch_size, count
        self.generator = torch.Generator().manual_seed(seed)
        self.order = torch.arange(count)

    def next(self):
        """返回下一个完整批次索引。"""
        if self.offset == self.count:
            self.order = torch.randperm(self.count, generator=self.generator)
            self.offset = 0
        batch = self.order[self.offset : self.offset + self.batch_size]
        self.offset += self.batch_size
        return batch

    def state_dict(self):
        """捕获下一批之前的状态。"""
        return {
            "count": self.count,
            "batch_size": self.batch_size,
            "offset": self.offset,
            "order": self.order.clone(),
            "rng": self.generator.get_state(),
        }

    def load_state_dict(self, state):
        """恢复同一批次契约，拒绝非法排列与游标。"""
        if (state["count"], state["batch_size"]) != (self.count, self.batch_size):
            raise ValueError("批次流准备不兼容")
        order = state["order"]
        if sorted(order.tolist()) != list(range(self.count)) or state["offset"] not in range(
            0, self.count + 1, self.batch_size
        ):
            raise ValueError("批次流状态损坏")
        self.order, self.offset = order.clone(), state["offset"]
        self.generator.set_state(state["rng"])
