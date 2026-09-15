"""用户速度模长能力；只认识数组，不依赖 Dojo。"""

import numpy as np


def speed_magnitude(velocity):
    """原实体顺序的 N×3 速度转为 N×1 速度模长，单位保持。"""
    return {"speed": np.linalg.norm(velocity, axis=-1, keepdims=True)}
