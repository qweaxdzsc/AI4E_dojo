"""历史后处理入口；旧任务脚本 `from ...post import physical` 仍调用 open_post。"""

from ai4e_core.applications.aero_cfd.infer.anchor_stage import open_post

__all__ = ["open_post"]
