"""打开预处理样本：规范化根目录、按对照表读盘并派生表面距离。"""

from __future__ import annotations

from collections.abc import Mapping
from functools import partial
from pathlib import Path
from typing import Any

import torch

from ai4e_core.abilities.data.save.store import load_named_tensors
from ai4e_core.abilities.data.source.split import (
    load_split_expected,
    load_split_lists,
    require_split_counts,
)
from ai4e_core.abilities.transform.fields import prepare_fields
from ai4e_core.applications.base import Stage

DEFAULT_PREPROCESSED_FOLDER = "preprocessed"
CHANNEL_FIELDS = ("surface_pressure", "volume_sdf")


def resolve_preprocessed_root(
    root: str | Path,
    *,
    folder_name: str = DEFAULT_PREPROCESSED_FOLDER,
) -> Path:
    """若根目录名不是预处理子目录则追加，并验证目录存在。

    Args:
        root: 数据根或已经指向预处理子目录的路径。
        folder_name: 预处理子目录名，默认 ``preprocessed``。

    Returns:
        存在的预处理根目录。

    Raises:
        FileNotFoundError: 解析后的目录不存在。
        ValueError: 解析后的目录名仍不是预处理子目录。
    """
    path = Path(root)
    if path.name != folder_name:
        path = path / folder_name
    if not path.is_dir():
        raise FileNotFoundError(f"预处理数据目录不存在: {path.as_posix()}")
    if path.name != folder_name:
        raise ValueError(f"期望目录名为 {folder_name}，得到 {path.name}")
    return path


def open_preprocessed_sample(
    sample_dir: str | Path,
    filemap: Mapping[str, str],
) -> dict[str, torch.Tensor]:
    """读对照表中的磁盘场，标量压力/体积距离收成单通道，并生成表面距离全零场。

    不套归一化。对照表外的场不读；``cell`` 缺文件时跳过。

    Args:
        sample_dir: 样本目录。
        filemap: 逻辑名到磁盘文件名。

    Returns:
        逻辑名到张量，含 ``surface_sdf``。

    Raises:
        RuntimeError: 必需文件缺失或加载失败，信息含完整路径。
        ValueError: 无法从表面坐标或法向得到点数。
        TypeError: 对照表或载荷类型错误。
    """
    loaded = load_named_tensors(sample_dir, filemap, optional=("cell",))
    fields: dict[str, torch.Tensor] = {}
    for name, payload in loaded.items():
        if not isinstance(payload, torch.Tensor):
            continue
        tensor = payload
        if name in CHANNEL_FIELDS and tensor.ndim == 1:
            tensor = tensor.unsqueeze(1)
        fields[name] = tensor
    count = _surface_point_count(fields)
    fields["surface_sdf"] = torch.zeros(count, 1, dtype=torch.float32)
    return fields


def _surface_point_count(fields: Mapping[str, Any]) -> int:
    """用表面坐标或法向的首维作为表面点数。"""
    for key in ("surface_position", "surface_normals"):
        value = fields.get(key)
        if isinstance(value, torch.Tensor) and value.ndim >= 1:
            return int(value.shape[0])
    raise ValueError("打开样本需要表面坐标或表面法向以生成表面距离")


def open_manifest_sample(
    manifest_path: str | Path, *, partition: str, index: int = 0
) -> dict[str, torch.Tensor]:
    """按产物清单读回实际字段与路径；禁止把归一化数据当物理数据派生。"""
    from ai4e_core.abilities.data.source.manifest import ManifestIndex

    manifest = ManifestIndex(manifest_path)
    if manifest.manifest["state"] != "physical":
        raise ValueError("物理读取接口拒绝归一化数据")
    return manifest.read(partition, index)


def prepare_physical_sample(
    fields: dict[str, torch.Tensor], *, rules=None
) -> dict[str, torch.Tensor]:
    """统一标量通道；零距离仅按显式项目规则在物理空间派生。"""
    return prepare_fields(fields, zero_fields=(rules or {}).get("zero_fields"))


