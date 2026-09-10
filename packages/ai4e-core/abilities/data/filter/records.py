"""对已声明身份的点组统一筛选，保留原数组与原 ID。"""

from collections.abc import Mapping, Sequence

import numpy as np

from ai4e_core.abilities.data.extract.records import FieldRecord, GroupContract
from ai4e_core.abilities.data.validate import require_valid_records
from ai4e_core.base.events import traced


@traced("记录筛选")
def filter_records(
    records: Sequence[FieldRecord],
    groups: Mapping[str, GroupContract],
    masks: Mapping[str, np.ndarray],
) -> tuple[list[FieldRecord], dict[str, GroupContract]]:
    """校验前后契约；点 mask 不能应用到单元组。返回新记录与组。"""
    require_valid_records(records, groups)
    updated = dict(groups)
    selected = {}
    for key, raw in masks.items():
        if key not in groups:
            raise ValueError(f"筛选未声明组: {key}")
        group = groups[key]
        mask = np.asarray(raw)
        if group["association"] != "point":
            raise ValueError(f"点 mask 不适用于单元组: {key}")
        if mask.dtype != bool or mask.shape != (group["count"],):
            raise ValueError(f"mask 必须为组 {key} 的等长一维布尔数组")
        ids = group["entity_ids"][mask]
        ids.setflags(write=False)
        updated[key] = {**group, "count": int(mask.sum()), "entity_ids": ids}
        selected[key] = mask
    output = []
    for record in records:
        key = record["group"]
        if key in selected:
            output.append(
                {
                    **record,
                    "values": record["values"][selected[key]],
                    "entity_ids": updated[key]["entity_ids"],
                }
            )
        else:
            output.append(record)
    require_valid_records(output, updated)
    return output, updated
