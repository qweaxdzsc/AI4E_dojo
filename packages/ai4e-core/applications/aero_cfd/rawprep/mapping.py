"""用户字段能力的公开适配：具名数组输入、原实体顺序输出与声明传播。"""

import inspect
from collections.abc import Mapping
from copy import deepcopy
from dataclasses import dataclass, replace

import numpy as np

from ai4e_core.base.config import operation_record, plain, resolve_operation


def _reference(value):
    if not isinstance(value, str) or value.count(".") != 1 or not all(value.split(".")):
        raise ValueError(f"字段引用必须为 域.字段: {value!r}")
    return value.split(".")


@dataclass
class FieldMapParameters:
    """字段映射配置；输出按 entity_like 保留原始行身份，不允许隐式筛选。"""

    inputs: dict
    outputs: dict
    target: str | None = None
    parameters: dict | None = None

    def __post_init__(self):
        if not isinstance(self.inputs, Mapping) or not self.inputs:
            raise ValueError("inputs 必须是非空映射")
        if not isinstance(self.outputs, Mapping) or not self.outputs:
            raise ValueError("outputs 必须是非空映射")
        for value in self.inputs.values():
            _reference(value)
        names = set()
        for spec in self.outputs.values():
            allowed = {"name", "entity_like", "components", "unit_from", "unit", "state"}
            if not isinstance(spec, Mapping) or set(spec) - allowed:
                raise ValueError("输出包含未知声明")
            if not {"name", "entity_like", "components", "state"} <= spec.keys():
                raise ValueError("输出必须声明 name/entity_like/components/state")
            name = spec["name"]
            if not isinstance(name, str) or not name or any(c in name for c in "/\\."):
                raise ValueError("输出逻辑名必须是非空单个字段名")
            if name in names:
                raise ValueError("输出逻辑名重复")
            names.add(name)
            _reference(spec["entity_like"])
            if spec["components"] not in (1, 3) or isinstance(spec["components"], bool):
                raise ValueError("输出目前支持 1 或 3 分量")
            if spec["state"] != "physical":
                raise ValueError("原始字段扩展必须声明 physical 状态")
            if ("unit" in spec) == ("unit_from" in spec):
                raise ValueError("输出必须且只能声明 unit 或 unit_from")
            if "unit_from" in spec:
                _reference(spec["unit_from"])


def map_fields(data, *, name: str, inputs, outputs, operation=None, target=None, parameters=None):
    """登记普通数组函数；输出继承原实体身份，新逻辑字段可直接选择和保存。

    输入是原 VTK 顺序的只读数组。函数必须逐行保序返回具名数组；需要改变实体
    集合时使用专门的同步筛选步骤。不能从返回数组数值猜测实体排列。
    """
    inputs, outputs = plain(inputs), plain(outputs)
    FieldMapParameters(inputs, outputs, target, parameters)
    fn = resolve_operation({"target": target, "parameters": parameters or {}}, operation=operation)
    try:
        inspect.signature(fn).bind(**{key: None for key in inputs})
    except TypeError as exc:
        raise ValueError(f"{name}: 输入绑定与能力签名不符: {exc}") from exc
    metadata = deepcopy(data.metadata)
    for spec in outputs.values():
        logical = spec["name"]
        if logical in metadata["outputs"]:
            raise ValueError(f"输出字段已存在: {logical}")
        domain, _ = _reference(spec["entity_like"])
        metadata["outputs"][logical] = {"domain": domain, "field": "fields." + logical}
    metadata.setdefault("extensions", []).append(
        {"step": name, "operation": operation_record(fn), "inputs": inputs, "outputs": outputs}
    )

    def apply(ctx):
        domains = {
            key: {
                **value,
                "fields": dict(value["fields"]),
                "field_specs": deepcopy(value["field_specs"]),
            }
            for key, value in ctx["data"].items()
        }

        def field(ref):
            domain, key = _reference(ref)
            if domain not in domains or key not in domains[domain]["fields"]:
                raise ValueError(f"{name}: 输入字段不存在: {ref}")
            return domains[domain]["fields"][key], domains[domain]["field_specs"][key]

        args = {}
        for key, ref in inputs.items():
            values, _ = field(ref)
            values = np.asarray(values).view()
            values.setflags(write=False)
            args[key] = values
        result = fn(**args)
        if not isinstance(result, Mapping) or set(result) != set(outputs):
            raise ValueError(f"{name}: 返回字段必须与 outputs 一一对应")
        for key, spec in outputs.items():
            like, declaration = field(spec["entity_like"])
            like_domain, _ = _reference(spec["entity_like"])
            for reference in inputs.values():
                values_in, input_declaration = field(reference)
                input_domain, _ = _reference(reference)
                if (
                    input_domain != like_domain
                    or input_declaration["association"] != declaration["association"]
                    or len(values_in) != len(like)
                ):
                    raise ValueError(
                        f"{name}/{key}: 输入与 entity_like 实体身份不一致；跨网格映射须使用专门能力"
                    )
            values = np.asarray(result[key])
            expected = (len(like), spec["components"])
            if values.shape == (len(like),) and spec["components"] == 1:
                values = values[:, None]
            if values.shape != expected or not np.issubdtype(values.dtype, np.number):
                raise ValueError(f"{name}/{key}: 输出形状应为 {expected}，实际 {values.shape}")
            domain, _ = _reference(spec["entity_like"])
            logical = spec["name"]
            if logical in domains[domain]["fields"]:
                raise ValueError(f"{name}: 不允许覆盖已有字段 {logical}")
            unit = field(spec["unit_from"])[1].get("unit") if "unit_from" in spec else spec["unit"]
            # 沿用现有 FieldRecord 的标量 (N,) 契约，公开函数可自然返回 N×1。
            domains[domain]["fields"][logical] = values[:, 0] if spec["components"] == 1 else values
            domains[domain]["field_specs"][logical] = {
                "association": declaration["association"],
                "kind": "scalar" if spec["components"] == 1 else "vector",
                "unit": unit,
                "state": "physical",
                "entity_like": spec["entity_like"],
            }
        return {**ctx, "data": domains}

    return replace(data, metadata=metadata).then(name, apply)
