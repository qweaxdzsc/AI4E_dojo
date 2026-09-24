"""可选任务管理交接；只约束可序列化记录，不约束科学组件签名。"""

import json
from copy import deepcopy


def json_record(value):
    """复制严格 JSON 值，拒绝非有限数、科学对象及隐式字符串转换。"""
    encoded = json.dumps(value, ensure_ascii=False, allow_nan=False)
    result = json.loads(encoded)
    if result != value:
        raise ValueError("management_record_requires_json")
    return result


def validate_description(value: dict) -> dict:
    """校验版本、输入标签及恢复位置；缺声明不生成领域默认值。"""
    value = json_record(value)
    if not isinstance(value, dict) or value.get("schema_version") != 1:
        raise ValueError("unsupported_task_description")
    stages = value.get("stages", [])
    if (
        not isinstance(stages, list)
        or len(stages) != len(set(stages))
        or any(not isinstance(s, str) or not s.isidentifier() for s in stages)
    ):
        raise ValueError("invalid_task_stages")
    inputs = value.get("inputs", {})
    if not isinstance(inputs, dict):
        raise TypeError("invalid_task_inputs")
    for key, requirement in inputs.items():
        parts = key.split(".")
        if len(parts) != 3 or parts[0] != "inputs" or not all(p.isidentifier() for p in parts):
            raise ValueError("invalid_task_input_position")
        if not isinstance(requirement, dict) or not isinstance(requirement.get("kind"), str):
            raise TypeError("invalid_task_input_requirement")
        if set(requirement) - {"kind", "stage", "name", "semantics", "statuses", "provided_by"}:
            raise ValueError("unknown_task_input_condition")
        if not isinstance(requirement.get("semantics", {}), dict):
            raise TypeError("invalid_task_input_semantics")
        statuses = requirement.get("statuses", ["succeeded"])
        if not isinstance(statuses, list) or not set(statuses) <= {
            "succeeded",
            "stopped",
            "failed",
        }:
            raise ValueError("invalid_task_input_statuses")
    for key in value.get("resume_inputs", []):
        if key not in inputs:
            raise ValueError("unknown_resume_input")
    if not isinstance(value.get("shared_outputs", {}), dict):
        raise TypeError("invalid_shared_outputs")
    if not isinstance(value.get("operations", []), list):
        raise TypeError("invalid_task_operations")
    return deepcopy(value)


def exact_json_equal(left, right) -> bool:
    """JSON 值按类型精确比较，布尔值不能匹配整数，列表保留顺序。"""
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            exact_json_equal(left[k], right[k]) for k in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(exact_json_equal(a, b) for a, b in zip(left, right))
    return left == right


def validate_execution_plan(value) -> list[dict]:
    """验证应用交付的有限子运行列表；只检查管理结构，不解释配置值。"""
    value = json_record(value)
    if not isinstance(value, list) or not value:
        raise ValueError("invalid_execution_plan")
    identities = set()
    for unit in value:
        if not isinstance(unit, dict) or not isinstance(unit.get("id"), str) or not unit["id"]:
            raise ValueError("invalid_execution_unit")
        if unit["id"] in identities:
            raise ValueError("duplicate_execution_unit")
        identities.add(unit["id"])
        for key in ("overrides", "input_keys", "stages", "samples"):
            if not isinstance(unit.get(key), list) or any(
                not isinstance(v, str) for v in unit[key]
            ):
                raise ValueError("invalid_execution_unit_" + key)
        if not unit["stages"] or any(not s.isidentifier() for s in unit["stages"]):
            raise ValueError("invalid_execution_stages")
        for key in unit["input_keys"]:
            parts = key.split(".")
            if len(parts) != 3 or parts[0] != "inputs" or not all(p.isidentifier() for p in parts):
                raise ValueError("invalid_execution_input")
        if any(
            not isinstance(unit.get(key), str) or not unit[key]
            for key in ("checkpoint_id", "split")
        ):
            raise ValueError("invalid_execution_selection")
    return value
