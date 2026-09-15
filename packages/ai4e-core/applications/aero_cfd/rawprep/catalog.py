"""检查目录的样本选择与字段核验；样本原生选择由数据组件交付。"""

import json


def sample_key(partition, name):
    """稳定不透明身份，避免前端猜测分隔符与跨分片重名。"""
    return json.dumps([partition, name], ensure_ascii=False, separators=(",", ":"))


def choose_samples(partitions, scope):
    """在已声明名单内选全部或明确身份；分片模式仅兼容旧请求，空选择不回退全部。"""
    if scope is None:
        return partitions
    if not isinstance(scope, dict):
        raise ValueError("sample_scope: 需要映射")  # noqa: TRY004 - 平台配置错误统一 ValueError
    mode = scope.get("mode")
    if mode not in {"all", "partitions", "samples"}:
        raise ValueError("sample_scope.mode: 未知范围")
    requested = scope.get("values", [])
    if not isinstance(requested, list) or not all(isinstance(v, str) for v in requested):
        raise ValueError("sample_scope.values: 需要字符串列表")
    if mode == "all" and requested:
        raise ValueError("sample_scope.values: 全部模式不能包含子集")
    if mode != "all" and (not requested or len(requested) != len(set(requested))):
        raise ValueError("sample_scope.values: 空或重复选择")
    available = (
        set(partitions)
        if mode == "partitions"
        else {sample_key(split, name) for split, names in partitions.items() for name in names}
    )
    if mode != "all" and set(requested) - available:
        raise ValueError("sample_scope.values: 样本或分片不在声明名单中")
    result = {
        split: [
            name
            for name in names
            if mode == "all"
            or (
                split in requested if mode == "partitions" else sample_key(split, name) in requested
            )
        ]
        for split, names in partitions.items()
    }
    result = {split: names for split, names in result.items() if names}
    if not result:
        raise ValueError("sample_scope: 声明名单为空")
    return result


def check_requested_fields(fields, config, *, source_catalog=None, declarations=None):
    """核验本次提取涉及的真实数组；不将代表样本的结构冒充所有样本。"""
    available = {item["field_id"]: item for item in fields}
    requests = []
    for domain, values in config.get("fields", {}).items():
        for name, overrides in values.items():
            spec = {**(source_catalog or {}).get(domain, {}).get(name, {}), **overrides}
            if spec.get("array"):
                requests.append(
                    (f"{domain}/{spec['association']}/{spec['array']}", spec["components"])
                )
    for entry in config.get("extraction", {}).get("entries", []):
        for output in entry["outputs"]:
            for member in output["members"]:
                ref = member["source_field"]
                if ref in (declarations or {}):
                    continue
                requests.append((ref, member.get("components", 1)))
    for ref, components in requests:
        if ref not in available:
            raise ValueError(f"缺少字段 {ref}")
        item = available[ref]
        if item["components"] != components or not item.get("supported", True):
            raise ValueError(f"字段类型或分量不兼容 {ref}")
