"""运行与逐项执行公开入口。"""

from .execute import BatchExecutionError, execute_many, for_each
from .runner import run_from_config
from .writer import RunWriter

__all__ = ["BatchExecutionError", "RunWriter", "execute_many", "for_each", "run_from_config"]

from .dataset import execute
from .operation import execute_operation
from .session import launch, load_user_configuration, run_recipe, stage
from .training import TrainingRun

__all__ += [
    "TrainingRun",
    "execute",
    "execute_operation",
    "launch",
    "load_user_configuration",
    "run_recipe",
    "stage",
]

from .provenance import managed_run

__all__ += ["managed_run"]

from .session import configuration_adapter

__all__ += ["configuration_adapter"]
