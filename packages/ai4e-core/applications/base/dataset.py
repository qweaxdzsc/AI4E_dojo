"""只持有样本引用与顺序步骤的按需数据视图，不读取数组或调度循环。"""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Dataset:
    """可复用样本清单；steps 由执行器逐样本消费，metadata 不含网格。"""

    root: Path
    samples: tuple[str, ...]
    partitions: Mapping[str, tuple[str, ...]]
    metadata: dict[str, Any]
    steps: tuple[tuple[str, Callable], ...] = ()
    options: dict[str, Any] = field(default_factory=dict)

    def then(self, name: str, operation: Callable, **options: Any) -> "Dataset":
        """返回附加一步的新视图，原视图不变，登记时不执行操作。"""
        return replace(
            self, steps=(*self.steps, (name, operation)), options={**self.options, **options}
        )
