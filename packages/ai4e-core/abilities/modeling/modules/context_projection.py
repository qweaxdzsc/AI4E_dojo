# ruff: noqa: SIM102
# 保留上游条件及异常类型，避免格式修复改变参考行为。
# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""结构化与点云上下文投影；参考定义和本地修正记录见包内 Notice/physicsnemo/source.json。"""

from __future__ import annotations

import torch
from torch import nn
from torch.distributed.tensor.placement_types import Replicate

te = None
TE_AVAILABLE = False
from .physics_attention import _compute_slices_from_projections, _project_input


def _structured_grid_to_conv_input(
    x: torch.Tensor,
    batch: int,
    tokens: int,
    channels: int,
    ndim: int,
    spatial_shape: tuple[int, ...],
) -> torch.Tensor:
    """执行_structured_grid_to_conv_input；张量布局、参数与返回值见下列参考说明。

    Reshape flat token tensor to spatial layout for Conv2d/Conv3d.

    Converts :math:`(B, N, C)` to :math:`(B, C, H, W)` for 2D or
    :math:`(B, C, H, W, D)` for 3D so that structured context projectors
    can apply spatial convolutions. Validates that :math:`N` matches the
    grid size.

    Parameters
    ----------
    x : torch.Tensor
        Input tensor of shape :math:`(B, N, C)` (batch, tokens, channels).
    batch : int
        Batch size :math:`B`.
    tokens : int
        Number of tokens :math:`N` (must equal :math:`H \\\\times W` or
        :math:`H \\\\times W \\\\times D`).
    channels : int
        Channel dimension :math:`C`.
    ndim : int
        Number of spatial dimensions; must be 2 or 3.
    spatial_shape : tuple[int, ...]
        :math:`(H, W)` for 2D or :math:`(H, W, D)` for 3D.

    Returns
    -------
    torch.Tensor
        Reshaped tensor of shape :math:`(B, C, H, W)` or
        :math:`(B, C, H, W, D)` for use as conv input.

    Raises
    ------
    ValueError
        If ``tokens`` does not match the product of ``spatial_shape``."""
    if ndim == 2:
        H, W = spatial_shape
        if tokens != H * W:
            raise ValueError(f"Expected N={H * W} tokens for 2D grid, got N={tokens}")
        return x.view(batch, H, W, channels).permute(0, 3, 1, 2)
    H, W, D = spatial_shape
    if tokens != H * W * D:
        raise ValueError(f"Expected N={H * W * D} tokens for 3D grid, got N={tokens}")
    return x.view(batch, H, W, D, channels).permute(0, 4, 1, 2, 3)


