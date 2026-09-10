"""模型要求预检，不推断或转换模型的数据布局。"""

from ai4e_spec.components.model import ModelRequirements


def validate_inputs(requirements: ModelRequirements, inputs: dict, batch_size: int) -> None:
    """拒绝缺失/额外输入以及不支持的批次。"""
    if not set(requirements.input_names) <= set(inputs) or set(inputs) - set(
        requirements.input_names + requirements.optional_input_names
    ):
        raise ValueError("模型输入字段与要求不一致")
    if batch_size < 1 or (
        requirements.max_batch_size is not None and batch_size > requirements.max_batch_size
    ):
        raise ValueError("模型不支持此批次大小")
