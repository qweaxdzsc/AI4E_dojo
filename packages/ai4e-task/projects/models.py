"""项目便携记录类型。"""

from typing import NotRequired, TypedDict


class Project(TypedDict):
    """研究项目身份，不以目录名充当身份。"""

    id: str
    name: str
    schema_version: int
    created_at: str
    updated_at: NotRequired[str]
    description: NotRequired[str]
    archived: NotRequired[bool]
