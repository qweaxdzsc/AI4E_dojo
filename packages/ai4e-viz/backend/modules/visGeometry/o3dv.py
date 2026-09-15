"""O3DV模块专属适配器。

这里只描述O3DV能够消费的几何表现形式，不保存服务URL，也不承担格式转换；格式转换
由 ``visConvertor`` 负责。
"""

from pathlib import Path


def representation_name(source_name: str) -> str:
    """根据源文件名生成稳定的GLB表现文件名。"""

    return f"{Path(source_name).stem}.glb"
