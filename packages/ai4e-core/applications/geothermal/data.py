"""地热发布数据的冻结交接；来源格式由注入的检查器解释。"""

import json
import shutil
from pathlib import Path

from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.data.save.arrays import save_json


def publish_dataset(source, output, *, inspect, kind="dataset"):
    """检查来源并复制已核验文件；仅完整发布才写出入口清单。"""
    source, output = Path(source).resolve(), Path(output).resolve()
    if output == source or output.is_relative_to(source):
        raise ValueError("数据输出不能位于只读来源目录内")
    record = inspect(source)
    output.mkdir(parents=True, exist_ok=True)
    for name, checksum in record["sha256"].items():
        if Path(name).name != name:
            raise ValueError("发布文件名必须是相对单文件名")
        target = output / name
        if target.exists():
            raise FileExistsError(target)
        shutil.copyfile(source / name, target)
        if digest(target) != checksum:
            raise ValueError("发布文件摘要不一致: " + name)
    record = {**record, "kind": kind, "origin": str(source), "source": "."}
    path = output / (kind + ".json")
    save_json(path, record)
    return str(path)


def read_bundle(path, *, kind=None, verify=True):
    """读回冻结记录并验证所有实际依赖；禁止出界或静默接受已变更输入。"""
    path = Path(path).resolve()
    record = json.loads(path.read_text())
    if record.get("version") != 1 or (kind and record.get("kind") != kind):
        raise ValueError("地热准备记录类型或版本不符")
    for name, checksum in record["sha256"].items():
        target = path.parent / name
        if Path(name).name != name or not target.is_file():
            raise ValueError("数据依赖缺失或越界: " + name)
        if verify and digest(target) != checksum:
            raise ValueError("数据依赖已变更: " + name)
    return record


def prepare_inputs(dataset, output):
    """保持作者冻结统计量与张量不变，将准备产物交付为自包含副本。"""
    record = read_bundle(dataset, kind="dataset")
    return publish_dataset(
        Path(dataset).parent, output, inspect=lambda _: record, kind="preparation"
    )


def record_bundle(session, path, *, kind, stage):
    """把清单及全部数据依赖交付给公开资产入口。"""
    path = Path(path).resolve()
    record = read_bundle(path, verify=False)
    session.record_asset(
        "geothermal_" + kind,
        path,
        kind=kind,
        stage=stage,
        dependencies=[path.parent / n for n in record["sha256"]],
        bundle_root=path.parent,
    )
