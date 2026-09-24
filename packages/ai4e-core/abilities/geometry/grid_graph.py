"""规则二维四邻接和三维六邻接；不推断连续障碍或物理拓扑。"""

from collections.abc import Sequence

import torch


def grid_edges(shape: Sequence[int], *, device=None) -> torch.Tensor:
    """返回 [2,E] 双向相邻边；节点按末轴最快展平，无自环和对角线。"""
    shape = tuple(shape)
    if len(shape) not in (2, 3) or any(type(n) is not int or n < 1 for n in shape):
        raise ValueError("shape 必须为二或三个正整数")
    ids = torch.arange(torch.Size(shape).numel(), device=device).reshape(shape)
    pieces = []
    for axis, size in enumerate(shape):
        if size == 1:
            continue
        left = [slice(None)] * len(shape)
        right = list(left)
        left[axis], right[axis] = slice(None, -1), slice(1, None)
        pairs = torch.stack((ids[tuple(left)].reshape(-1), ids[tuple(right)].reshape(-1)))
        pieces.extend((pairs, pairs.flip(0)))
    return (
        torch.cat(pieces, dim=1) if pieces else torch.empty(2, 0, dtype=torch.long, device=device)
    )
