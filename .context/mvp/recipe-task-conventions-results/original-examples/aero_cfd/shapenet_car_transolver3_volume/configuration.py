"""案例参数连接：框架转换集中维护，用户在此声明局部扩展参数。"""

from ai4e_contrib.application.aero_cfd import configuration as shared

STEP_PARAMETERS = {}


def application_parameters(config):
    """用本案例扩展声明连接到公开业务参数入口。"""
    return shared.application_parameters(config, declarations=STEP_PARAMETERS)


def load_configuration(path, overrides=None):
    """以配置文件位置解析参数；不在复制目录维护平台内部键转换。"""
    return shared.load_configuration(path, overrides, declarations=STEP_PARAMETERS)


load_components = shared.load_components
