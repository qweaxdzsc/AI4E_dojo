"""中立分支—主干内积读出，显式区分样本、查询与输出分组。

本地按 DeepONet 数学定义独立实现；参考 Lu 等 arXiv:1910.03193。
不复制作者原仓库或 DeepXDE 的受许可源码。
"""

import torch
from torch import Tensor, nn


class BranchTrunkReadout(nn.Module):
    """将分支和主干特征映射到 ``[B,Q,O]``，K 为每输出潜变量宽度。

    单输出必须使用 ``multi_output=None``；多输出必须显式选择
    ``split_branch``、``split_trunk`` 或 ``split_both``。不推断查询布局。
    """

    def __init__(
        self,
        latent_dim: int,
        out_channels: int = 1,
        multi_output: str | None = None,
        bias: bool = True,
    ) -> None:
        super().__init__()
        if any(type(n) is not int or n <= 0 for n in (latent_dim, out_channels)):
            raise ValueError("latent_dim 和 out_channels 须为正整数")
        choices = ("split_branch", "split_trunk", "split_both")
        if (out_channels == 1 and multi_output is not None) or (
            out_channels > 1 and multi_output not in choices
        ):
            raise ValueError("单输出使用 None，多输出须声明 split_branch/trunk/both")
        self.latent_dim, self.out_channels = latent_dim, out_channels
        self.multi_output = multi_output
        self.branch_width = latent_dim * (
            out_channels if multi_output in ("split_branch", "split_both") else 1
        )
        self.trunk_width = latent_dim * (
            out_channels if multi_output in ("split_trunk", "split_both") else 1
        )
        self.bias = nn.Parameter(torch.zeros(out_channels)) if bias else None

    def forward(
        self, branch_features: Tensor, trunk_features: Tensor, *, query_layout: str
    ) -> Tensor:
        """融合 ``[B,K或O*K]`` 和共享 ``[Q,*]`` 或逐样本 ``[B,Q,*]``。

        ``query_layout`` 仅接受 shared/per_sample；非法宽度、批次或秩抛
        ValueError。成对查询显式表达为 per_sample 的 Q=1。
        """
        if query_layout not in ("shared", "per_sample"):
            raise ValueError("query_layout 须为 shared 或 per_sample")
        if branch_features.ndim != 2 or branch_features.shape[-1] != self.branch_width:
            raise ValueError(f"分支须为 [B,{self.branch_width}]")
        rank = 2 if query_layout == "shared" else 3
        if trunk_features.ndim != rank or trunk_features.shape[-1] != self.trunk_width:
            raise ValueError(f"主干须为 {rank} 维，末轴为 {self.trunk_width}")
        if query_layout == "per_sample" and trunk_features.shape[0] != branch_features.shape[0]:
            raise ValueError("逐样本查询批次数须与分支相同，禁止广播")
        outputs = []
        equation = "bk,qk->bq" if query_layout == "shared" else "bk,bqk->bq"
        for output in range(self.out_channels):
            part = slice(output * self.latent_dim, (output + 1) * self.latent_dim)
            branch = (
                branch_features[:, part]
                if self.multi_output in ("split_branch", "split_both")
                else branch_features
            )
            trunk = (
                trunk_features[..., part]
                if self.multi_output in ("split_trunk", "split_both")
                else trunk_features
            )
            # 保留逐输出内积及梯度归约顺序。把输出轴合并进一次einsum虽然
            # 数学等价，FP32共享主干的反向求和仍可能沿不同次序累积舍入误差。
            value = torch.einsum(equation, branch, trunk)
            if self.bias is not None:
                # value是本次新计算，原位偏置不修改输入；同时保持上游偏置
                # 反向归约路径，避免大查询集的FP32偏置梯度采用另一求和顺序。
                value += self.bias[output : output + 1]
            outputs.append(value)
        return torch.stack(outputs, dim=-1)
