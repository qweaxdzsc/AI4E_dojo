"""通用装配机制：阶段盒子与阶段管道。"""

from ai4e_core.applications.base.pipeline import Pipeline
from ai4e_core.applications.base.stage import Stage, StageError

__all__ = ["Pipeline", "Stage", "StageError"]
