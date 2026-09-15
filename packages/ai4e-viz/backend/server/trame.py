"""Trame兼容启动入口。

进程、URL和会话启动属于Server；物理场业务场景逐步迁入 ``visPhysField``，纯VTK
性能原语迁入 ``visEngine``。Server只转发模块内统一Trame服务。
"""

from modules.visPhysField.trameServer import *  # noqa: F403 - Server公开模块级Trame控制器
