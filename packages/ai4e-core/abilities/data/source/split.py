"""按传入名单列分片，不扫盘冒充官方顺序。"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import yaml

SPLIT_BUCKETS = ("train", "test", "eval")
SLICE_LABELS = {"train": "训练集", "test": "测试集", "eval": "评价集"}


def load_split_lists(source: str | Path | Mapping[str, Any]) -> dict[str, list[str]]:
    """从映射或 YAML 取出分片相对路径名单，保持原顺序。

    忽略 ``expected`` 等非名单键。名单值必须是字符串序列。

    Args:
        source: 已展开的映射，或 YAML 路径。

    Returns:
        分片名到相对路径列表。

    Raises:
        TypeError: 根节点或名单不是映射/序列。
        FileNotFoundError: YAML 不存在。
    """
    data = _as_mapping(source)
    splits: dict[str, list[str]] = {}
    for key, value in data.items():
        if key == "expected":
            continue
        if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
            raise TypeError(f"分片 {key} 必须是路径列表")
        splits[str(key)] = [str(item) for item in value]
    return splits


def load_split_expected(source: str | Path | Mapping[str, Any]) -> dict[str, int]:
    """读取分片文件里的期望人数；没有则返回空映射。"""
    data = _as_mapping(source)
    expected = data.get("expected")
    if expected is None:
        return {}
    if not isinstance(expected, Mapping):
        raise TypeError("分片期望人数必须是映射")
    return {str(key): int(value) for key, value in expected.items()}


def require_split_counts(
    splits: Mapping[str, Sequence[str]],
    expected: Mapping[str, int],
) -> None:
    """校验各分片人数。人数不对则失败，不改名单。

    Args:
        splits: 分片名到相对路径。
        expected: 分片名到期望人数。

    Raises:
        ValueError: 某分片人数与期望不符。
        TypeError: 期望表不是映射。
    """
    if not isinstance(expected, Mapping):
        raise TypeError("分片期望人数必须是映射")
    for name, count in expected.items():
        actual = len(splits.get(str(name), ()))
        if actual != int(count):
            raise ValueError(f"分片 {name} 期望 {count} 个样本，实际 {actual}")


def flatten_samples(partitions: Mapping[str, Sequence[str]]) -> list[str]:
    """跨原分片去重保序，得到当前清单已经处理出来的全部样本。"""
    seen: list[str] = []
    names: set[str] = set()
    for samples in partitions.values():
        for sample in samples:
            identity = str(sample)
            if identity in names:
                continue
            names.add(identity)
            seen.append(identity)
    return seen


def named_slice(name: Any, default: str = "train") -> str:
    """分片名缺省为 default；旧 validation 并进 eval。"""
    value = str(name or default)
    return "eval" if value == "validation" else value


def complete_split_buckets(
    partitions: Mapping[str, Sequence[str]] | None,
) -> dict[str, list[str]]:
    """补齐固定三分片；缺的桶为空名单。旧 validation 并进 eval。"""
    source = partitions or {}
    result = {name: [str(item) for item in source.get(name) or []] for name in SPLIT_BUCKETS}
    if not result["eval"] and source.get("validation"):
        result["eval"] = [str(item) for item in source["validation"]]
    return result


def published_slices(record: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    """从准备记录读出 train/test/eval；不改历史文件，缺的切片人数为 0。"""
    payload = record if isinstance(record, Mapping) else {}
    partitions = payload.get("partitions")
    partitions = partitions if isinstance(partitions, Mapping) else {}
    counts = payload.get("split_counts")
    counts = counts if isinstance(counts, Mapping) else {}
    split = payload.get("split")
    split = split if isinstance(split, Mapping) else {}
    completed = complete_split_buckets(partitions)
    method = str(split.get("method") or "original")
    try:
        seed = int(split.get("seed") or 0)
    except (TypeError, ValueError):
        seed = 0
    slices: list[dict[str, Any]] = []
    for name in SPLIT_BUCKETS:
        if name in partitions or (name == "eval" and "validation" in partitions):
            count = len(completed[name])
        elif name in counts:
            try:
                count = int(counts[name] or 0)
            except (TypeError, ValueError):
                count = 0
        else:
            count = 0
        slices.append(
            {
                "name": name,
                "role": name,
                "label": SLICE_LABELS[name],
                "count": count,
                "method": method,
                "seed": seed,
            }
        )
    return slices


def default_counts(partitions: Mapping[str, Sequence[str]]) -> dict[str, int]:
    """用原分片人数作默认值；缺的桶为 0，未识别分片并进 train。"""
    counts = {name: len(partitions.get(name) or []) for name in SPLIT_BUCKETS}
    leftovers = flatten_samples(
        {key: value for key, value in partitions.items() if key not in SPLIT_BUCKETS}
    )
    counts["train"] += len(leftovers)
    return counts


def restrict_partitions(
    partitions: Mapping[str, Sequence[str]],
    samples: Sequence[str] | None,
) -> dict[str, list[str]]:
    """执行范围指定样本时先缩小样本池；未指定则保持全部已处理样本。"""
    if samples is None:
        return {str(key): [str(item) for item in value] for key, value in partitions.items()}
    allowed = [str(item) for item in samples]
    if not allowed:
        raise ValueError("指定样本不能为空")
    if len(set(allowed)) != len(allowed):
        raise ValueError("指定样本重复")
    known = set(flatten_samples(partitions))
    missing = [item for item in allowed if item not in known]
    if missing:
        raise ValueError(f"指定样本不在当前清单: {missing[0]}")
    chosen = set(allowed)
    return {
        str(key): [str(item) for item in value if str(item) in chosen]
        for key, value in partitions.items()
        if any(str(item) in chosen for item in value)
    }


def resolve_split(
    partitions: Mapping[str, Sequence[str]],
    split: Mapping[str, Any] | None,
) -> dict[str, list[str]]:
    """按准备声明重划 train/test/eval；不改张量，只返回新名单。

    ``method=original`` 保持原成员（未识别分片并进 train），忽略数量改写。
    ``method=random`` 打平后按种子抽取，数量之和必须等于全部样本，train 至少一个。
    可选 ``samples`` 先限定执行范围，再划分。
    """
    declaration = split or {}
    source = restrict_partitions(partitions, declaration.get("samples"))
    method = str(declaration.get("method") or "original")
    if method == "original":
        result = {name: [str(item) for item in source.get(name) or []] for name in SPLIT_BUCKETS}
        extras = flatten_samples(
            {key: value for key, value in source.items() if key not in SPLIT_BUCKETS}
        )
        result["train"] = list(result["train"]) + extras
        return {name: items for name, items in result.items() if items}
    if method != "random":
        raise ValueError(f"不支持的抽取方法: {method}")
    counts = declaration.get("counts") or default_counts(source)
    return draw_random(flatten_samples(source), counts, int(declaration.get("seed") or 0))


def draw_random(
    samples: Sequence[str],
    counts: Mapping[str, Any],
    seed: int,
) -> dict[str, list[str]]:
    """按种子打乱后切成 train/test/eval；空桶不进入结果。"""
    normalized = {name: int(counts.get(name) or 0) for name in SPLIT_BUCKETS}
    if any(value < 0 for value in normalized.values()):
        raise ValueError("分片数量不能为负")
    if sum(normalized.values()) != len(samples):
        raise ValueError(
            f"分片数量之和必须等于全部样本数 {len(samples)}，当前为 {sum(normalized.values())}"
        )
    if normalized["train"] < 1:
        raise ValueError("训练分片至少需要 1 个样本")
    pool = [str(item) for item in samples]
    random.Random(seed).shuffle(pool)
    result: dict[str, list[str]] = {}
    offset = 0
    for name in SPLIT_BUCKETS:
        size = normalized[name]
        if size:
            result[name] = pool[offset : offset + size]
        offset += size
    return result


def apply_declared_split(index, config: Mapping[str, Any], overlay=None) -> None:
    """把准备记录里的名单或当前 ``trainprep.split`` 套到已打开的清单索引。"""
    if overlay:
        # 原分片已经完全相同时保持 (split, sample) 身份；同名样本可来自
        # 不同文件，不能在恢复准备时先打平再查找而制造身份冲突。
        current = {key: list(names) for key, names in index.partitions.items()}
        frozen = {key: list(names) for key, names in overlay.items()}
        if current != frozen:
            index.remap_partitions(overlay)
        return
    split = (config.get("trainprep") or {}).get("split")
    if split:
        index.remap_partitions(resolve_split(index.partitions, split))


def _as_mapping(source: str | Path | Mapping[str, Any]) -> Mapping[str, Any]:
    """文件读成映射，已是映射则原样返回。"""
    if isinstance(source, Mapping):
        return source
    path = Path(source)
    if not path.is_file():
        raise FileNotFoundError(f"分片名单不存在: {path.as_posix()}")
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, Mapping):
        raise TypeError(f"分片名单根节点必须是映射: {path.as_posix()}")
    return loaded
