"""具名字段与坐标提取，以及显式实体身份契约。"""

from .records import FieldRecord, GroupContract
from .vtk_fields import extract_coordinates, extract_field, extract_scalars, extract_vectors

__all__ = [
    "FieldRecord",
    "GroupContract",
    "extract_coordinates",
    "extract_field",
    "extract_scalars",
    "extract_vectors",
]
