"""按块轮换留出验证集的可恢复样本流；使用 Python 全局随机流。"""

import random


class RotatingChunkStream:
    """块内顺序不变，每轮对上一轮块顺序洗牌并留出最后一块。"""

    def __init__(self, chunks, samples_per_chunk):
        if len(chunks) < 2 or samples_per_chunk < 1 or len(set(chunks)) != len(chunks):
            raise ValueError("轮换流至少需要两个独立分块")
        self.chunks = list(chunks)
        self.samples_per_chunk = samples_per_chunk
        self.epoch = 0
        self.cursor = 0
        self.steps = (len(chunks) - 1) * samples_per_chunk

    def next(self):
        """返回块身份、块内样本位置和从1起算的轮次。"""
        if self.epoch == 0 or self.cursor == self.steps:
            random.shuffle(self.chunks)
            self.epoch += 1
            self.cursor = 0
        chunk = self.chunks[self.cursor // self.samples_per_chunk]
        row = self.cursor % self.samples_per_chunk
        self.cursor += 1
        return chunk, row, self.epoch

    def state_dict(self):
        """记录已有排列和下一样本游标，RNG由共享检查点保存。"""
        return {
            "chunks": list(self.chunks),
            "samples_per_chunk": self.samples_per_chunk,
            "epoch": self.epoch,
            "cursor": self.cursor,
        }

    def load_state_dict(self, state):
        """拒绝来源或轮次游标不相容的状态。"""
        if (
            sorted(state["chunks"]) != sorted(self.chunks)
            or state["samples_per_chunk"] != self.samples_per_chunk
        ):
            raise ValueError("轮换流来源不一致")
        if not 0 <= state["cursor"] <= self.steps or state["epoch"] < 0:
            raise ValueError("轮换流游标非法")
        self.chunks = list(state["chunks"])
        self.epoch = state["epoch"]
        self.cursor = state["cursor"]
