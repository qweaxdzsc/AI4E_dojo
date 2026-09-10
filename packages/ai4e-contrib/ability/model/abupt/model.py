"""贡献多域 AB-UPT 的显式构造及无缓存训练入口。"""

INPUTS = (
    "geometry_position",
    "geometry_supernode_idx",
    "geometry_batch_idx",
    "domain_anchor_positions",
)
OPTIONAL_INPUTS = (
    "domain_query_positions",
    "domain_anchor_features",
    "domain_query_features",
    "conditioning_inputs",
    "geometry_conditioning_inputs",
)
SOURCE = "abupt-domain-v3:noether-313e6c5c2ff31f283a3e5935b4d85888aac6b025"


def construct(**parameters):
    """构造唯一新结构；调用方必须声明 data_specs。"""
    from .network import AnchoredBranchedUPT

    return AnchoredBranchedUPT(**parameters)


def predict(model, inputs):
    """训练前向只消费声明输入，不接收目标或推理缓存。"""
    if not set(INPUTS) <= set(inputs) or set(inputs) - set(INPUTS + OPTIONAL_INPUTS):
        raise ValueError("多域模型输入缺失或包含未声明字段")
    return model(**inputs)[0]


def describe(model):
    """在组件内解释布局和结构版本，保持旧检查点字段及类型。"""
    return {"model_version": model.structure_version, "input_layout": model.layout.signature}


construct.describe = describe
