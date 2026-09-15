"""ShapeNet-Car 的样本身份、官方分片与字段来源；不加载网格。"""

from collections.abc import Mapping
from pathlib import Path

import yaml
from omegaconf import OmegaConf

from ai4e_core.applications.base.dataset import Dataset
from ai4e_core.base.events import event, operation

MANIFEST_PATH = Path(__file__).with_name("manifest.yaml")


def open_dataset(*, root, manifest=None, samples="all", partition="official", check_exists=True) -> Dataset:
    """按 manifest 打开按需数据集；显式样本必须存在且恰好归属一个分片。"""
    samples = (
        OmegaConf.to_container(samples, resolve=True) if OmegaConf.is_config(samples) else samples
    )
    partition = (
        OmegaConf.to_container(partition, resolve=True)
        if OmegaConf.is_config(partition)
        else partition
    )
    with operation("数据集", root=str(root)):
        root = Path(root).resolve()
        if not root.is_dir():
            raise FileNotFoundError(f"原始数据目录不存在: {root}")
        path = Path(manifest or MANIFEST_PATH).resolve()
        metadata = yaml.safe_load(path.read_text())
        if metadata.get("version") != 1:
            raise ValueError("不支持的原始数据 manifest 版本")
        if partition == "official":
            source = path.parent / metadata["partition"]
            groups = yaml.safe_load(source.read_text())
            expected = groups.pop("expected", {})
            if any(len(groups.get(k, [])) != v for k, v in expected.items()):
                raise ValueError("官方分片数量与 manifest 不一致")
        elif isinstance(partition, Mapping):
            groups = dict(partition)
        else:
            groups = yaml.safe_load(Path(partition).read_text())
        if not groups or set(groups) - {"train", "eval", "test"}:
            raise ValueError("分片必须是 train/eval/test 的非空映射")
        all_items = []
        for name, values in groups.items():
            if not isinstance(values, (list, tuple)):
                raise TypeError(f"分片 {name} 必须是样本列表")
            for value in values:
                item = Path(value)
                if (
                    item.is_absolute()
                    or ".." in item.parts
                    or value in all_items
                    or item.as_posix() != value
                    or value == "."
                ):
                    raise ValueError(f"非法或重复/跨分片样本: {value}")
                all_items.append(value)
        if samples == "all":
            selected = all_items
        elif isinstance(samples, (list, tuple)):
            selected = list(samples)
        else:
            raise TypeError("dataset.samples 必须为 all 或显式样本列表")
        if not selected or len(selected) != len(set(selected)) or set(selected) - set(all_items):
            raise ValueError("样本选择为空、重复或未出现在分片名单中")
        for value in selected:
            target = (root / value).resolve()
            if not target.is_relative_to(root) or (check_exists and not target.is_dir()):
                raise FileNotFoundError(f"样本不存在或越出数据根: {target}")
        chosen = {k: tuple(v for v in values if v in selected) for k, values in groups.items()}
        chosen = {k: v for k, v in chosen.items() if v}
        event(
            "数据集", "选择结果", 样本总数=len(selected), **{k: len(v) for k, v in chosen.items()}
        )
        metadata["manifest_path"] = str(path)
        metadata["reference_statistics"] = str(path.parent / metadata["reference_statistics"])
        return Dataset(root, tuple(selected), chosen, metadata)
