"""物理域与模型字段绑定检查，禁止跨域同形数组静默错配。"""


def validate_bindings(sample: dict, bindings: dict) -> None:
    """输入绑定只可消费声明域的坐标和点场；工况来源独立校验。"""
    context = sample["identity"]
    for name, binding in bindings["domains"].items():
        if name not in sample["domains"]:
            raise ValueError(f"{context}/{name}: 数据没有模型要求的域")
        domain = sample["domains"][name]
        if binding["position"] != domain["position"]:
            raise ValueError(f"{context}/{name}: 模型坐标绑定与物理域不一致")
        available = set(domain["fields"].values())
        for field in (*binding.get("features", {}).values(), *binding.get("targets", {}).values()):
            if field not in available:
                raise ValueError(f"{context}/{name}/{field}: 模型字段不属于该物理域")
    for declaration in bindings.get("conditioning", {}).values():
        if "field" in declaration and declaration["field"] not in sample["conditions"]:
            raise ValueError(f"{context}/{declaration['field']}: 缺少样本级工况")
