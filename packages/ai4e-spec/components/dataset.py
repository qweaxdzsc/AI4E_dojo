"""按需数据访问契约；点字段、样本工况与拓扑分别交接。"""

from typing import Any, Protocol


class DatasetView(Protocol):
    """数据来源提供稳定身份和内容摘要，不向消费方暴露存储布局。"""

    partitions: dict[str, list[str]]

    def read(self, partition: str, index: int = 0, *, fields=None, selection=None) -> Any:
        """读取样本的选定字段和点；selection 的语义由视图声明。"""
        ...

    def describe(self) -> dict:
        """返回可序列化的数据、字段与分块语义；持久视图含 reference 引用。"""
        ...

    def content_digest(self) -> str:
        """按稳定次序计算本次消费的数据内容身份。"""
        ...
