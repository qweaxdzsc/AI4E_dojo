"""文件检查的跨包描述，不携带数值库对象或本机绝对路径。"""

from typing import Literal, NotRequired, TypedDict


class FileField(TypedDict):
    """字段身份由归属与名称组成，形状保持原始实体数。"""

    id: str
    name: str
    association: Literal["geometry", "point", "cell", "array", "column"]
    shape: list[int]
    dtype: str
    components: NotRequired[int]


class FileInspection(TypedDict):
    """真实文件字段目录，内容修订由宿主受控文件服务补充。"""

    kind: Literal["mesh", "tensor", "text"]
    fields: list[FileField]
    revision: NotRequired[str]
    points: NotRequired[int]
    cells: NotRequired[int]
