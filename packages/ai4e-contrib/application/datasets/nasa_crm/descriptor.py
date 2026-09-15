"""数据集的原始处理描述；默认参数与可选功能来自随包 manifest。"""

from pathlib import Path

from ai4e_core.applications.aero_cfd.rawprep.descriptor import load_description


def describe_rawprep(config=None):
    """无需读取原始数组即可返回绑定、字段和处理默认值。"""
    return load_description(Path(__file__).with_name("manifest.yaml"), config)
