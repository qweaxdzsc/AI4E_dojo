"""原 ema-pytorch 滑动平均适配，保留预热和计数器。"""

from ema_pytorch import EMA


class MovingAverage:
    """与既有 checkpoint 的 state 属性交接，不改原 EMA 更新算术。"""

    def __init__(self, model, *, beta=0.995, update_every=10):
        self.average = EMA(model, beta=beta, update_every=update_every).to(
            next(model.parameters()).device
        )

    def update(self, model=None):
        """在优化器与调度器完成后更新。"""
        self.average.update()

    @property
    def model(self):
        """返回独立平均权重模型。"""
        return self.average.ema_model

    @property
    def state(self):
        """完整记录原 EMA 的初始化、步数、在线权重和平均权重。"""
        return self.average.state_dict()

    @state.setter
    def state(self, value):
        self.average.load_state_dict(value, strict=True)
