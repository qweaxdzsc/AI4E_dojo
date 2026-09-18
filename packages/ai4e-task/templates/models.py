"""从公共 recipe 结构投影的内部查询类型。"""

from typing import NotRequired, TypedDict


class Entry(TypedDict):
    """输出绑定任务或已声明共享目录；阶段输入决定本次捕获的资产范围。"""

    shared_outputs: NotRequired[dict[str, dict[str, str]]]
    stage_inputs: NotRequired[dict[str, list[dict[str, str]]]]
    script: str
    config: str
    inputs: dict[str, str]
    outputs: dict[str, str]
    convention_version: int
    components: NotRequired[dict[str, str]]
    resume_key: NotRequired[str]
