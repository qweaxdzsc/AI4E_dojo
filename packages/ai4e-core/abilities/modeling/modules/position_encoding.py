"""AB-UPT 来源组件；本地修改为包内导入，来源与 ENPL 许可见贡献组件 LICENSE。"""

import einops
import torch
from torch import nn


class ContinuousSincosEmbed(nn.Module):
    """Embedding layer for continuous coordinates using sine and cosine functions as used in transformers.
    This implementation is able to deal with arbitrary coordinate dimensions (e.g., 2D and 3D coordinate systems).

    Args:
        dim: Dimensionality of the embedded input coordinates.
        ndim: Number of dimensions of the input domain.
        max_wavelength: Max length. Defaults to 10000.
        assert_positive: If true, assert if all input coordiantes are positive. Defaults to True.
    """

    def __init__(
        self,
        dim: int,
        ndim: int,
        max_wavelength: int = 10000,
        assert_positive: bool = True,
    ):
        super().__init__()
        self.dim = dim
        self.ndim = ndim
        # if dim is not cleanly divisible -> cut away trailing dimensions
        self.ndim_padding = dim % ndim
        dim_per_ndim = (dim - self.ndim_padding) // ndim
        self.sincos_padding = dim_per_ndim % 2
        self.max_wavelength = max_wavelength
        self.padding = self.ndim_padding + self.sincos_padding * ndim
        self.assert_positive = assert_positive
        effective_dim_per_wave = (self.dim - self.padding) // ndim
        assert effective_dim_per_wave > 0
        arange = torch.arange(0, effective_dim_per_wave, 2, dtype=torch.float32)
        self.register_buffer(
            "omega",
            1.0 / max_wavelength ** (arange / effective_dim_per_wave),
        )

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """Forward method of the ContinuousSincosEmbed layer.

        Args:
            coords: Tensor of coordinates. The shape of the tensor should be
                (batch size, number of points, coordinate dimension) or (number of points, coordinate dimension).

        Returns:
            Tensor with embedded coordinates.
        """
        if self.assert_positive:
            # check if coords are positive
            assert torch.all(coords >= 0)
        # fp32 to avoid numerical imprecision
        coords = coords.float()
        with torch.autocast(device_type=str(coords.device).split(":")[0], enabled=False):
            coordinate_ndim = coords.shape[-1]
            assert self.ndim == coordinate_ndim
            out = coords.unsqueeze(-1) @ self.omega.unsqueeze(0)
            emb = torch.concat([torch.sin(out), torch.cos(out)], dim=-1)
            if coords.ndim == 3:
                emb = einops.rearrange(emb, "bs num_points ndim dim -> bs num_points (ndim dim)")
            elif coords.ndim == 2:
                emb = einops.rearrange(emb, "num_points ndim dim -> num_points (ndim dim)")
            else:
                raise NotImplementedError
        if self.padding > 0:
            padding = torch.zeros(*emb.shape[:-1], self.padding, device=emb.device, dtype=emb.dtype)
            emb = torch.concat([emb, padding], dim=-1)
        return emb


class RopeFrequency(nn.Module):
    """Creates frequencies for rotary embeddings (RoPE) from https://arxiv.org/abs/2104.09864 for variable positions.

    Args:
        dim: Dimensionality of frequencies (in transformers this should be the head dimension).
        ndim: Dimensionality of the coordinates (e.g., 2 for 2D coordinates, 3 for 3D coordinates).
        max_wavelength: Theta parameter for the transformer sine/cosine embedding. Default: 10000.0
        assert_positive: Makes sure that coordinates were rescaled to be positive only. Default: True
    """

    def __init__(
        self,
        dim: int,
        ndim: int,
        max_wavelength: int = 10000.0,
        assert_positive: bool = True,
    ):
        super().__init__()
        self.dim = dim
        self.ndim = ndim
        # if dim is not cleanly divisible -> cut away trailing dimensions
        self.ndim_padding = dim % ndim
        dim_per_ndim = (dim - self.ndim_padding) // ndim
        self.sincos_padding = dim_per_ndim % 2
        self.max_wavelength = max_wavelength
        self.padding = self.ndim_padding + self.sincos_padding * ndim
        self.assert_positive = assert_positive
        effective_dim_per_wave = (self.dim - self.padding) // ndim
        assert effective_dim_per_wave > 0
        arange = torch.arange(0, effective_dim_per_wave, 2, dtype=torch.float)
        self.register_buffer(
            "omega",
            1.0 / max_wavelength ** (arange / effective_dim_per_wave),
        )

    def forward(self, coords: torch.Tensor) -> torch.Tensor:
        """生成与坐标同设备的复数旋转频率，不隐式跨设备计算。"""
        if self.assert_positive:
            # check if coords are positive
            assert torch.all(coords >= 0), (
                f"coords.shape={coords.shape} coords.min={coords.min(dim=-2).values} "
                f"coords.max={coords.max(dim=-2).values} numel={coords.numel()} is_positive.numel={(coords > 0).sum()}"
            )

        with torch.autocast(device_type=str(coords.device).split(":")[0], enabled=False):
            coordinate_ndim = coords.shape[-1]
            assert self.ndim == coordinate_ndim
            out = coords.float().unsqueeze(-1) @ self.omega.unsqueeze(0)
        out = einops.rearrange(out, "... ndim dim -> ... (ndim dim)")
        # add padding
        assert self.padding % 2 == 0
        out = torch.concat(
            [out, torch.zeros(*out.shape[:-1], self.padding // 2, device=coords.device)], dim=-1
        )
        # 频率保留在模型设备；当前 MPS 支持复数，避免跨设备舍入与传输。
        return torch.polar(torch.ones_like(out), out)
