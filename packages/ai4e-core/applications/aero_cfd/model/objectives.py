"""按显式学习目标绑定预测、目标、反变换及比较方法。"""

from copy import deepcopy


def objectives(config=None):
    """不根据预测头或磁盘字段自动增加监督项。"""
    settings = config or {}
    terms = deepcopy(settings.get("supervision", []))
    if not terms:
        raise ValueError("必须显式声明 supervision 学习目标")
    names = set()
    for term in terms:
        for key in ("name", "prediction", "target", "normalization"):
            if not term.get(key):
                raise ValueError("学习目标绑定不完整")
        if term["name"] in names:
            raise ValueError("学习目标名称重复")
        names.add(term["name"])
        term.setdefault("weight", 1.0)
        term.setdefault("loss", "mse")
        term.setdefault("delta", 1.0)
    return terms
