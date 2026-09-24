"""本地配置及拟合状态交接；模型参数不进入通用运行器。"""

from ai4e_contrib.application.surrogate_modeling.configuration import (
    component,
    load_configuration,
    validate,
)
from ai4e_contrib.application.surrogate_modeling.preparation import preparation_identity

__all__ = ["component", "fit_context", "load_configuration", "validate"]


def fit_context(cfg, prepared, metadata):
    """保存与预测共同核对字段、统计、组件和可搬移的准备内容身份。"""
    if metadata["case"] != cfg["dataset"]["case"]:
        raise ValueError("配置案例与准备不一致")
    return {
        "preparation_identity": preparation_identity(prepared),
        "dataset": cfg["dataset"],
        "model": cfg["model"],
        "components": cfg["components"],
        "fields": metadata["fields"],
        "units": metadata["units"],
        "statistics": metadata["statistics"],
    }
