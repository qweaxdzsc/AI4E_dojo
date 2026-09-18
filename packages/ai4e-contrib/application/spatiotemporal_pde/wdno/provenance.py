"""冻结实际组件和数值代码身份，避免变体冒领原版。"""

import inspect
from pathlib import Path

from ai4e_core.abilities.data.save.array_manifest import digest


def identity(function) -> dict:
    """普通可重建函数的路径和所在文件摘要。"""
    module = inspect.getmodule(function)
    filename = inspect.getsourcefile(function)
    if module is None or filename is None or "<locals>" in function.__qualname__:
        raise ValueError("持久化组件需要可重建的模块级函数")
    return {"callable": f"{module.__name__}.{function.__qualname__}", "sha256": digest(filename)}


def numerical_sources() -> dict:
    """冻结 WDNO 的实际已安装能力源码，覆盖传递依赖。"""
    from ai4e_contrib.ability.model.wdno import unet

    ability = Path(unet.__file__).resolve().parents[2]
    files = {}
    for section in ("model", "constraint", "inference", "transform", "eval"):
        for path in sorted((ability / section / "wdno").glob("*.py")):
            files[str(path.relative_to(ability))] = digest(path)
    return files


def recipe_sources(script: str) -> dict:
    """冻结本次可编辑研究目录的直接Python文件，由writer发布来源记录。"""
    directory = Path(script).resolve().parent
    return {
        path.name: {"sha256": digest(path), "text": path.read_text()}
        for path in sorted(directory.glob("*.py"))
    }
