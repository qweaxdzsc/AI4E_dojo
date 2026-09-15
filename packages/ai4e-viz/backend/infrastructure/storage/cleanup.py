"""运行期派生文件清理边界。

本模块只允许清理 ``tmp`` 和可重建 ``derived`` 内容；原始对象、数据库、成功导出与
备份不属于普通清理候选。
"""

from __future__ import annotations

from pathlib import Path

from infrastructure.config import runtime_paths


def cleanup_roots() -> tuple[Path, Path]:
    """返回允许被维护脚本扫描的两个受控目录。"""

    paths = runtime_paths()
    return paths.temporary, paths.derived
