"""三维物理场配置与结果索引的Repository边界。

现有版本尚未拥有独立物理场配置表，场内容解析仍归``visDatasets``，原始资产登记归
``dataAssets``，可视化结果仍归
``visIO``。本文件明确未来物理场专属表和SQL的唯一归属，但不会在目录重构时伪造表。
"""


def persistence_ready() -> bool:
    """说明物理场专属持久化尚未实现；不影响读取现有数据集和可视化资产。"""

    return False
