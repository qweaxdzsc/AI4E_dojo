"""时空场身份与布局校验；各场的空间网格允许不同。"""


def validate_layout(shape, axes):
    """要求轴名称唯一且与数组维数一一对应。"""
    if len(shape) != len(axes) or len(set(axes)) != len(axes) or min(shape) < 1:
        raise ValueError("时空轴或形状声明非法")


def validate_pairing(records):
    """耦合场必须拥有相同样本身份和物理时间；不假定空间大小相同。"""
    if not records:
        raise ValueError("耦合场为空")
    first = records[0]
    for record in records[1:]:
        if (
            record["sample_ids"] != first["sample_ids"]
            or record["time_indices"] != first["time_indices"]
        ):
            raise ValueError("耦合场样本或物理时间不配对")
