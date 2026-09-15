"""参数化 PDE 阶段交接校验；仅认识公开组件与内容身份。"""

import importlib
import inspect
import json
from pathlib import Path

from ai4e_core.abilities.data.save.bundle import digest, file_digest, load_bundle


def load_component(path):
    """加载完整模块或对象路径，禁止推测具体模型类型。"""
    try:
        return importlib.import_module(path)
    except ModuleNotFoundError as exc:
        if exc.name != path:
            raise
        module, name = path.rsplit(".", 1)
        return getattr(importlib.import_module(module), name)


def source_identity(component):
    """记录公开组件所在模块目录源码摘要，覆盖相邻实现文件。"""
    file = Path(inspect.getfile(component))
    files = {p.name: file_digest(p) for p in sorted(file.parent.glob("*.py"))}
    dependencies = getattr(component, "SOURCE_MODULES", ())
    if dependencies:
        files["declared_dependencies"] = {
            name: file_digest(inspect.getfile(importlib.import_module(name)))
            for name in dependencies
        }
    return digest(files)


def preparation_contract(cfg, dataset, model_component):
    """提取影响物理点集和模型准备的语义，不包含训练权重或轮次。"""
    model = cfg["model"]
    contract = {
        "schema": 1,
        "case": cfg["case"],
        "data": dataset.manifest["content_id"],
        "model_component": source_identity(model_component),
        "model": {
            k: model[k]
            for k in (
                "control_points",
                "degree",
                "hard_initial",
                "sampling",
                "boundary_conditions",
                "initial_conditions",
                "periodic_boundary_conditions",
            )
        },
        "boundary_enforcement": model["constraints"]["boundary_conditions"]["enforcement"],
    }

    # 函数目标/自定义采样的路径未变但源码改变时，冻结点集也必须重建。
    def functions(value):
        if isinstance(value, dict):
            for key, child in value.items():
                if key == "function":
                    yield child
                else:
                    yield from functions(child)
        elif isinstance(value, list):
            for child in value:
                yield from functions(child)

    references = sorted(set(functions(contract["model"])))
    if references:
        contract["user_sources"] = {
            path: source_identity(load_component(path)) for path in references
        }
    return contract


def open_preparation(cfg, dataset, model_component):
    """独立阶段重新打开准备清单并检查语义和文件内容。"""
    path = Path(cfg["trainprep"]["output"]) / "preparation.json"
    value = json.loads(path.read_text())
    if value["contract"] != preparation_contract(cfg, dataset, model_component):
        raise ValueError("准备产物与数据、采样、物理条件或模型实现不一致，请重新准备")
    if digest({k: v for k, v in value.items() if k != "content_id"}) != value["content_id"]:
        raise ValueError("准备清单摘要失效")
    expected = {(r["id"], r["split"]) for r in dataset.manifest["samples"]}
    actual = {(r["id"], r["split"]) for r in value["samples"]}
    if expected != actual or len(actual) != len(value["samples"]):
        raise ValueError("准备清单样本身份不完整或重复")
    return path, value


def read_prepared(path, record):
    """逐个准备样本读盘，并在消费前检查内容摘要。"""
    target = (path.parent / record["path"]).resolve()
    if not target.is_relative_to(path.parent.resolve()) or file_digest(target) != record["sha256"]:
        raise ValueError(f"{record['id']}: 准备样本路径或摘要失效")
    value = load_bundle(target)
    if value["sample"]["id"] != record["id"]:
        raise ValueError("准备样本身份不一致")
    return value