def probe(config: dict, *, prepare=None, dry_run: bool = False) -> dict:
    """按项目配置执行只读或准备探测，贡献组件通过参数注入。"""
    from ai4e_core.abilities.data.save.normalization import save_record
    from ai4e_core.abilities.data.source.manifest import ManifestIndex

    from .normalization import bind_normalization

    train = config.get("train", {})
    mode = train.get("mode", "probe")
    if mode not in {"probe", "prepare"}:
        raise ValueError("数据探测只支持 probe/prepare")
    index = ManifestIndex(
        train.get("manifest") or Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    )
    partition = train.get("probe_split", "test")
    sample_index = int(train.get("probe_index", 0))
    raw = index.read(partition, sample_index)
    is_normalized = index.manifest["state"] == "normalized"
    physical_prepare = partial(
        prepare_physical_sample, rules=config.get("trainprep", {}).get("physical_rules", {})
    )
    physical = raw if is_normalized else physical_prepare(raw)
    result = {
        "physical": physical,
        "sample_id": index.partitions[partition][sample_index],
        "split_counts": {k: len(v) for k, v in index.partitions.items()},
    }
    if mode == "probe":
        if is_normalized:
            from .normalization import Normalization

            frozen = Normalization(index.manifest["normalization"])
            if frozen.digest != index.manifest["normalization_digest"]:
                raise ValueError("归一化记录摘要不一致")
            result["physical"] = {
                name: frozen.inverse(name, value) if name in frozen.transforms else value
                for name, value in raw.items()
            }
        return result
    if prepare is None:
        raise ValueError("准备探测需要显式注入模型的数据组织组件")
    from .normalization import Normalization

    if is_normalized:
        normalization = Normalization(index.manifest["normalization"])
        if normalization.digest != index.manifest["normalization_digest"]:
            raise ValueError("归一化记录摘要不一致")
        normalized = raw
        physical = {
            name: normalization.inverse(name, value) if name in normalization.transforms else value
            for name, value in raw.items()
        }
        result["physical"] = physical
    else:
        normalization = bind_normalization(config, index.manifest)
        normalized = normalization.apply(physical)
    if config["normalization"].get("materialize", False) and not is_normalized:
        from ai4e_core.abilities.data.save.normalization import materialize

        result["normalized_manifest"] = str(
            materialize(
                index,
                normalization,
                config["paths"]["datasets"]["normalize"],
                physical_prepare,
                dry_run=dry_run,
            )
        )
    sampled = prepare(
        normalized,
        config["sampling"],
        sample=result["sample_id"],
        evaluation=True,
        normalization=normalization,
        data_specs=(config.get("model") or {}).get("data_specs"),
        bindings=config["trainprep"],
        geometry_conditioning_dims=config["model"]
        .get("parameters", {})
        .get("geometry_conditioning_dims"),
    )
    record_path = save_record(
        config["paths"]["datasets"]["normalize"]["root"],
        normalization.digest,
        normalization.record,
        dry_run=dry_run,
    )
    result.update(
        normalized=normalized,
        sampled=sampled,
        normalization=normalization.record,
        normalization_path=str(record_path),
    )
    return result


ALLOWED_MODEL = "ab_upt"
DEFAULT_SPLIT_COUNTS = {"train": 789, "test": 100}
DEFAULT_TEST_REPEATS = 10


def repeated_samples(samples: list[str], repeats: int):
    """官方评估名单各走多次，长度等于人数乘重复次数。"""
    if repeats < 1:
        raise ValueError("重复次数必须为正")
    for repeat in range(repeats):
        for index, sample in enumerate(samples):
            yield index, sample, repeat


def prepare_partition_sample(
    index,
    partition: str,
    item: int,
    *,
    prepare,
    normalization,
    physical_prepare,
    normalized_input: bool,
    sampling: dict,
    config: dict,
    epoch: int = 0,
    evaluation: bool = False,
    repeat=None,
):
    """读一个分片样本，套冻结变换后交给注入的采样准备。"""
    raw = index.read(partition, item)
    fields = raw if normalized_input else normalization.apply(physical_prepare(raw))
    chosen = dict(sampling)
    if repeat is not None:
        chosen["seed"] = int(chosen["seed"]) + int(repeat)
    return prepare(
        fields,
        chosen,
        **({"sample_index": item} if sampling.get("random_stream") == "global" else {}),
        sample=index.partitions[partition][item],
        epoch=epoch,
        evaluation=evaluation,
        normalization=normalization,
        data_specs=(config.get("model") or {}).get("data_specs"),
        bindings=config["trainprep"],
        geometry_conditioning_dims=config["model"]
        .get("parameters", {})
        .get("geometry_conditioning_dims"),
    )


