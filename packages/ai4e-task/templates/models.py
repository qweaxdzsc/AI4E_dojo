"""用户执行入口的显式文件与路径绑定。"""

from typing import TypedDict


class Entry(TypedDict):
    """outputs 是配置键到 data_dir/run_root 模板，inputs 是配置键到资产类型。"""

    script: str
    config: str
    inputs: dict[str, str]
    outputs: dict[str, str]
