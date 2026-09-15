"""推理字段选择；评价按分量，持久化按原始完整字段。"""

from .catalog import describe_fields


def configure_selection(job, *, fields=None):
    """登记选择而不执行计算；显式空选择不恢复默认字段。"""
    from .stage import _register

    job.selection = resolve_selection(
        job.config,
        job.dataset_component,
        fields,
        derived_fields=job.extensions.get("derived_fields"),
    )

    def apply(item):
        item.selection = job.selection
        return item

    return _register(job, "selection", apply)


def resolve_selection(config, dataset_component=None, fields=None, *, derived_fields=None):
    """解析同一份字段目录，供新旧原生脚本共用。"""
    choices = describe_fields(config, dataset_component=dataset_component)
    for declaration in (derived_fields or {}).values():
        count = declaration["components"]
        parts = ["scalar"] if count == 1 else [*map(str, range(count)), "magnitude"]
        for component in parts:
            choices.append(
                {
                    "id": f"{declaration['domain']}:{declaration['name']}:{component}",
                    "domain": declaration["domain"],
                    "field": declaration["name"],
                    "component": component,
                    "components": count,
                    "label": declaration["name"]
                    + ("" if component == "scalar" else " · " + component),
                    "source": declaration["domain"] + "." + declaration["name"],
                    "unit": declaration["unit"],
                    "association": declaration["association"],
                    "category": "派生",
                    "available": True,
                    "evaluable": False,
                    "reason": "派生字段未声明独立真值",
                    "default": component != "magnitude",
                }
            )
    available = {f["id"]: f for f in choices}
    if fields is None:
        fields = [f["id"] for f in choices if f["default"]]
    if not fields or len(fields) != len(set(fields)) or set(fields) - available.keys():
        raise ValueError("推理物理量选择不存在、重复或为空")
    return [available[key] for key in fields]
