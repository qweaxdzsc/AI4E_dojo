"""参数化 PDE 领域装配，只调用注入组件的公开接口。"""

from .infer import infer
from .post import post
from .rawprep import rawprep
from .train import train
from .trainprep import trainprep

__all__ = ["infer", "post", "rawprep", "train", "trainprep"]