def iter_partition_batches(
    index,
    partition: str,
    *,
    prepare,
    collate,
    normalization,
    physical_prepare,
    normalized_input: bool,
    sampling: dict,
    config: dict,
    batch_size: int,
    device,
    epoch: int = 0,
    evaluation: bool = False,
    repeat=None,
):
    """按分片准备并收批，训练评估与独立后处理共用同一采样入口。"""
    from ai4e_core.abilities.training.batch import to_device

    if batch_size < 1:
        raise ValueError("批次必须为正")
    pending = []
    items = range(len(index.partitions[partition]))
    if not evaluation and sampling.get("random_stream") == "global":
        # 与历史 DataLoader(generator=None) 建立迭代器时生成 base_seed 的
        # 随机流推进保持一致，随后 RandomSampler 才从同一全局流取顺序种子。
        torch.empty((), dtype=torch.int64).random_().item()
        items = torch.utils.data.RandomSampler(items)
    from ai4e_core.base.events import sample_context

    for item in items:
        identity = [{"sample_id": index.partitions[partition][item], "index": int(item)}]
        with sample_context("数据准备", identity):
            pending.append(
                prepare_partition_sample(
                    index,
                    partition,
                    item,
                    prepare=prepare,
                    normalization=normalization,
                    physical_prepare=physical_prepare,
                    normalized_input=normalized_input,
                    sampling=sampling,
                    config=config,
                    epoch=epoch,
                    evaluation=evaluation,
                    repeat=repeat,
                )
            )
        if len(pending) == batch_size:
            identities = [
                {
                    "sample_id": value["metadata"]["sample"],
                    "index": index.partitions[partition].index(value["metadata"]["sample"]),
                }
                for value in pending
            ]
            with sample_context("拼批", identities):
                batch = to_device(collate(pending), device)
            yield batch
            pending = []
    if pending:
        identities = [
            {
                "sample_id": value["metadata"]["sample"],
                "index": index.partitions[partition].index(value["metadata"]["sample"]),
            }
            for value in pending
        ]
        with sample_context("拼批", identities):
            batch = to_device(collate(pending), device)
        yield batch


def repeat_seed_epoch(repeat: int) -> int:
    """由重复序号派生独立采样流，避免固定评估种子下重复无新信息。"""
    if repeat < 0:
        raise ValueError("重复序号不能为负")
    return int(repeat)


def read_probe_stage(cfg: Mapping[str, Any]) -> Stage:
    """按配置交出名为 ``train`` 的阶段。

    步骤为：记下模型名称、打开分片、读取探测样本；不执行训练。
    不读命令行，不建运行目录。

    Args:
        cfg: 案例配置。本函数不读磁盘。

    Returns:
        训练准备阶段盒子。
    """
    del cfg
    return Stage(
        name="train",
        steps=[
            select_abupt_step,
            open_splits_step,
            read_probe_sample_step,
        ],
    )


def select_abupt_step(ctx: dict[str, Any]) -> dict[str, Any]:
    """确认已有运行目录，并记下模型为 AB-UPT。"""
    if ctx.get("run_dir") is None:
        raise ValueError("训练阶段需要已有运行目录")
    model = _train_section(ctx["config"]).get("model")
    if str(model) != ALLOWED_MODEL:
        raise ValueError(f"本切片只选定 AB-UPT，得到 {model}")
    ctx["model"] = ALLOWED_MODEL
    return ctx


def open_splits_step(ctx: dict[str, Any]) -> dict[str, Any]:
    """规范化预处理根目录，按名单列分片并校验人数。"""
    config = ctx["config"]
    manifest_path = _train_section(config).get("manifest")
    if manifest_path is None and "paths" in config:
        manifest_path = Path(config["paths"]["datasets"]["root"]) / "manifest.json"
    if manifest_path:
        from ai4e_core.abilities.data.source.manifest import ManifestIndex

        manifest_index = ManifestIndex(manifest_path)
        if manifest_index.manifest["state"] != "physical":
            raise ValueError("旧只读探测仅支持物理数据，归一化数据请使用 trainprep")
        ctx["manifest_index"] = manifest_index
        ctx["manifest_path"] = str(manifest_path)
        ctx["splits"] = manifest_index.partitions
        ctx["split_counts"] = {k: len(v) for k, v in ctx["splits"].items()}
        return ctx
    folder = _root_subdir(config)
    root = resolve_preprocessed_root(_output_dir(config), folder_name=folder)
    splits_path = _splits_path(ctx)
    splits = load_split_lists(splits_path)
    require_split_counts(splits, _expected(config, splits_path))
    ctx["preprocessed_root"] = root
    ctx["splits"] = splits
    ctx["split_counts"] = {name: len(items) for name, items in splits.items()}
    return ctx


