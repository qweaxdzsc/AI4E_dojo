"""可复制配置入口；路径与参数验证由 PCNO 应用提供。"""

from ai4e_contrib.application.geothermal.pcno.configuration import (
    component,
    load_configuration,
    validate,
)

__all__ = ["component", "load_configuration", "validate"]
