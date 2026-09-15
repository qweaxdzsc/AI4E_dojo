"""步骤参数与普通 callable 的校验；不注册业务能力或决定执行顺序。"""

import hashlib
import inspect
from collections.abc import Callable, Mapping
from dataclasses import asdict, is_dataclass
from functools import partial
from importlib import import_module
from pathlib import Path

from omegaconf import OmegaConf


def plain(value):
    """将配置转换成独立普通容器，保留字段顺序。"""
    from copy import deepcopy

    return (
        OmegaConf.to_container(value, resolve=True)
        if OmegaConf.is_config(value)
        else deepcopy(value)
    )


def validate_step_parameters(config, *, declarations: Mapping[str, Callable]) -> None:
    """按案例声明校验额外配置块；声明只描述参数，不执行计算能力。"""
    config = plain(config)
    for path, validator in declarations.items():
        value = config
        for name in path.split("."):
            if not isinstance(value, Mapping) or name not in value:
                raise ValueError(f"缺少步骤配置: {path}")
            value = value[name]
        if not isinstance(value, Mapping):
            raise TypeError(f"{path} 必须为参数映射")
        try:
            validator(**value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"步骤配置 {path}: {exc}") from exc


def resolve_operation(selection=None, *, default=None, operation=None):
    """解析全限定函数与绑定参数；直接注入与配置选择遵守同一签名。"""
    spec = plain(selection or {})
    if not isinstance(spec, Mapping):
        raise TypeError("能力选择必须为映射")
    target = spec.get("target")
    parameters = spec.get("parameters", {})
    if not isinstance(parameters, Mapping):
        raise TypeError("能力 parameters 必须为映射")
    if operation is not None and target:
        raise ValueError("不能同时直接传入能力与指定 target")
    fn = operation or default
    if target:
        if not isinstance(target, str) or "." not in target:
            raise ValueError("target 必须是可导入的全限定函数路径")
        module, name = target.rsplit(".", 1)
        fn = getattr(import_module(module), name)
    if not callable(fn):
        raise TypeError("步骤需要可调用的能力")
    try:
        inspect.signature(fn).bind_partial(**parameters)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"能力参数与签名不符: {exc}") from exc
    return partial(fn, **parameters) if parameters else fn


def operation_record(operation) -> dict:
    """记录实际实现和绑定参数；源文件内容变化使扩展来源失效。"""
    parameters = {}
    fn = operation
    if isinstance(fn, partial):
        if fn.args:
            raise ValueError("可冻结能力只允许通过具名参数绑定")
        parameters = plain(fn.keywords or {})
        fn = fn.func
    target = fn if inspect.isfunction(fn) or inspect.isclass(fn) else type(fn)
    path = inspect.getsourcefile(target)
    if path is None:
        raise ValueError("扩展能力必须提供可追踪的 Python 源码")
    record = {
        "name": target.__module__ + "." + target.__qualname__,
        "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest(),
        "parameters": parameters,
    }
    if not (inspect.isfunction(fn) or inspect.isclass(fn)):
        if is_dataclass(fn):
            record["constructor"] = asdict(fn)
        elif not vars(fn):
            record["constructor"] = {}
        else:
            raise ValueError(
                "有状态能力对象请使用 dataclass 或通过 target/parameters 提供可重建工厂"
            )
    if "<locals>" in record["name"] or "<lambda>" in record["name"]:
        raise ValueError("冻结能力必须可从模块导入，不能保存闭包或匿名函数")
    return record


def restore_operation(record):
    """从冻结声明重建普通函数或可声明对象，并核对实现内容。"""
    module, name = record["name"].rsplit(".", 1)
    fn = getattr(import_module(module), name)
    if "constructor" in record:
        fn = fn(**record["constructor"])
    if record.get("parameters"):
        fn = partial(fn, **record["parameters"])
    actual = operation_record(fn)
    if any(actual.get(key) != value for key, value in record.items()):
        raise ValueError("冻结能力实现发生变化，请重新准备或训练")
    return fn
