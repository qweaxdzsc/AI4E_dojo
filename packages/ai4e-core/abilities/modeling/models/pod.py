"""公共降维块组成的完整 POD 表示；不隐式预测未知系数。"""

from ai4e_core.abilities.modeling.modules.reduced_basis import ReducedBasis


class POD:
    """拟合与使用分离；representation 可替换为满足本地编码/解码约定的对象。"""

    def __init__(self, state: dict | None = None, *, representation=None) -> None:
        if (state is None) == (representation is None):
            raise ValueError("显式提供 state 或 representation 其中一个")
        self.representation = ReducedBasis(state) if representation is None else representation

    def encode(self, value):
        """使用公共表示编码场的最后一轴。"""
        return self.representation.encode(value)

    def decode(self, value):
        """使用公共表示解码系数的最后一轴。"""
        return self.representation.decode(value)

    def reconstruct(self, value):
        """先编码后重建，不修改拟合状态。"""
        return self.decode(self.encode(value))

    def to_state(self) -> dict:
        """交付公共表示的可保存状态。"""
        return self.representation.to_state()

    get_state = to_state

    @classmethod
    def from_state(cls, state: dict) -> "POD":
        """通过公共表示的门禁恢复模型。"""
        return cls(state)

    def torch_decoder(self, **kwargs):
        """交付与本模型相同状态的可微冻结解码器。"""
        return self.representation.torch_decoder(**kwargs)
