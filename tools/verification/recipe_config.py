"""验收工具读取案例配置；只在验证侧加载普通 recipe，不成为库依赖。"""

import importlib.util
from pathlib import Path

import yaml


def experiment_sampling(user: dict) -> dict:
    """读取显式实验的种子和锚点预算；缺声明时拒绝回退默认实验。"""
    if "sampling" in user:
        raise ValueError("旧实验 sampling 已移除，请使用 model.sampling")
    modern = user.get("model", {}).get("sampling")
    legacy = user.get("trainprep", {}).get("sampling")
    if modern is not None and legacy is not None:
        raise ValueError("model.sampling 与 trainprep.sampling 不能同时存在")
    sampling = modern if modern is not None else legacy
    try:
        sampling["seed"]
        sampling["supernodes"]["num_points"]
        sampling["domains"]["surface"]["anchor"]["num_points"]
        sampling["domains"]["volume"]["anchor"]["num_points"]
    except (KeyError, TypeError) as exc:
        raise ValueError("显式实验缺少 model.sampling 种子或采样预算") from exc
    return sampling


def read_experiment(path: Path | None) -> tuple[dict, dict]:
    """未指定实验才采用参考默认；指定后必须提供完整必要声明。"""
    if path is None:
        return {}, {}
    user = yaml.safe_load(Path(path).read_text())
    return user, experiment_sampling(user)


def configuration_module(config_path: Path):
    """按用户案例位置加载其配置模块，保持验证与实际入口的映射一致。"""
    path = Path(config_path).parent / "configuration.py"
    spec = importlib.util.spec_from_file_location("verified_recipe_configuration", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_application_config(config_path: Path) -> dict:
    """用案例自己的解析和参数提取获得实际业务输入。"""
    module = configuration_module(config_path)
    return module.application_parameters(module.load_configuration(config_path))
