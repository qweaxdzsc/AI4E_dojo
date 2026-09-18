"""可恢复原 Torch RandomSampler 单进程索引顺序。"""

import torch


class SourceStream:
    """保存排列和游标；按原 DataLoader 消耗全局 CPU 的两个种子。"""

    def __init__(self, count: int, batch_size: int):
        if count < 1 or batch_size < 1:
            raise ValueError("样本数与批量必须为正")
        self.count, self.batch_size, self.offset = count, batch_size, count
        self.order = torch.arange(count)

    def next(self):
        if self.offset == self.count:
            # DataLoader iterator base_seed，然后 RandomSampler 自己的 seed。
            torch.empty((), dtype=torch.int64).random_()
            seed = int(torch.empty((), dtype=torch.int64).random_().item())
            self.order = torch.randperm(self.count, generator=torch.Generator().manual_seed(seed))
            self.offset = 0
        end = min(self.offset + self.batch_size, self.count)
        result = self.order[self.offset : end]
        self.offset = end
        return result

    def state_dict(self):
        return {
            "count": self.count,
            "batch_size": self.batch_size,
            "offset": self.offset,
            "order": self.order.clone(),
        }

    def load_state_dict(self, state):
        if (state["count"], state["batch_size"]) != (self.count, self.batch_size):
            raise ValueError("数据流契约变化")
        if sorted(state["order"].tolist()) != list(range(self.count)) or not (
            state["offset"] == self.count
            or 0 <= state["offset"] < self.count
            and state["offset"] % self.batch_size == 0
        ):
            raise ValueError("数据流排列或游标非法")
        self.order, self.offset = state["order"].clone(), state["offset"]
