"""本地时序用户组件：可恢复窗口流、八块可微滚动及科学目标。"""

import numpy as np
import torch

from ai4e_core.abilities.constraint.compare import compare
from ai4e_core.abilities.data.extract.time_windows import window_slices
from ai4e_core.abilities.data.save.array_manifest import read_arrays


class WindowStream:
    """每个 epoch 先取起点再打乱轨迹；支持尾批与可选混合起点。"""

    def __init__(self, count, batch_size, *, seed, mixed=False):
        self.count, self.batch_size, self.mixed = count, batch_size, mixed
        self.rng = np.random.Generator(np.random.PCG64(seed))
        self.cursor, self.epoch, self.starts, self.order = count, 0, None, None

    def next(self):
        """交付轨迹序号与窗口起点，随机流仅在轮界推进。"""
        if self.cursor == self.count:
            self.starts = self.rng.integers(0, 162, size=self.count)
            if self.mixed:
                anchors = self.rng.choice([0, 80, 161], size=self.count)
                self.starts = np.where(self.rng.random(self.count) < 0.5, anchors, self.starts)
            self.order = self.rng.permutation(self.count)
            self.cursor, self.epoch = 0, self.epoch + 1
        ids = self.order[self.cursor : min(self.cursor + self.batch_size, self.count)]
        self.cursor += len(ids)
        return [(int(i), int(self.starts[i])) for i in ids]

    def state_dict(self):
        """保存精确游标与 PCG64 状态，训练器负责冻结。"""
        return {
            "rng": self.rng.bit_generator.state,
            "cursor": self.cursor,
            "epoch": self.epoch,
            "starts": self.starts,
            "order": self.order,
        }

    def load_state_dict(self, state):
        """恢复显式状态；不重新抽样。"""
        if not 0 <= state["cursor"] <= self.count:
            raise ValueError("窗口游标非法")
        self.rng.bit_generator.state = state["rng"]
        for key in ["cursor", "epoch", "starts", "order"]:
            setattr(self, key, state[key])


class WindowBatch:
    """带摘要的准备缓存只打开一次，每批只堆叠选中的窗口。"""

    def __init__(self, records, device):
        self.data = [
            read_arrays(r["manifest"], kind="rmhd-normalized-v1")[1]["values"] for r in records
        ]
        self.device = device

    def __call__(self, ids):
        values = []
        for i, start in ids:
            history, future = window_slices(start, 211, 10, 40)
            values.append(self.data[i][history.start : future.stop])
        return torch.from_numpy(np.stack(values)).to(self.device)


def predict_blocks(model, history):
    """八次5帧预测；保持全部计算图，不使用未来真值回填。"""
    predictions = []
    for _ in range(8):
        block = model(history.flatten(1, 2)).reshape(len(history), 5, 6, 100, 100)
        predictions.append(block)
        history = torch.cat([history[:, 5:], block], dim=1)
    return torch.cat(predictions, dim=1)


def block_mse(model, values):
    """八块等尺寸，完整40帧 MSE 等价于等权块损失；保持全部滚动梯度。"""
    return compare(predict_blocks(model, values[:, :10]), values[:, 10:], method="mse")


def direct_prediction(model, history):
    """一次返回40帧的自定义网络采用相同推理交接。"""
    return model(history)


class RelativeObjective:
    """最终轮逐样本逐场相对RMSE；全局 compare 不具有相同归约语义。"""

    def __init__(self, stats, device):
        self.offset = torch.tensor(
            np.array(stats["mean"]) / np.array(stats["std"]), dtype=torch.float32, device=device
        ).reshape(1, 1, 6, 1, 1)

    def __call__(self, model, values):
        target, prediction = values[:, 10:], model(values[:, :10])
        numerator = (prediction - target).square().mean(dim=(1, 3, 4))
        denominator = (target + self.offset).square().mean(dim=(1, 3, 4)).clamp_min(1e-12)
        return (numerator / denominator + 1e-12).sqrt().mean()
