"""统一运行路径与兼容环境变量配置。

这里集中回答“运行数据放在哪里”，但不理解任何业务表。新代码默认写入用户缓存目录；旧 ``QODER_*`` 变量继续用于测试和过渡，避免目录重构破坏现有调用。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class RuntimePaths:
    """运行期目录的不可变值对象。

    所有字段均由同一个运行根目录派生，防止各模块自行拼接路径。调用方可以在测试中
    通过 ``AI4E_VIS_RUNTIME_DIR`` 将整套状态隔离到临时目录。
    """

    root: Path
    database: Path
    objects: Path
    derived: Path
    exports: Path
    quarantine: Path
    temporary: Path
    logs: Path
    telemetry: Path
    runtime: Path
    backups: Path

    def ensure(self) -> "RuntimePaths":
        """创建运行期目录并返回自身；不会创建业务文件或修改数据库。"""

        for path in (
            self.database.parent, self.objects, self.derived, self.exports,
            self.quarantine, self.temporary, self.logs, self.telemetry,
            self.runtime, self.backups,
        ):
            path.mkdir(parents=True, exist_ok=True)
        return self


def runtime_paths() -> RuntimePaths:
    """根据环境变量返回统一运行路径。

    ``AI4E_VIS_DB_PATH`` 只覆盖数据库文件；其余文件仍由
    ``AI4E_VIS_RUNTIME_DIR`` 管理。路径在这里解析为绝对路径，数据库内仍只能保存
    相对于运行根目录的 ``storage_key``。
    """

    root = Path(os.environ.get("AI4E_VIS_RUNTIME_DIR", Path.home() / ".cache" / "ai4e-vis")).expanduser().resolve()
    database = Path(os.environ.get("AI4E_VIS_DB_PATH", root / "db" / "ai4e_vis.sqlite3")).expanduser().resolve()
    return RuntimePaths(
        root=root, database=database, objects=root / "objects", derived=root / "derived",
        exports=root / "exports", quarantine=root / "quarantine", temporary=root / "tmp",
        logs=root / "logs", telemetry=root / "telemetry", runtime=root / "runtime",
        backups=root / "backups",
    )


def configured_database_path(*legacy_names: str) -> Path:
    """返回数据库位置，同时兼容现有测试使用的 ``QODER_*`` 变量。

    参数顺序表达兼容优先级；只要测试显式指定旧变量，就不会触碰真实运行库。
    """

    for name in legacy_names:
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser().resolve()
    return runtime_paths().database
