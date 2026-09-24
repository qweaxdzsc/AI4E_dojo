"""冻结系统Python的精确运行库闭包；不开放整个Homebrew或用户目录。"""

import os
import shutil
import ssl
import stat
import subprocess
import sys
import sysconfig
import uuid
from pathlib import Path


def readonly_runtime():
    """登记标准库native扩展依赖与证书单文件，保留动态加载器使用的别名。"""
    base = Path(sys.base_prefix).resolve()
    paths = {str(base), str(Path(sys._base_executable))}
    alias = (
        Path(sysconfig.get_config_var("BINDIR"))
        / f"python{sys.version_info.major}.{sys.version_info.minor}"
    )
    if alias.is_file():
        paths.add(str(alias))
    pending = list(
        (base / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/lib-dynload").glob(
            "*.so"
        )
    )
    seen = set()
    while pending:
        path = pending.pop()
        resolved = path.resolve(strict=True)
        if resolved in seen:
            continue
        seen.add(resolved)
        result = subprocess.run(
            ["/usr/bin/otool", "-L", str(path)], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines()[1:]:
            dependency = line.strip().split(" (", 1)[0]
            if not dependency.startswith("/") or dependency.startswith(("/usr/lib/", "/System/")):
                continue
            item = Path(dependency)
            if not item.is_file():
                raise FileNotFoundError(f"Python运行库缺失: {item}")
            paths.add(str(item))
            pending.append(item)
    certificates = ssl.get_default_verify_paths()
    if certificates.cafile:
        paths.add(certificates.cafile)
    return sorted(paths)


def independent_copy(source, destination):
    """APFS写时复制仍是独立inode；后续修改互不可见，不采用硬链接。"""
    source, destination = Path(source), Path(destination)
    if source.is_symlink():
        raise ValueError("初始材料不得是链接")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise FileExistsError(destination)
    if sys.platform == "darwin":
        subprocess.run(["/bin/cp", "-cR", str(source), str(destination)], check=True)
    elif source.is_dir():
        shutil.copytree(source, destination)
    else:
        shutil.copyfile(source, destination)
    return destination


def clone_verified_file(reference, destination, expected_sha256):
    """只对字节完全相同的独立快照文件重建APFS副本，收据内容摘要保持不变。

    用于主控冻结环境的存储优化；不修改研究工作区或候选。调用者应保存
    返回的inode/摘要证据。替换前后分别校验，任何不一致都不提升临时副本。
    """
    from ..io import digest

    reference, destination = Path(reference), Path(destination)
    if reference.is_symlink() or destination.is_symlink():
        raise ValueError("存储优化不接受链接")
    before = destination.stat()
    origin = reference.stat()
    if before.st_ino == origin.st_ino or before.st_nlink != 1 or origin.st_nlink != 1:
        raise ValueError("文件必须为独立inode")
    if digest(reference) != expected_sha256 or digest(destination) != expected_sha256:
        raise ValueError("文件内容不符合冻结摘要")

    def attributes(path):
        if sys.platform == "darwin":
            names = subprocess.run(
                ["/usr/bin/xattr", str(path)], capture_output=True, text=True, check=True
            ).stdout.splitlines()
            return {
                name: subprocess.run(
                    ["/usr/bin/xattr", "-px", name, str(path)], capture_output=True, check=True
                ).stdout
                for name in names
            }
        if hasattr(os, "listxattr"):
            return {name: os.getxattr(path, name) for name in os.listxattr(path)}
        return {}

    original_attributes = attributes(destination)
    if attributes(reference) != original_attributes:
        raise ValueError("扩展属性不同，保留原快照")
    temporary = destination.with_name(destination.name + ".clone-" + str(uuid.uuid4()))
    try:
        independent_copy(reference, temporary)
        temporary.chmod(stat.S_IMODE(before.st_mode))
        if digest(temporary) != expected_sha256 or temporary.stat().st_ino == origin.st_ino:
            raise ValueError("新副本摘要或独立性不符")
        # 保留原目标元信息；不因同内容优化改变执行位、时间或扩展属性。
        shutil.copystat(destination, temporary)
        if attributes(temporary) != original_attributes:
            raise ValueError("副本扩展属性变化，保留原快照")
        if digest(destination) != expected_sha256:
            raise ValueError("提升前原快照发生变化")
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            temporary.unlink()
    after = destination.stat()
    return {
        "sha256": expected_sha256,
        "size": before.st_size,
        "before_inode": before.st_ino,
        "after_inode": after.st_ino,
        "reference_inode": origin.st_ino,
        "nlink": after.st_nlink,
        "independent": after.st_ino != origin.st_ino and after.st_nlink == 1,
    }
