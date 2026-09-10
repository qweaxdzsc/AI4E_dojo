"""具名字段与行身份契约；身份由提取方声明，校验方不猜测数组来源。"""

from typing import Literal, TypedDict

import numpy as np

Association = Literal["point", "cell"]
FieldKind = Literal["scalar", "vector"]


class GroupContract(TypedDict):
    """同源实体组；entity_ids 是当前行对应的原始 point/cell ID。"""

    source: str
    association: Association
    count: int
    entity_ids: np.ndarray


class FieldRecord(TypedDict):
    """每场显式声明来源与行身份，可与组共享同一个只读身份数组。"""

    name: str
    values: np.ndarray
    association: Association
    kind: FieldKind
    group: str
    source: str
    entity_ids: np.ndarray
