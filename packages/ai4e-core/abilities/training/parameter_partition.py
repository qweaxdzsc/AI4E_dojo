"""显式条件的参数分组，确保可训练参数恰好覆盖一次。"""


def partition_parameters(model, selectors: dict):
    """selector(name, parameter) 返回布尔；重复/遗漏均失败，冻结参数不分配。"""
    groups = {name: [] for name in selectors}
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        matches = [key for key, select in selectors.items() if select(name, parameter)]
        if len(matches) != 1:
            raise ValueError(f"参数 {name} 分配次数为 {len(matches)}")
        groups[matches[0]].append(parameter)
    return groups
