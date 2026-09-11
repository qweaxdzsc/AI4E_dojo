"""本机服务配置；外部数据目录仅由启动参数授权。"""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """服务运行根、原样模板和可浏览数据根。"""

    root: Path
    template: Path
    data_roots: list[Path] = field(default_factory=list)
    web_dist: Path | None = None