class _SliceToContextMixin:
    """可独立使用的_SliceToContextMixin计算组件。

    Internal mixin providing shared slice-to-context init and slice aggregation.

    Used by :class:`ContextProjector` and :class:`StructuredContextProjector` to
    avoid duplicating ``in_project_slice``, ``temperature``, ``proj_temperature``,
    and the call to
    :func:`~physicsnemo.nn.module.physics_attention._compute_slices_from_projections`."""

    def _init_slice_components(
        self, dim_head: int, slice_num: int, heads: int, use_te: bool, plus: bool
    ) -> None:
        """执行_init_slice_components；张量布局、参数与返回值见下列参考说明。

        Initialize slice projection, temperature, and optional adaptive temperature.

        Sets ``in_project_slice``, ``temperature``, and (when ``plus`` is True)
        ``proj_temperature`` on this instance. Uses Transformer Engine linear
        when ``use_te`` is True and TE is available.

        Parameters
        ----------
        dim_head : int
            Head dimension for the slice projection input.
        slice_num : int
            Number of slices (output dimension of ``in_project_slice``).
        heads : int
            Number of heads (used for temperature shape).
        use_te : bool
            Whether to prefer Transformer Engine for linear layers.
        plus : bool
            If True, add ``proj_temperature`` for Transolver++."""
        linear_layer = te.Linear if use_te and TE_AVAILABLE else nn.Linear
        self.in_project_slice = linear_layer(dim_head, slice_num)
        self.temperature = nn.Parameter(torch.ones([1, 1, heads, 1]) * 0.5)
        if plus:
            self.proj_temperature = nn.Sequential(
                linear_layer(dim_head, slice_num), nn.GELU(), linear_layer(slice_num, 1), nn.GELU()
            )

    def _compute_slices(
        self, slice_projections: torch.Tensor, fx: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """执行_compute_slices；张量布局、参数与返回值见下列参考说明。

        Compute slice weights and slice tokens from projections and latent features.

        Delegates to :func:`~physicsnemo.nn.module.physics_attention._compute_slices_from_projections`,
        the shared free function that also backs
        :meth:`~physicsnemo.nn.module.physics_attention.PhysicsAttentionBase._compute_slices_from_projections`.

        Parameters
        ----------
        slice_projections : torch.Tensor
            Shape :math:`(B, N, H, S)`.
        fx : torch.Tensor
            Shape :math:`(B, N, H, D)`.

        Returns
        -------
        tuple[torch.Tensor, torch.Tensor]
            ``(slice_weights, slice_token)`` with shapes :math:`(B, N, H, S)`
            and :math:`(B, H, S, D)`."""
        proj_temp = getattr(self, "proj_temperature", None) if self.plus else None
        return _compute_slices_from_projections(
            slice_projections, fx, self.temperature, self.plus, proj_temperature=proj_temp
        )


class ContextProjector(_SliceToContextMixin, nn.Module):
    """可独立使用的ContextProjector计算组件。

    Projects context features onto physical state space.

    This context projector is conceptually similar to half of a GALE attention layer.
    It projects context values (geometry or global embeddings) onto a learned physical
    state space, but unlike a full attention layer, it never projects back to the
    original space. The projected features are used as context in all GALE blocks
    of the GeoTransolver model.

    Parameters
    ----------
    dim : int
        Input dimension of the context features.
    heads : int, optional
        Number of projection heads. Default is 8.
    dim_head : int, optional
        Dimension of each projection head. Default is 64.
    dropout : float, optional
        Dropout rate. Default is 0.0.
    slice_num : int, optional
        Number of learned physical state slices. Default is 64.
    use_te : bool, optional
        Whether to use Transformer Engine backend when available. Default is ``False``.
    plus : bool, optional
        Whether to use Transolver++ features. Default is ``False``.

    Forward
    -------
    x : torch.Tensor
        Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
        :math:`N` is number of tokens, and :math:`C` is number of channels.

    Outputs
    -------
    torch.Tensor
        Slice tokens of shape :math:`(B, H, S, D)` where :math:`H` is number of heads,
        :math:`S` is number of slices, and :math:`D` is head dimension.

    Notes
    -----
    The global features are reused in all blocks of the model, so the learned
    projections must capture globally useful features rather than layer-specific ones.

    See Also
    --------
    :class:`~physicsnemo.nn.module.gale.GALE` : Full GALE attention layer that uses these projected context features.
    :class:`~physicsnemo.models.geotransolver.GeoTransolver` : Main model that uses ContextProjector for geometry and global embeddings.

    Examples
    --------
    >>> import torch
    >>> projector = ContextProjector(dim=64, heads=8, dim_head=32, slice_num=32, use_te=False)
    >>> x = torch.randn(2, 100, 64)  # (batch, tokens, features)
    >>> slice_tokens = projector(x)
    >>> slice_tokens.shape
    torch.Size([2, 8, 32, 32])"""

    def __init__(
        self,
        dim: int,
        heads: int = 8,
        dim_head: int = 64,
        dropout: float = 0.0,
        slice_num: int = 64,
        use_te: bool = False,
        plus: bool = False,
        concrete_dropout: bool = False,
    ) -> None:
        if use_te or plus or concrete_dropout:
            raise NotImplementedError("当前移植仅支持普通 PyTorch GALE、无混合精度扩展及无时间条件")
        super().__init__()
        inner_dim = dim_head * heads
        self.dim_head = dim_head
        self.heads = heads
        self.plus = plus
        self.scale = dim_head ** (-0.5)
        self.use_te = use_te
        linear_layer = te.Linear if use_te and TE_AVAILABLE else nn.Linear
        self.in_project_x = linear_layer(dim, inner_dim)
        if not plus:
            self.in_project_fx = linear_layer(dim, inner_dim)
        self.softmax = nn.Softmax(dim=-1)
        self._init_slice_components(dim_head, slice_num, heads, use_te, plus)
        if concrete_dropout:
            raise NotImplementedError("此扩展分支不在当前移植范围")
        else:
            self.output_dropout = None

    def project_input_onto_slices(
        self, x: torch.Tensor
    ) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        """执行project_input_onto_slices；张量布局、参数与返回值见下列参考说明。

        Project the input onto the slice space.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size,
            :math:`N` is number of tokens, and :math:`C` is number of channels.

        Returns
        -------
        torch.Tensor or tuple[torch.Tensor, torch.Tensor]
            If ``plus=True``, returns single tensor of shape :math:`(B, N, H, D)` where
            :math:`H` is number of heads and :math:`D` is head dimension. If ``plus=False``,
            returns tuple of two tensors both of shape :math:`(B, N, H, D)`, representing
            the query and key projections respectively."""
        fx = None if self.plus else self.in_project_fx
        return _project_input(
            x, self.in_project_x, self.heads, self.dim_head, "B N (H D) -> B N H D", project_fx=fx
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """执行forward；张量布局、参数与返回值见下列参考说明。

        Project inputs to physical state slices.

        This performs a partial physics attention operation: it projects the input onto
        learned physical state slices but does not project back to the original space.
        The resulting slice tokens serve as context for GALE attention layers.

        Parameters
        ----------
        x : torch.Tensor
            Input tensor of shape :math:`(B, N, C)` where :math:`B` is batch size, :math:`N` is
            number of tokens, and :math:`C` is number of channels.

        Returns
        -------
        torch.Tensor
            Slice tokens of shape :math:`(B, H, S, D)` where :math:`H` is number of heads,
            :math:`S` is number of slices, and :math:`D` is head dimension.

        Notes
        -----
        This method implements the encoding portion of the physics attention mechanism.
        The slice tokens capture learned physical state representations that are used
        as cross-attention context throughout the model."""
        if not torch.compiler.is_compiling():
            if x.ndim != 3:
                raise ValueError(
                    f"Expected 3D input tensor (B, N, C), got {x.ndim}D tensor with shape {tuple(x.shape)}"
                )
        if self.plus:
            projected_x = self.project_input_onto_slices(x)
            feature_projection = projected_x
        else:
            projected_x, feature_projection = self.project_input_onto_slices(x)
        slice_projections = self.in_project_slice(projected_x)
        _, slice_tokens = self._compute_slices(slice_projections, feature_projection)
        if self.output_dropout is not None:
            slice_tokens = self.output_dropout(slice_tokens)
        return slice_tokens


class StructuredContextProjector(_SliceToContextMixin, nn.Module):
    """可独立使用的StructuredContextProjector计算组件。

    Context projector with Conv2d/Conv3d geometry encoding on structured grids.

    Same output interface as :class:`ContextProjector`—slice tokens
    :math:`(B, H, S, D)`—but projects per-cell geometry via spatial convolutions
    aligned with structured GALE attention."""

    def __init__(
        self,
        dim: int,
        spatial_shape: tuple[int, ...],
        heads: int = 8,
        dim_head: int = 64,
        dropout: float = 0.0,
        slice_num: int = 64,
        kernel: int = 3,
        use_te: bool = False,
        plus: bool = False,
        concrete_dropout: bool = False,
    ) -> None:
        if use_te or plus or concrete_dropout:
            raise NotImplementedError("当前移植仅支持普通 PyTorch GALE、无混合精度扩展及无时间条件")
        if spatial_shape is not None and len(spatial_shape) != 2:
            raise NotImplementedError("当前仅支持二维结构网格")
        super().__init__()
        if len(spatial_shape) not in (2, 3):
            raise ValueError(
                f"StructuredContextProjector expects spatial_shape of length 2 or 3, got {spatial_shape!r}"
            )
        inner_dim = dim_head * heads
        self.dim_head = dim_head
        self.heads = heads
        self.plus = plus
        self.use_te = use_te
        self.spatial_shape = tuple(int(s) for s in spatial_shape)
        self._nd = len(self.spatial_shape)
        pad = kernel // 2
        if self._nd == 2:
            H, W = self.spatial_shape
            self.H, self.W = (H, W)
            self.in_project_x = nn.Conv2d(dim, inner_dim, kernel, 1, pad)
            if not plus:
                self.in_project_fx = nn.Conv2d(dim, inner_dim, kernel, 1, pad)
        else:
            H, W, D_ = self.spatial_shape
            self.H, self.W, self.D = (H, W, D_)
            self.in_project_x = nn.Conv3d(dim, inner_dim, kernel, 1, pad)
            if not plus:
                self.in_project_fx = nn.Conv3d(dim, inner_dim, kernel, 1, pad)
        self.softmax = nn.Softmax(dim=-1)
        self.dropout = nn.Dropout(dropout)
        self._init_slice_components(dim_head, slice_num, heads, use_te, plus)
        if concrete_dropout:
            raise NotImplementedError("此扩展分支不在当前移植范围")
        else:
            self.output_dropout = None

    def _grid_project(self, x: torch.Tensor) -> torch.Tensor | tuple[torch.Tensor, torch.Tensor]:
        B, N, C = x.shape
        grid = _structured_grid_to_conv_input(x, B, N, C, self._nd, self.spatial_shape)
        pattern = (
            "B (H D) h w -> B (h w) H D" if self._nd == 2 else "B (H D) h w d -> B (h w d) H D"
        )
        fx = None if self.plus else self.in_project_fx
        return _project_input(
            grid, self.in_project_x, self.heads, self.dim_head, pattern, project_fx=fx
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if not torch.compiler.is_compiling():
            if x.ndim != 3:
                raise ValueError(
                    f"Expected 3D input (B, N, C), got {x.ndim}D shape {tuple(x.shape)}"
                )
        if self.plus:
            projected_x = self._grid_project(x)
            feature_projection = projected_x
        else:
            projected_x, feature_projection = self._grid_project(x)
        slice_projections = self.in_project_slice(projected_x)
        _, slice_tokens = self._compute_slices(slice_projections, feature_projection)
        if self.output_dropout is not None:
            slice_tokens = self.output_dropout(slice_tokens)
        return slice_tokens


class GlobalContextBuilder(nn.Module):
    """可独立使用的GlobalContextBuilder计算组件。

    Orchestrates all context construction with a clean, simple interface.

    Manages geometry tokenization, global embedding tokenization, and optional
    multi-scale local features. This is the main entry point for building context
    in the GeoTransolver model.

    Parameters
    ----------
    functional_dims : tuple[int, ...]
        Dimensions of each functional input type.
    geometry_dim : int | None, optional
        Geometry feature dimension. If ``None``, geometry context is disabled.
        Default is ``None``.
    global_dim : int | None, optional
        Global embedding dimension. If ``None``, global context is disabled.
        Default is ``None``.
    radii : list[float], optional
        Radii for local features. Default is ``[0.05, 0.25]``.
    neighbors_in_radius : list[int], optional
        Neighbors per radius. Default is ``[8, 32]``.
    n_hidden_local : int, optional
        Hidden dim for local features. Default is 32.
    n_hidden : int, optional
        Model hidden dimension. Default is 256.
    n_head : int, optional
        Number of attention heads. Default is 8.
    dropout : float, optional
        Dropout rate. Default is 0.0.
    slice_num : int, optional
        Number of slices for tokenization. Default is 32.
    use_te : bool, optional
        Whether to use Transformer Engine. Default is ``False``.
    plus : bool, optional
        Whether to use Transolver++ features. Default is ``False``.
    include_local_features : bool, optional
        Enable local feature extraction. Default is ``False``.
    structured_shape : tuple[int, ...] | None, optional
        If set, disables ball-query extractors and uses
        :class:`StructuredContextProjector` for geometry when ``geometry_dim``
        is set. Default is ``None``.

    Forward
    -------
    This class does not implement a standard ``forward`` method. Instead, use
    :meth:`build_context` to construct context, local features, and the
    detached geometry context.

    See Also
    --------
    :class:`ContextProjector` : Used for tokenizing geometry and global embeddings.
    :class:`MultiScaleFeatureExtractor` : Used for multi-scale local features.
    :class:`~physicsnemo.models.geotransolver.GeoTransolver` : Main model that uses this builder.

    Examples
    --------
    >>> import torch
    >>> builder = GlobalContextBuilder(
    ...     functional_dims=(64,),
    ...     geometry_dim=3,
    ...     global_dim=16,
    ...     n_hidden=256,
    ...     n_head=8,
    ...     use_te=False,
    ... )
    >>> local_embeddings = (torch.randn(2, 100, 64),)
    >>> geometry = torch.randn(2, 100, 3)
    >>> global_embedding = torch.randn(2, 1, 16)
    >>> context, local_feats, geo_ctx = builder.build_context(
    ...     local_embeddings, None, geometry, global_embedding
    ... )
    >>> context.shape
    torch.Size([2, 8, 32, 64])"""

    def __init__(
        self,
        functional_dims: tuple[int, ...],
        geometry_dim: int | None = None,
        global_dim: int | None = None,
        radii: list[float] | None = None,
        neighbors_in_radius: list[int] | None = None,
        n_hidden_local: int = 32,
        n_hidden: int = 256,
        n_head: int = 8,
        dropout: float = 0.0,
        slice_num: int = 32,
        use_te: bool = False,
        plus: bool = False,
        include_local_features: bool = False,
        structured_shape: tuple[int, ...] | None = None,
        concrete_dropout: bool = False,
    ) -> None:
        if use_te or plus or concrete_dropout:
            raise NotImplementedError("当前移植仅支持普通 PyTorch GALE、无混合精度扩展及无时间条件")
        if structured_shape is not None and len(structured_shape) != 2:
            raise NotImplementedError("当前仅支持二维结构网格")
        super().__init__()
        if radii is None:
            radii = [0.05, 0.25]
        if neighbors_in_radius is None:
            neighbors_in_radius = [8, 32]
        dim_head = n_hidden // n_head
        context_dim = 0
        self.structured_shape = structured_shape
        use_local_bq = (
            geometry_dim is not None and include_local_features and (structured_shape is None)
        )
        if use_local_bq:
            from .multiscale_local import MultiScaleFeatureExtractor

            self.local_extractors = nn.ModuleList(
                [
                    MultiScaleFeatureExtractor(
                        geometry_dim,
                        radii,
                        neighbors_in_radius,
                        n_hidden_local,
                        n_head,
                        dim_head,
                        dropout,
                        slice_num,
                        use_te,
                        plus,
                        concrete_dropout=concrete_dropout,
                    )
                    for _ in functional_dims
                ]
            )
            context_dim += dim_head * len(radii) * len(functional_dims)
        else:
            self.local_extractors = None
        if geometry_dim is not None:
            if structured_shape is not None:
                self.geometry_tokenizer = StructuredContextProjector(
                    geometry_dim,
                    structured_shape,
                    n_head,
                    dim_head,
                    dropout,
                    slice_num,
                    use_te=use_te,
                    plus=plus,
                    concrete_dropout=concrete_dropout,
                )
            else:
                self.geometry_tokenizer = ContextProjector(
                    geometry_dim,
                    n_head,
                    dim_head,
                    dropout,
                    slice_num,
                    use_te,
                    plus=plus,
                    concrete_dropout=concrete_dropout,
                )
            context_dim += dim_head
        else:
            self.geometry_tokenizer = None
        if global_dim is not None:
            self.global_tokenizer = ContextProjector(
                global_dim,
                n_head,
                dim_head,
                dropout,
                slice_num,
                use_te,
                plus,
                concrete_dropout=concrete_dropout,
            )
            context_dim += dim_head
        else:
            self.global_tokenizer = None
        self._context_dim = context_dim

    def get_context_dim(self) -> int:
        """执行get_context_dim；张量布局、参数与返回值见下列参考说明。

        Return total context dimension.

        Returns
        -------
        int
            Total dimension of the concatenated context features."""
        return self._context_dim

    def build_context(
        self,
        local_embeddings: tuple[torch.Tensor, ...],
        local_positions: tuple[torch.Tensor, ...] | None,
        geometry: torch.Tensor | None = None,
        global_embedding: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]:
        """执行build_context；张量布局、参数与返回值见下列参考说明。

        Build all context and local features.

        Parameters
        ----------
        local_embeddings : tuple[torch.Tensor, ...]
            Input embeddings, each of shape :math:`(B, N, C_i)` where :math:`B` is
            batch size, :math:`N` is number of tokens, and :math:`C_i` is the feature
            dimension for input type :math:`i`.
        local_positions : tuple[torch.Tensor, ...] | None
            Local positions, each of shape :math:`(B, N, 3)`. These are used to query
            neighbors for local features. Required if ``include_local_features=True``.
        geometry : torch.Tensor | None, optional
            Geometry features of shape :math:`(B, N, C_{geo})`. Default is ``None``.
        global_embedding : torch.Tensor | None, optional
            Global embedding of shape :math:`(B, N_g, C_g)`. Default is ``None``.

        Returns
        -------
        tuple[torch.Tensor | None, list[torch.Tensor] | None, torch.Tensor | None]
            - ``context``: Concatenated context tensor of shape :math:`(B, H, S, D_c)`
              where :math:`D_c` is the total context dimension, or ``None`` if no
              context sources are provided.
            - ``local_features``: List of local feature tensors, one per input type,
              each of shape :math:`(B, N, D_l)`, or ``None`` if local features are
              disabled.
            - ``geometry_context_detached``: Detached geometry-tokenizer output of shape
              :math:`(B, H, S, D)`, intended for downstream observers such as the
              embedded OOD guard.  ``None`` when geometry tokenization is disabled
              or no geometry was provided.

        Raises
        ------
        ValueError
            If ``local_positions`` is ``None`` but local features are enabled."""
        if not torch.compiler.is_compiling():
            if len(local_embeddings) == 0:
                raise ValueError("Expected non-empty tuple of local embeddings")
            for i, emb in enumerate(local_embeddings):
                if emb.ndim != 3:
                    raise ValueError(
                        f"Expected 3D local_embedding tensor (B, N, C) at index {i}, got {emb.ndim}D tensor with shape {tuple(emb.shape)}"
                    )
        context_parts = []
        local_features = None
        geometry_context_detached: torch.Tensor | None = None
        if local_positions is None and self.local_extractors is not None:
            raise ValueError("Local positions are required if local features are enabled.")
        if self.local_extractors is not None and geometry is not None:
            local_features = []
            for i, embedding in enumerate(local_embeddings):
                spatial_coords = local_positions[i]
                context_feats = self.local_extractors[i].extract_context_features(
                    spatial_coords, geometry
                )
                context_parts.extend(context_feats)
                local_feats = self.local_extractors[i].extract_local_features(
                    spatial_coords, geometry
                )
                local_features.append(local_feats)
        if self.geometry_tokenizer is not None and geometry is not None:
            geometry_context = self.geometry_tokenizer(geometry)
            geometry_context_detached = geometry_context.detach()
            context_parts.append(geometry_context)
        if self.global_tokenizer is not None and global_embedding is not None:
            context_parts.append(self.global_tokenizer(global_embedding))
        context = torch.cat(context_parts, dim=-1) if context_parts else None
        if context is not None and hasattr(context, "redistribute"):
            context = context.redistribute(placements=[Replicate()])
        return (context, local_features, geometry_context_detached)
