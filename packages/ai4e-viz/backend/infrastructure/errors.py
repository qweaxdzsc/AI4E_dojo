"""跨技术层共享的基础异常；业务异常继续由所属模块定义。"""


class InfrastructureError(RuntimeError):
    """文件、数据库或外部运行时基础设施失败时的统一基类。"""