def read_probe_sample_step(ctx: dict[str, Any]) -> dict[str, Any]:
    """按对照表打开探测分片的一个样本，默认 test 第 0 个。"""
    train = _train_section(ctx["config"])
    split_name = str(train.get("probe_split") or "test")
    index = int(train.get("probe_index") or 0)
    relatives = list((ctx.get("splits") or {}).get(split_name) or [])
    if index < 0 or index >= len(relatives):
        raise ValueError(f"分片 {split_name} 没有第 {index} 个样本")
    relative = relatives[index]
    if "manifest_path" in ctx:
        from ai4e_core.applications.aero_cfd.trainprep.dataset import (
            prepare_physical_sample,
        )

        fields = prepare_physical_sample(
            ctx["manifest_index"].read(split_name, index),
            rules={"zero_fields": {"surface_sdf": "surface_position"}},
        )
    else:
        sample_dir = Path(ctx["preprocessed_root"]) / relative
        fields = open_preprocessed_sample(sample_dir, _filemap(ctx["config"]))
    ctx["sample"] = fields
    ctx["sample_id"] = relative
    ctx["names"] = list(fields)
    ctx.setdefault("reports", {})["train"] = {
        "model": ctx["model"],
        "split_counts": ctx["split_counts"],
        "sample_id": relative,
        "names": list(fields),
    }
    return ctx


def _train_section(config: Mapping[str, Any]) -> dict[str, Any]:
    """取出 ``train`` 段。"""
    section = config.get("train")
    return dict(section) if isinstance(section, Mapping) else {}


def _pre_section(config: Mapping[str, Any]) -> dict[str, Any]:
    """取出 ``pre`` 段。"""
    section = config.get("pre")
    return dict(section) if isinstance(section, Mapping) else {}


def _root_subdir(config: Mapping[str, Any]) -> str:
    """预处理子目录名，默认 ``preprocessed``。"""
    output = _pre_section(config).get("output")
    if isinstance(output, Mapping) and output.get("root_subdir"):
        return str(output["root_subdir"])
    return "preprocessed"


def _output_dir(config: Mapping[str, Any]) -> Path:
    """读取预处理写出根 ``pre.output.dir``。"""
    output = _pre_section(config).get("output")
    if not isinstance(output, Mapping) or not output.get("dir"):
        raise TypeError("配置缺少 pre.output.dir")
    return Path(str(output["dir"]))


def _filemap(config: Mapping[str, Any]) -> dict[str, str]:
    """读取对照表。"""
    output = _pre_section(config).get("output")
    if not isinstance(output, Mapping) or not output.get("filemap"):
        raise TypeError("配置缺少 pre.output.filemap")
    filemap = output["filemap"]
    if not isinstance(filemap, Mapping):
        raise TypeError("pre.output.filemap 必须是映射")
    return {str(key): str(value) for key, value in filemap.items()}


def _splits_path(ctx: Mapping[str, Any]) -> Path:
    """解析官方或覆盖后的分片名单路径。"""
    raw = _train_section(ctx["config"]).get("splits")
    if not raw:
        raise ValueError("缺少 train.splits")
    path = Path(str(raw))
    if path.is_absolute():
        return path
    recipe_dir = ctx.get("recipe_dir")
    if recipe_dir is None:
        raise ValueError("相对分片路径需要 recipe_dir")
    return Path(recipe_dir) / path


def _expected(config: Mapping[str, Any], splits_path: Path) -> dict[str, int]:
    """配置覆盖优先，其次分片文件，最后官方人数。"""
    override = _train_section(config).get("expected")
    if isinstance(override, Mapping) and override:
        return {str(key): int(value) for key, value in override.items()}
    from_file = load_split_expected(splits_path)
    if from_file:
        return from_file
    return dict(DEFAULT_SPLIT_COUNTS)
