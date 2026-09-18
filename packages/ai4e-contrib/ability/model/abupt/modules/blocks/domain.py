"""共享权重的域注意力、条件调制与独立 K/V 投影。"""

import einops
from torch import nn
from torch.nn import functional as F

from ai4e_core.abilities.modeling.modules.feed_forward import Mlp

from ..rope import rope


class Modulation(nn.Module):
    """零初始化缩放平移，未启用条件时保持恒等。"""

    def __init__(self, dim, enabled):
        super().__init__()
        self.linear = nn.Linear(dim, 2 * dim) if enabled else None
        if self.linear is not None:
            nn.init.zeros_(self.linear.weight)
            nn.init.zeros_(self.linear.bias)

    def forward(self, x, condition):
        if self.linear is None:
            return x
        shift, scale = self.linear(condition).unsqueeze(1).chunk(2, dim=-1)
        return x * (1 + scale) + shift


def initialize_linear(module):
    """局部线性层截断正态初始化；构造顺序属于可复现模型行为。"""
    if isinstance(module, nn.Linear):
        nn.init.trunc_normal_(module.weight, std=0.02)
        if module.bias is not None:
            nn.init.zeros_(module.bias)


class KVProjection(nn.Module):
    """独立键值参数，共同投影接口供缓存跳过计数。"""

    def __init__(self, dim):
        super().__init__()
        self.k = nn.Linear(dim, dim)
        self.v = nn.Linear(dim, dim)

    def forward(self, x):
        import torch

        # 使用官方相同的联合矩阵乘，保留独立参数及初始化顺序。
        return F.linear(
            x, torch.cat([self.k.weight, self.v.weight]), torch.cat([self.k.bias, self.v.bias])
        )


