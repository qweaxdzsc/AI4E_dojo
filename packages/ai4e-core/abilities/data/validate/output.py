"""无写入的输出规划，供 dry-run 和提交共用。"""

from collections.abc import Mapping, Sequence
from pathlib import Path

from ai4e_core.base.events import traced


def validate_filemap(filemap: Mapping[str, str]) -> None:
    """目标仅允许单个 .pt 文件名或 .zarr 目录名，且一个文件只对应一个载荷。"""
    if not isinstance(filemap, Mapping) or not filemap:
        raise ValueError("输出对照表必须是非空映射")
    seen: set[str] = set()
    for name, filename in filemap.items():
        if not isinstance(name, str) or not name:
            raise ValueError("对照表逻辑名必须是非空字符串")
        if (
            not isinstance(filename, str)
            or "/" in filename
            or "\\" in filename
            or "\x00" in filename
            or filename in (".", "..")
            or not filename.endswith((".pt", ".zarr"))
        ):
            raise ValueError(f"文件名非法: {filename}")
        if filename.casefold() in seen:
            raise ValueError(f"目标文件名重复: {filename}")
        seen.add(filename.casefold())


def validate_destination(dest: str | Path, *, overwrite: bool = False) -> Path:
    """校验实际样本目录与遗留恢复目录，不因父目录存在而拒绝。"""
    path = Path(dest).absolute()
    if path.is_symlink():
        raise ValueError(f"目标不得为符号链接: {path}")
    if path.exists() and (not overwrite or not path.is_dir()):
        raise FileExistsError(f"输出目录已存在或不是目录: {path}")
    parent = path.parent
    if parent.exists():
        leftovers = [
            p
            for p in parent.iterdir()
            if p.name.startswith(f".{path.name}.") and p.suffix in (".tmp", ".bak")
        ]
        if leftovers:
            raise FileExistsError(f"发现遗留目录，请显式恢复或清理: {leftovers}")
    for ancestor in path.parents:
        if ancestor.exists() and not ancestor.is_dir():
            raise NotADirectoryError(str(ancestor))
    return path


@traced("输出规划")
def plan_output(
    dest: str | Path,
    names: Sequence[str],
    filemap: Mapping[str, str],
    *,
    optional: Sequence[str] = (),
    overwrite: bool = False,
) -> dict[str, str]:
    """校验映射完整性和目标；返回本次实际写出的逻辑名映射。"""
    validate_filemap(filemap)
    unknown_optional = set(optional) - set(filemap)
    if unknown_optional:
        raise ValueError(f"可选字段未在输出中声明: {sorted(unknown_optional)}")
    missing = set(filemap) - set(names) - set(optional)
    if missing:
        raise ValueError(f"缺少必需输出: {sorted(missing)}")
    selected = {key: value for key, value in filemap.items() if key in names}
    if not selected:
        raise ValueError("输出为空，不能报告写入成功")
    validate_destination(dest, overwrite=overwrite)
    return selected
