"""运行目录的唯一写入方；按事件元信息分流阶段日志、摘要与堆栈。"""

from __future__ import annotations

import json
import logging
import subprocess
import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from omegaconf import OmegaConf


class RunWriter:
    """只写一次运行的配置、日志和摘要，不写训练张量。"""

    def __init__(self, run_dir: Path) -> None:
        self.run_dir = Path(run_dir)

    @classmethod
    def create(cls, run_root: str | Path, *, nested: bool = True) -> RunWriter:
        """在 ``runs/`` 下新建本次运行目录。

        Args:
            run_root: 运行根目录，其下会出现 ``runs/<时间戳>_<短号>/``。

        Returns:
            已建好目录的写入方。
        """
        from .provenance import MANAGED

        managed = MANAGED.get()
        if managed is not None:
            if managed["claimed"]:
                raise RuntimeError("multiple_core_sessions_in_one_run")
            if Path(run_root).resolve() != Path(managed["context"].run_dir).resolve().parent:
                raise ValueError("managed_run_root_mismatch")
            managed["claimed"] = True
            return managed["writer"]
        stamp = datetime.now(UTC).astimezone().strftime("%Y-%m-%dT%H-%M-%S")
        base = Path(run_root) / "runs" if nested else Path(run_root)
        run_dir = base / f"{stamp}_{uuid4().hex[:6]}"
        run_dir.mkdir(parents=True)
        (run_dir / "inputs").mkdir()
        (run_dir / "logs").mkdir()
        return cls(run_dir)

    @property
    def log_path(self) -> Path:
        """运行日志文件路径。"""
        return self.run_dir / "logs" / "run.log"

    def write_inputs(self, source_config: str | Path | None, resolved: dict[str, Any]) -> None:
        """只保存展开校验后的最终生效配置。

        Args:
            source_config: 用户提交的原始 YAML。
            resolved: 覆盖、展开默认并联合校验后的配置树。
        """
        OmegaConf.save(OmegaConf.create(resolved), self.run_dir / "inputs" / "config.yaml")

    def write_code_snapshot(self, trees: list[str | Path]) -> Path:
        """打包当次源码，含未提交与未跟踪文件，排除忽略规则。"""
        files = _snapshot_files([Path(item) for item in trees])
        if not files:
            raise ValueError("源码快照没有可打包文件")
        target = self.run_dir / "code.tar.gz"
        with tarfile.open(target, "w:gz") as archive:
            for name, path in files:
                archive.add(path, arcname=name, recursive=False)
        return target

    def write_artifact(self, name: str, value: dict) -> Path:
        """原子发布可序列化的阶段交付，不允许逃出运行目录。"""
        if not name or Path(name).name != name or not name.endswith(".json"):
            raise ValueError("阶段交付必须为单一 JSON 文件名")
        folder = self.run_dir / "artifacts"
        folder.mkdir(exist_ok=True)
        target = folder / name
        temporary = folder / f".{name}.{uuid4().hex}.tmp"
        try:
            temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return target

    def write_summary(self, summary: dict[str, Any]) -> None:
        """写入作业摘要，不得包含张量文件。

        Args:
            summary: 可 JSON 序列化的计数、路径和失败信息。
        """
        self._write_json(self.run_dir / "summary.json", summary)

    def write_provenance(self, context: dict) -> None:
        """在计算前原子保存完整版本及来源；task 无需回写 run。"""
        self._write_json(self.run_dir / "lineage.json", context)

    def _write_json(self, target: Path, value: dict) -> None:
        """唯一 writer 的同级临时 JSON 提交。"""
        temporary = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
        try:
            temporary.write_text(
                json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8"
            )
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)

    def attach_log(self, logger: logging.Logger) -> logging.Handler:
        """创建并连接运行日志写入方，调用方负责在 finally 关闭。"""
        handler = logging.FileHandler(self.log_path, encoding="utf-8")
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)
        return handler

    def attach_logs(self, logger: logging.Logger) -> list[logging.Handler]:
        """按事件元信息筛选控制台摘要；能力详情和堆栈分别写入独占文件。"""

        class Readable(logging.Formatter):
            def formatException(self, exc_info):
                return ""

            def format(self, record):
                import copy

                clean = copy.copy(record)
                clean.exc_info = None
                clean.exc_text = None
                return super().format(clean)

        class Console(logging.Filter):
            def filter(self, record):
                return (
                    record.levelno >= logging.ERROR
                    or getattr(record, "operation", "")
                    in {"运行", "阶段", "数据集", "批量前处理", "统计", "数据清单"}
                    or getattr(record, "event_state", "") == "进度"
                )

        detail = logging.FileHandler(self.log_path, encoding="utf-8")
        detail.setFormatter(Readable("%(asctime)s %(levelname)s %(message)s"))
        errors = logging.FileHandler(
            self.run_dir / "logs" / "errors.log", encoding="utf-8", delay=True
        )
        errors.setLevel(logging.ERROR)
        errors.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        console = logging.StreamHandler()
        console.addFilter(Console())
        console.setFormatter(Readable("%(levelname)s %(message)s"))
        logger.setLevel(logging.INFO)
        for handler in (detail, errors, console):
            logger.addHandler(handler)
        return [detail, errors, console]

    def write_checkpoint(self, label: str, payload: dict) -> Path:
        """原子提交状态字典检查点；失败时保留旧文件。"""
        import torch

        if label not in {"best", "latest", "last", "ema_latest"}:
            raise ValueError("未知检查点标签")
        folder = self.run_dir / "checkpoints"
        folder.mkdir(exist_ok=True)
        target = folder / f"{label}.pt"
        temporary = folder / f".{label}.{uuid4().hex}.tmp"
        try:
            torch.save(payload, temporary)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        return target


def _git_root(path: Path) -> Path | None:
    """向上查找 git 仓库根。"""
    current = path.resolve()
    if current.is_file():
        current = current.parent
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    return None


def _snapshot_files(trees: list[Path]) -> list[tuple[str, Path]]:
    """收集各树中应快照的文件，优先走 git 清单。"""
    collected: dict[str, Path] = {}
    for tree in trees:
        root = Path(tree).resolve()
        if not root.exists():
            raise FileNotFoundError(f"源码快照路径不存在: {root}")
        if root.is_file():
            collected[str(Path(root.parent.name) / root.name)] = root
            continue
        git = _git_root(root)
        if git is None:
            for path in root.rglob("*"):
                if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
                    collected[str(Path(root.name) / path.relative_to(root))] = path
            continue
        relative = "." if root == git else str(root.relative_to(git))
        listed = subprocess.run(
            ["git", "-C", str(git), "ls-files", "-co", "--exclude-standard", relative],
            check=False,
            capture_output=True,
            text=True,
        )
        if listed.returncode != 0:
            raise ValueError("无 git 不能写入可复现源码快照")
        for line in listed.stdout.splitlines():
            path = git / line
            if path.is_file():
                collected[line] = path
    return sorted(collected.items())
