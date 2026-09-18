"""纯标准库的运行身份与来源交接；不持有训练对象。"""

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class RunContext:
    """task 分配位置，core writer 独占写入；版本身份不会因 run 改变。"""

    project_id: str
    task_id: str
    version_id: str
    run_id: str
    run_dir: str
    data_dir: str
    code_dir: str
    version: dict = field(default_factory=dict)
    assets: dict = field(default_factory=dict)
    resumed_from: str | None = None
    schema_version: int = 1
    stage_outputs: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """转换为可独立保存的运行溯源记录。"""
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> "RunContext":
        """拒绝未知 schema 和空身份。"""
        result = cls(**value)
        if result.schema_version != 1 or not all(
            (result.project_id, result.task_id, result.version_id, result.run_id)
        ):
            raise ValueError("invalid_run_context")
        return result
