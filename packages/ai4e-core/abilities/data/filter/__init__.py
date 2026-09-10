"""有效点标记、精确重合标记及按组筛选，不改原数组。"""

from .coincident import exterior_mask
from .records import filter_records
from .select import apply_aligned_mask
from .used_vertices import used_vertex_mask

__all__ = ["apply_aligned_mask", "exterior_mask", "filter_records", "used_vertex_mask"]
