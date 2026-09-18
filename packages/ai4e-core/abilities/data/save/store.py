"""具名张量目录提交；覆盖失败恢复旧目录，不承担业务字段选择。"""

import shutil
import warnings
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from uuid import uuid4

import torch

from ai4e_core.abilities.data.validate import plan_output
from ai4e_core.base.events import traced


class BackupCleanupWarning(UserWarning):
    """正式目录已提交，但旧备份清理失败。"""


def write_tensor_file(path: str | Path, payload, *, overwrite: bool = False) -> Path:
    """原子提交一个张量或具名张量包；失败不替换已有文件。"""
    entries = list(payload.values()) if isinstance(payload, Mapping) else [payload]
    if not entries or not all(isinstance(value, torch.Tensor) for value in entries):
        raise TypeError("载荷必须为张量或非空具名张量映射")
    target = Path(path)
    if target.exists() and not overwrite:
        raise FileExistsError(str(target))
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        with temporary.open("wb") as stream:
            torch.save(payload, stream)
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


@traced("张量提交")
def write_named_tensors(
    dest: str | Path,
    payloads: Mapping[str, torch.Tensor | Mapping[str, torch.Tensor]],
    filemap: Mapping[str, str],
    *,
    optional: Sequence[str] = (),
    overwrite: bool = False,
    extra_writers: Mapping[str, Any] | None = None,
) -> Path:
    """预检后写同级临时目录，备份旧目录再提升；恢复失败保留所有证据。

    每次提交只记 debug；循环里的常规摘要由 application 阶段输出。
    """
    selected = plan_output(dest, list(payloads), filemap, optional=optional, overwrite=overwrite)
    for name in selected:
        value = payloads[name]
        entries = value.values() if isinstance(value, Mapping) else [value]
        if isinstance(value, Mapping) and not value:
            raise ValueError(f"载荷为空: {name}")
        if not all(isinstance(t, torch.Tensor) for t in entries):
            raise TypeError(f"载荷必须为张量或具名张量映射: {name}")
    extra_writers = dict(extra_writers or {})
    for filename in extra_writers:
        if Path(filename).name != filename or filename in selected.values():
            raise ValueError("附加产物文件名非法或冲突")
    target = Path(dest).absolute()
    target.parent.mkdir(parents=True, exist_ok=True)
    token = uuid4().hex
    temporary = target.parent / f".{target.name}.{token}.tmp"
    backup = target.parent / f".{target.name}.{token}.bak"
    temporary.mkdir()
    backed_up = False
    try:
        for name, filename in selected.items():
            if filename.endswith(".zarr"):
                from .zarr import write_zarr

                write_zarr(temporary / filename, payloads[name])
            else:
                with (temporary / filename).open("wb") as stream:
                    torch.save(payloads[name], stream)
        for filename, write in extra_writers.items():
            write(temporary / filename)
        if target.exists():
            if not overwrite:
                raise FileExistsError(str(target))
            target.replace(backup)
            backed_up = True
        try:
            temporary.replace(target)
        except Exception as commit_error:
            if backed_up:
                try:
                    backup.replace(target)
                except Exception as restore_error:  # noqa: BLE001 - 恢复失败必须保留备份并报告路径
                    raise RuntimeError(
                        f"提交及恢复失败，旧数据保留在 {backup}；新数据在 {temporary}；"
                        f"目标 {target}；恢复原因: {restore_error}"
                    ) from commit_error
            raise
    except Exception:
        # 恢复失败时不得清除仍可人工恢复的新旧目录。
        if not backup.exists() and temporary.exists():
            shutil.rmtree(temporary, ignore_errors=True)
        raise
    if backed_up:
        try:
            shutil.rmtree(backup)
        except OSError as exc:
            warnings.warn(
                f"已提交 {target}，备份清理失败: {backup}: {exc}",
                BackupCleanupWarning,
                stacklevel=2,
            )
    return target


@traced("张量读取")
def load_named_tensor(path: str | Path) -> Any:
    """仅加载张量和具名张量映射。

    每次调用只记 debug，供循环按样本读取；失败仍为错误。阶段摘要由
    application 输出，不在此重复 info。
    """
    if Path(path).suffix == ".zarr":
        from .zarr import read_zarr

        return read_zarr(path)
    return torch.load(Path(path), weights_only=True)


def load_named_tensors(
    sample_dir: str | Path, filemap: Mapping[str, str], *, optional: Sequence[str] = ()
) -> dict[str, Any]:
    """按对照表读回样本目录里已有的逻辑名。

    对照表外的不读、不造。可选逻辑名缺文件时跳过，其余缺失或加载失败
    包装为带完整路径的 ``RuntimeError``。可选性由业务层传入。

    Args:
        sample_dir: 样本目录。
        filemap: 逻辑名到磁盘文件名。
        optional: 允许缺失的逻辑名。

    Returns:
        逻辑名到载荷。

    Raises:
        TypeError: 对照表不是映射。
        ValueError: 逻辑名或文件名非法。
        RuntimeError: 必需文件缺失或 ``torch.load`` 失败。
    """
    from ai4e_core.abilities.data.validate import validate_filemap

    validate_filemap(filemap)
    result = {}
    for name, filename in filemap.items():
        path = Path(sample_dir) / filename
        if name in optional and not path.exists():
            continue
        try:
            result[name] = load_named_tensor(path)
        except Exception as exc:
            raise RuntimeError(f"Failed to load {path}: {exc}") from exc
    return result
