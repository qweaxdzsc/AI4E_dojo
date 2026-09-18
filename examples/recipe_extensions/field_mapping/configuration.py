"""案例参数连接：框架转换集中维护，用户在此声明局部扩展参数。"""

from ai4e_contrib.application.aero_cfd import configuration as shared
from ai4e_core.applications.aero_cfd.rawprep import FieldMapParameters

STEP_PARAMETERS = {"rawprep.speed": FieldMapParameters}


def application_parameters(config, *, session=None):
    """纯配置转换；执行正文可显式传入会话以分配本次输出。"""
    outputs = (
        {name: session.output_dir(name) for name in ("rawprep", "trainprep", "infer", "post")}
        if session is not None else None
    )
    return shared.application_parameters(config, declarations=STEP_PARAMETERS, output_dirs=outputs)


def load_configuration(path, overrides=None):
    """以配置文件位置解析参数；不在复制目录维护平台内部键转换。"""
    return shared.load_configuration(path, overrides, declarations=STEP_PARAMETERS)


load_components = shared.load_components