class DomainBlock(nn.Module):
    """每域共享 Q/K/V 与前馈；queries 从不成为 K/V。"""

    def __init__(self, dim, heads, conditioned=False, *, perceiver=False):
        super().__init__()
        self.heads = heads
        # 参数注册顺序决定梯度裁剪的浮点归约顺序。
        self.norm_q = nn.RMSNorm(dim, eps=1e-6, elementwise_affine=not conditioned)
        self.norm_kv = (
            nn.RMSNorm(dim, eps=1e-6, elementwise_affine=not conditioned)
            if perceiver
            else self.norm_q
        )
        if perceiver:
            self.kv = KVProjection(dim)
            self.q = nn.Linear(dim, dim)
        else:
            self.q = nn.Linear(dim, dim)
            self.kv = KVProjection(dim)
        self.proj = nn.Linear(dim, dim)
        for module in (
            [self.kv.k, self.kv.v, self.q, self.proj]
            if perceiver
            else [self.q, self.kv.k, self.kv.v, self.proj]
        ):
            initialize_linear(module)
        self.norm_mlp = nn.RMSNorm(dim, eps=1e-6, elementwise_affine=not conditioned)
        self.mod_q = Modulation(dim, conditioned)
        self.mod_kv = Modulation(dim, conditioned)
        self.mod_mlp = Modulation(dim, conditioned)
        self.mlp = Mlp(dim)
        self.mlp.apply(initialize_linear)

    def heads_view(self, x):
        """把通道维拆为注意力头，保持 token 行顺序。"""
        return x.reshape(x.shape[0], x.shape[1], self.heads, -1).transpose(1, 2)

    def project_kv(self, x, frequencies, condition):
        """仅在完整前向或预填充时投影键值。"""
        projected = self.kv(self.mod_kv(self.norm_kv(x), condition))
        k, v = einops.rearrange(
            projected, "b s (two h d) -> two b h s d", two=2, h=self.heads
        ).unbind(0)
        return rope(k, freqs=frequencies), v

    def forward(
        self,
        x,
        frequencies=None,
        kv=None,
        condition=None,
        *,
        kind=None,
        geometry=None,
        geometry_frequencies=None,
        cache=None,
    ):
        """模块入口：字典走多域路径，张量走单域注意力，供 TorchVista 收成模块盒。"""
        if isinstance(x, dict):
            return self.forward_domains(
                x,
                frequencies,
                kv,
                kind=kind,
                geometry=geometry,
                geometry_frequencies=geometry_frequencies,
                cache=cache,
            )
        q = rope(self.heads_view(self.q(self.mod_q(self.norm_q(x), condition))), freqs=frequencies)
        value = F.scaled_dot_product_attention(q, *kv).transpose(1, 2).flatten(2)
        x = x + self.proj(value)
        return x + self.mlp(self.mod_mlp(self.norm_mlp(x), condition))

    def forward_domains(
        self,
        values,
        frequencies,
        anchors,
        *,
        kind,
        geometry=None,
        geometry_frequencies=None,
        cache=None,
    ):
        """无条件官方路径：联合投影、按同形注意力收批，再统一残差与前馈。"""
        import torch

        names = list(values)
        sizes = [values[d].shape[1] for d in names]
        x = torch.cat([values[d] for d in names], dim=1)
        freq = torch.cat([frequencies[d] for d in names], dim=1)
        normalized = self.norm_q(x)
        if kind == "p":
            q = rope(self.heads_view(self.q(normalized)), freqs=freq)
            layer = (
                cache
                if cache is not None
                else {"geometry": self.project_kv(geometry, geometry_frequencies, None)}
            )
        elif cache is not None:
            q = rope(self.heads_view(self.q(normalized)), freqs=freq)
            layer = cache
        else:
            combined = F.linear(
                normalized,
                torch.cat([self.q.weight, self.kv.k.weight, self.kv.v.weight]),
                torch.cat([self.q.bias, self.kv.k.bias, self.kv.v.bias]),
            )
            q, k, v = einops.rearrange(
                combined, "b s (three h d) -> three b h s d", three=3, h=self.heads
            ).unbind(0)
            q, k = rope(q, freqs=freq), rope(k, freqs=freq)
            ks, vs = k.split(sizes, dim=2), v.split(sizes, dim=2)
            layer = {
                d: (ks[i][:, :, : anchors[d]], vs[i][:, :, : anchors[d]])
                for i, d in enumerate(names)
            }
        queries = dict(zip(names, q.split(sizes, dim=2), strict=True))
        if kind == "p":
            attended = F.scaled_dot_product_attention(q, *layer["geometry"])
        else:
            patterns = {}
            for d in names:
                sources = [d] if kind == "s" else [other for other in layer if other != d]
                keys, vals = [
                    torch.cat([layer[source][j] for source in sources], dim=2) for j in (0, 1)
                ]
                patterns.setdefault((queries[d].shape[2], keys.shape[2]), []).append(
                    (d, queries[d], keys, vals)
                )
            outputs = {}
            for group in patterns.values():
                args = [torch.cat([item[j] for item in group], dim=0) for j in (1, 2, 3)]
                chunks = F.scaled_dot_product_attention(*args).chunk(len(group), dim=0)
                outputs.update({item[0]: chunk for item, chunk in zip(group, chunks, strict=True)})
            attended = torch.cat([outputs[d] for d in names], dim=2)
        x = x + self.proj(attended.transpose(1, 2).flatten(2))
        x = x + self.mlp(self.norm_mlp(x))
        return dict(zip(names, x.split(sizes, dim=1), strict=True)), layer


class DomainReadout(nn.Module):
    """域输出头：归一化与投影共同注册，保留数值归约的参数顺序。"""

    def __init__(self, dim, outputs, conditioned=False):
        super().__init__()
        self.norm = nn.RMSNorm(dim, eps=1e-6, elementwise_affine=not conditioned)
        self.linear = nn.Linear(dim, outputs)
        initialize_linear(self.linear)
        self.modulation = Modulation(dim, conditioned)

    @property
    def out_features(self):
        """该域所有输出字段的总宽度。"""
        return self.linear.out_features

    def forward(self, value, condition=None):
        """归一化并按可选条件调制，再投影到物理字段。"""
        return self.linear(self.modulation(self.norm(value), condition))
