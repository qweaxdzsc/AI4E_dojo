"""固定输入传感器、显式查询布局的中立 DeepONet 架构。

本地组合公开 FeedForward 与 BranchTrunkReadout；算法来源为
Lu 等 arXiv:1910.03193，参考实现的许可与版本由独立核对工具记录。
"""

from torch import Tensor, nn

from ai4e_core.abilities.modeling.modules.branch_trunk import BranchTrunkReadout
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward


class DeepONet(nn.Module):
    """分支编码固定传感器，主干编码查询，末层激活由主干明确提供。

    自定义 branch/trunk/readout 均正常注册；自定义主干自行负责末层激活。
    传感器选择、排列和缺失支撑属于调用方，本类不缓存分支或切断梯度。
    """

    def __init__(
        self,
        sensor_features: int,
        query_dim: int,
        latent_dim: int,
        out_channels: int = 1,
        multi_output: str | None = None,
        *,
        branch_hidden: tuple[int, ...] = (64, 64),
        trunk_hidden: tuple[int, ...] = (64, 64),
        activation: str = "tanh",
        trunk_final_activation: str | None = "tanh",
        branch: nn.Module | None = None,
        trunk: nn.Module | None = None,
        readout: nn.Module | None = None,
    ) -> None:
        super().__init__()
        if any(type(n) is not int or n <= 0 for n in (sensor_features, query_dim)):
            raise ValueError("sensor_features 和 query_dim 须为正整数")
        contract = BranchTrunkReadout(latent_dim, out_channels, multi_output)
        self.sensor_features, self.query_dim = sensor_features, query_dim
        self.out_channels = out_channels
        self.branch = (
            branch
            if branch is not None
            else FeedForward(sensor_features, contract.branch_width, branch_hidden, activation)
        )
        self.trunk = (
            trunk
            if trunk is not None
            else FeedForward(
                query_dim,
                contract.trunk_width,
                trunk_hidden,
                activation,
                final_activation=trunk_final_activation,
            )
        )
        self.readout = readout if readout is not None else contract
        if any(not isinstance(m, nn.Module) for m in (self.branch, self.trunk, self.readout)):
            raise TypeError("branch/trunk/readout 须为 nn.Module")

    def forward(
        self, branch_input: Tensor, queries: Tensor, *, query_layout: str = "shared"
    ) -> Tensor:
        """返回 [B,Q,O]；输入为 [B,F] 与 [Q,D] 或 [B,Q,D]。

        可改变查询集合；改变固定传感器含义需重新准备并记录模型配置。
        """
        if branch_input.ndim != 2 or branch_input.shape[-1] != self.sensor_features:
            raise ValueError(f"分支输入须为 [B,{self.sensor_features}]")
        if query_layout not in ("shared", "per_sample"):
            raise ValueError("query_layout 须为 shared 或 per_sample")
        rank = 2 if query_layout == "shared" else 3
        if queries.ndim != rank or queries.shape[-1] != self.query_dim:
            raise ValueError(f"查询须为 {rank} 维且末轴为 {self.query_dim}")
        if query_layout == "per_sample" and queries.shape[0] != branch_input.shape[0]:
            raise ValueError("逐样本查询批次数须相同")
        branch = self.branch(branch_input)
        if query_layout == "per_sample" and type(self.trunk) is FeedForward:
            # 此公开组件逐点作用于末轴，明确使用二维线性映射避免非连续[B,Q,D]
            # 与[Q,D]触发不同矩阵内核。仅适用于精确FeedForward类；用户主干及
            # 子类可能有跨查询耦合，必须保留其原样本/查询轴，不能盲目展平。
            trunk = self.trunk(queries.reshape(-1, self.query_dim)).reshape(
                *queries.shape[:-1], self.trunk.out_features
            )
        else:
            trunk = self.trunk(queries)
        result = self.readout(branch, trunk, query_layout=query_layout)
        if result.shape != (branch_input.shape[0], queries.shape[-2], self.out_channels):
            raise ValueError("readout 须返回 [B,Q,out_channels]，禁止隐式布局变化")
        return result
