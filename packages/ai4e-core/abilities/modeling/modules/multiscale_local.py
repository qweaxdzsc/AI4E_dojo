# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""多尺度局部邻域编码；参考定义和本地修正记录见包内 Notice/physicsnemo/source.json。"""

from __future__ import annotations

import torch
from einops import rearrange
from torch import nn

te = None
TE_AVAILABLE = False
from ai4e_core.abilities.geometry.radius_query import BallQuery as BQWarp

from .context_projection import ContextProjector
from .projected_mlp import Mlp


class GeometricFeatureProcessor(nn.Module):
    """可独立使用的GeometricFeatureProcessor计算组件。

    Processes geometric features at a single spatial scale using BQWarp.

    This is a simple, reusable component that handles neighbor querying and
    feature processing for one radius scale. It encapsulates the BQWarp +
    MLP pattern used throughout the model.

    Parameters
    ----------
    radius : float
        Query radius for neighbor search.
    neighbors_in_radius : int
        Maximum number of neighbors within the radius.
    feature_dim : int
        Dimension of the input features to query.
    hidden_dim : int
        Output dimension after MLP processing.

    Forward
    -------
    query_points : torch.Tensor
        Query coordinates of shape :math:`(B, N, 3)` where :math:`B` is batch size
        and :math:`N` is number of query points.
    key_features : torch.Tensor
        Features to query from of shape :math:`(B, N, C)` where :math:`C` is
        ``feature_dim``.

    Outputs
    -------
    torch.Tensor
        Processed features of shape :math:`(B, N, D)` where :math:`D` is ``hidden_dim``.

    See Also
    --------
    :class:`MultiScaleFeatureExtractor` : Uses multiple GeometricFeatureProcessor instances.
    :class:`~physicsnemo.nn.BQWarp` : The ball query operation used internally.

    Examples
    --------
    >>> import torch
    >>> processor = GeometricFeatureProcessor(
    ...     radius=0.1, neighbors_in_radius=16, feature_dim=3, hidden_dim=64
    ... )
    >>> query_points = torch.randn(2, 100, 3)  # (batch, points, xyz)
    >>> key_features = torch.randn(2, 100, 3)  # (batch, points, features)
    >>> output = processor(query_points, key_features)
    >>> output.shape
    torch.Size([2, 100, 64])"""

    def __init__(
        self, radius: float, neighbors_in_radius: int, feature_dim: int, hidden_dim: int
    ) -> None:
        super().__init__()
        self.bq_warp = BQWarp(radius=radius, neighbors_in_radius=neighbors_in_radius)
        self.mlp = Mlp(
            in_features=feature_dim * neighbors_in_radius,
            hidden_features=[hidden_dim, hidden_dim // 2],
            out_features=hidden_dim,
            act_layer=nn.GELU,
            drop=0.0,
        )

    def forward(self, query_points: torch.Tensor, key_features: torch.Tensor) -> torch.Tensor:
        """执行forward；张量布局、参数与返回值见下列参考说明。

        Query neighbors and process features.

        Parameters
        ----------
        query_points : torch.Tensor
            Query coordinates of shape :math:`(B, N, 3)` where :math:`B` is batch size
            and :math:`N` is number of query points.
        key_features : torch.Tensor
            Features to query from of shape :math:`(B, N, C)` where :math:`C` is the
            feature dimension.

        Returns
        -------
        torch.Tensor
            Processed features of shape :math:`(B, N, D)` where :math:`D` is the
            hidden dimension."""
        if not torch.compiler.is_compiling():
            if query_points.ndim != 3:
                raise ValueError(
                    f"Expected 3D query_points tensor (B, N, 3), got {query_points.ndim}D tensor with shape {tuple(query_points.shape)}"
                )
            if key_features.ndim != 3:
                raise ValueError(
                    f"Expected 3D key_features tensor (B, N, C), got {key_features.ndim}D tensor with shape {tuple(key_features.shape)}"
                )
        _, neighbors = self.bq_warp(query_points, key_features)
        neighbors_flat = rearrange(neighbors, "b n k c -> b n (k c)")
        return torch.nn.functional.tanh(self.mlp(neighbors_flat))


class MultiScaleFeatureExtractor(nn.Module):
    """可独立使用的MultiScaleFeatureExtractor计算组件。

    Multi-scale geometric feature extraction with minimal complexity.

    Manages multiple GeometricFeatureProcessor instances for different radii.
    Provides both tokenized context and concatenated local features.

    Parameters
    ----------
    geometry_dim : int
        Dimension of geometry features.
    radii : list[float]
        Radii for multi-scale processing.
    neighbors_in_radius : list[int]
        Neighbors per radius (must have same length as ``radii``).
    hidden_dim : int
        Hidden dimension for processing.
    n_head : int
        Number of attention heads.
    dim_head : int
        Dimension per head.
    dropout : float, optional
        Dropout rate. Default is 0.0.
    slice_num : int, optional
        Number of slices for context tokenization. Default is 64.
    use_te : bool, optional
        Whether to use Transformer Engine. Default is ``False``.
    plus : bool, optional
        Whether to use Transolver++ features. Default is ``False``.

    Forward
    -------
    This class does not implement a standard ``forward`` method. Instead, use:

    - :meth:`extract_context_features`: Get tokenized features for GALE context.
    - :meth:`extract_local_features`: Get concatenated features for local pathway.

    See Also
    --------
    :class:`GeometricFeatureProcessor` : Single-scale processor used by this class.
    :class:`ContextProjector` : Tokenizer used for context features.
    :class:`GlobalContextBuilder` : High-level builder that uses this class.

    Examples
    --------
    >>> import torch
    >>> extractor = MultiScaleFeatureExtractor(
    ...     geometry_dim=3,
    ...     radii=[0.05, 0.25],
    ...     neighbors_in_radius=[8, 32],
    ...     hidden_dim=32,
    ...     n_head=8,
    ...     dim_head=32,
    ...     use_te=False,
    ... )
    >>> spatial_coords = torch.randn(2, 100, 3)
    >>> geometry = torch.randn(2, 100, 3)
    >>> context_feats = extractor.extract_context_features(spatial_coords, geometry)
    >>> len(context_feats)  # One per scale
    2
    >>> local_feats = extractor.extract_local_features(spatial_coords, geometry)
    >>> local_feats.shape  # Concatenated across scales
    torch.Size([2, 100, 64])"""

    def __init__(
        self,
        geometry_dim: int,
        radii: list[float],
        neighbors_in_radius: list[int],
        hidden_dim: int,
        n_head: int,
        dim_head: int,
        dropout: float = 0.0,
        slice_num: int = 64,
        use_te: bool = False,
        plus: bool = False,
        concrete_dropout: bool = False,
    ) -> None:
        if use_te or plus or concrete_dropout:
            raise NotImplementedError("当前移植仅支持普通 PyTorch GALE、无混合精度扩展及无时间条件")
        super().__init__()
        self.num_scales = len(radii)
        self.processors = nn.ModuleList(
            [
                GeometricFeatureProcessor(
                    radii[i], neighbors_in_radius[i], geometry_dim, hidden_dim
                )
                for i in range(self.num_scales)
            ]
        )
        self.tokenizers = nn.ModuleList(
            [
                ContextProjector(
                    hidden_dim,
                    n_head,
                    dim_head,
                    dropout,
                    slice_num,
                    use_te,
                    plus,
                    concrete_dropout=concrete_dropout,
                )
                for _ in range(self.num_scales)
            ]
        )

    def extract_context_features(
        self, spatial_coords: torch.Tensor, geometry: torch.Tensor
    ) -> list[torch.Tensor]:
        """执行extract_context_features；张量布局、参数与返回值见下列参考说明。

        Extract and tokenize features for context.

        Parameters
        ----------
        spatial_coords : torch.Tensor
            Spatial coordinates of shape :math:`(B, N, 3)`.
        geometry : torch.Tensor
            Geometry features of shape :math:`(B, N, C_{geo})`.

        Returns
        -------
        list[torch.Tensor]
            List of tokenized context features, one per scale, each of shape
            :math:`(B, H, S, D)`."""
        return [
            tokenizer(processor(spatial_coords, geometry))
            for processor, tokenizer in zip(self.processors, self.tokenizers)
        ]

    def extract_local_features(
        self, spatial_coords: torch.Tensor, geometry: torch.Tensor
    ) -> torch.Tensor:
        """执行extract_local_features；张量布局、参数与返回值见下列参考说明。

        Extract and concatenate features for local pathway.

        Parameters
        ----------
        spatial_coords : torch.Tensor
            Spatial coordinates of shape :math:`(B, N, 3)`.
        geometry : torch.Tensor
            Geometry features of shape :math:`(B, N, C_{geo})`.

        Returns
        -------
        torch.Tensor
            Concatenated local features of shape :math:`(B, N, D_{total})` where
            :math:`D_{total}` is ``hidden_dim * num_scales``."""
        return torch.cat(
            [processor(geometry, spatial_coords) for processor in self.processors], dim=-1
        )
