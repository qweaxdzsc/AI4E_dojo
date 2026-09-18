"""独立计算组件：只依赖 Python 标准库，不导入 Dojo。"""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Mesh:
    """示例网格采用自己的数据表示。"""

    vertices: list[tuple[float, float, float]]


def read_mesh(path):
    """将用户输入读成组件自己的对象。"""
    return Mesh([tuple(point) for point in json.loads(Path(path).read_text())])


def encode_points(points, *, radius):
    """点集生成特征，返回普通元组而非框架对象。"""
    return tuple(sum(value * value for value in point) ** 0.5 / radius for point in points)


def save_features(features, path):
    """写指定的数据目录并返回引用，不写运行记录。"""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(features))
    return target
