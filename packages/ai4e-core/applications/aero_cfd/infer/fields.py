"""推理派生字段步骤：继承已有域的实体身份并交付保存和网格消费。"""

import re

import torch

from ai4e_core.base.config import operation_record, plain, resolve_operation

from .stage import _register


def configure_derived_fields(
    job,
    *,
    name: str,
    domain: str,
    unit: str | None,
    inputs: dict,
    association: str = "point",
    components: int = 1,
    operation=None,
    settings=None,
):
    """登记普通函数；参数绑定已命名物理数组，输出必须覆盖同域全部实体。"""
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name):
        raise ValueError("派生字段名称必须是稳定标识")
    # 当前完整物理路径为点场；不把 cell 数据误标为 point。
    if association != "point" or domain not in job.config["trainprep"]["domains"]:
        raise ValueError("派生字段必须绑定已有 point 域")
    if unit is not None and (not isinstance(unit, str) or not unit.strip()):
        raise ValueError("单位必须为明确字符串或未知的 null")
    if isinstance(components, bool) or not isinstance(components, int) or components < 1:
        raise ValueError("分量数必须为正整数")
    inputs = plain(inputs)
    if not inputs or any(
        not isinstance(v, str) or not v.startswith(domain + ".") for v in inputs.values()
    ):
        raise ValueError("派生字段输入须为同一域的具名数组")
    fn = resolve_operation(settings, operation=operation)
    key = domain + "." + name
    declaration = {
        "name": name,
        "domain": domain,
        "unit": unit,
        "association": association,
        "components": components,
        "inputs": inputs,
        "operation": operation_record(fn),
    }
    job.extensions.setdefault("derived_fields", {})[key] = declaration

    def apply(item):
        if domain not in item.domains:
            raise ValueError("派生字段必须位于物理输出之后")
        if key in item.payloads or name in item.domains[domain]["targets"]:
            raise ValueError("派生字段与现有输出重名")
        value = fn(**{arg: item.payloads[source] for arg, source in inputs.items()})
        if not isinstance(value, torch.Tensor):
            raise TypeError("派生字段须返回 Tensor")
        value = value.detach().cpu()
        if components == 1 and value.ndim == 1:
            value = value[:, None]
        count = len(item.payloads[item.domains[domain]["ids"]])
        if value.shape != (count, components) or not torch.isfinite(value).all():
            raise ValueError("派生字段输出形状、实体覆盖或数值无效")
        item.payloads[key] = value
        item.domains[domain].setdefault("derived_fields", {})[name] = {
            "field": key,
            "unit": unit,
            "association": association,
            "components": components,
            "ids": item.domains[domain]["ids"],
            "state": "physical",
        }
        return item

    return _register(job, "derived:" + key, apply)
