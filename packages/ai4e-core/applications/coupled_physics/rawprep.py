"""耦合数组来源物化装配，解压与完整性检查委托 data 能力。"""

from ai4e_core.abilities.data.source.archives import extract_archives


def materialize(root, destination, *, execute=True):
    """原数据只读，处理目录由调用方显式指定。"""
    return extract_archives(root, destination, execute=execute)
