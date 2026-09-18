"""用户配置只做路径和参数解析，不依赖领域默认配置。"""
from pathlib import Path
from ai4e_core.base.config import load_config


def load_configuration(path, overrides=None):
    """相对输入输出以案例配置目录解析，步骤仍由 Python 决定。"""
    cfg = load_config(path, overrides)
    for key in ("input_path", "output_path", "run_root"):
        value = Path(cfg[key])
        cfg[key] = str(value if value.is_absolute() else Path(path).resolve().parent / value)
    return cfg
