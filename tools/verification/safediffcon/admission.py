"""SafeDiffCon 参考准入：只读核验原数据和源码，产物写到独立证据目录。

本工具不接入 Dojo 算法，不把数据通过视为论文复现通过。Arrow 分片可直接
从下载 ZIP 流式读取；同时存在展开副本时校验完整字节摘要，禁止静默择一。
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import zipfile
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

import h5py
import numpy as np
from pyarrow import ipc


def digest_stream(stream) -> str:
    """按块计算完整字节摘要，不将大文件整体读入内存。"""
    digest = hashlib.sha256()
    while chunk := stream.read(4 * 1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def digest_file(path: Path) -> str:
    """计算明确文件的内容身份。"""
    with Path(path).open("rb") as stream:
        return digest_stream(stream)


def write_json(path: Path, value: dict) -> None:
    """原子发布验证证据，不调用框架运行记录的私有实现。"""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode="w", dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
    temporary.replace(path)


def audit_burgers(root: Path, *, counts: dict | None = None) -> dict:
    """逐值扫描三个官方分片，核验样本、时间轴和论文不安全样本数量。"""
    formal = counts is None
    counts = counts or {"train": 39000, "cal": 1000, "test": 50}
    unsafe_expected = {"train": 34985, "cal": 900, "test": 50}
    result = {}
    for split, count in counts.items():
        path = Path(root) / f"burgers_{split}.h5"
        before = digest_file(path)
        with h5py.File(path, "r") as source:
            u = source[split]["pde_11-128"]
            f = source[split]["pde_11-128_f"]
            if u.shape != (count, 11, 128) or f.shape != (count, 10, 128):
                raise ValueError(f"{split}: 状态或控制形状不符: {u.shape}, {f.shape}")
            unsafe = 0
            for start in range(0, count, 256):
                states, controls = u[start : start + 256], f[start : start + 256]
                if not np.isfinite(states).all() or not np.isfinite(controls).all():
                    raise ValueError(f"{split}: 非有限数据，起始样本 {start}")
                unsafe += int(np.any(np.abs(states) > 0.8, axis=(1, 2)).sum())
            if formal and unsafe != unsafe_expected[split]:
                raise ValueError(f"{split}: 不安全样本 {unsafe} 与论文不符")
            result[split] = {
                "samples": count,
                "unsafe_samples": unsafe,
                "state_shape": list(u.shape),
                "action_shape": list(f.shape),
                "source": str(path.resolve()),
                "sha256": before,
            }
        if digest_file(path) != before:
            raise ValueError(f"扫描期间数据变化: {path}")
    return {
        "status": "passed",
        "splits": result,
        "model_shape": [3, 16, 128],
        "scale": 10,
        "safety_channel": "max(u**2) broadcast before padding",
    }


def arrow_sources(root: Path, *, shards: int = 4) -> list[dict]:
    """发现精确命名的分片，拒绝重复副本内容不一致或缺失。"""
    root = Path(root)
    found = []
    archives = sorted(root.glob("*.zip"))
    for index in range(shards):
        name = f"data-{index:05d}-of-{shards:05d}.arrow"
        candidates = [{"path": str(p.resolve()), "member": None} for p in sorted(root.rglob(name))]
        for archive in archives:
            with zipfile.ZipFile(archive) as bundle:
                for info in bundle.infolist():
                    if Path(info.filename).name == name:
                        candidates.append({"path": str(archive.resolve()), "member": info.filename})
        if not candidates:
            raise FileNotFoundError(f"缺失 Arrow 分片: {name}")
        for source in candidates:
            with open_arrow(source) as stream:
                source["sha256"] = digest_stream(stream)
        if len({item["sha256"] for item in candidates}) != 1:
            raise ValueError(f"重复分片内容冲突: {name}")
        found.append({"name": name, "selected": candidates[0], "copies": candidates})
    return found


@contextmanager
def open_arrow(source: dict):
    """打开数值分片；ZIP 不解压到原始目录。"""
    if source["member"] is None:
        with Path(source["path"]).open("rb") as stream:
            yield stream
    else:
        with zipfile.ZipFile(source["path"]) as archive, archive.open(source["member"]) as stream:
            yield stream


def audit_tokamak(root: Path, *, counts: tuple = (48950, 1000, 50), shards: int = 4) -> dict:
    """扫描全部轨迹，同时量化原 targets 与源码 outputs 目标的差异。"""
    sources = arrow_sources(root, shards=shards)
    limits = np.cumsum(counts)
    stats = {
        name: {"samples": 0, "unsafe_samples": 0, "target_mse_sum": 0.0, "target_max_abs": 0.0}
        for name in ("train", "cal", "test")
    }
    cursor = 0
    for source in sources:
        rows = 0
        with open_arrow(source["selected"]) as stream:
            reader = ipc.open_stream(stream)
            for batch in reader:
                for record in batch.to_pylist():
                    arrays = {}
                    for field, shape in (
                        ("outputs", (122, 8)),
                        ("actions", (121, 9)),
                        ("targets", (122, 3)),
                    ):
                        values = np.asarray(record[field])
                        if values.shape != shape or not np.isfinite(values).all():
                            raise ValueError(f"Tokamak 样本 {cursor} 的 {field} 形状或数值错误")
                        arrays[field] = values
                    if cursor >= limits[-1]:
                        raise ValueError("Tokamak 样本数超出官方划分")
                    name = ("train", "cal", "test")[
                        int(np.searchsorted(limits, cursor, side="right"))
                    ]
                    entry = stats[name]
                    entry["samples"] += 1
                    entry["unsafe_samples"] += int((arrays["outputs"][:, 4] < 4.98).any())
                    difference = arrays["outputs"][:, [1, 6]] - arrays["targets"][:, [0, 2]]
                    entry["target_mse_sum"] += float(np.square(difference).mean(axis=0).sum())
                    entry["target_max_abs"] = max(
                        entry["target_max_abs"], float(np.abs(difference).max())
                    )
                    cursor += 1
                    rows += 1
        source["rows"] = rows
        with open_arrow(source["selected"]) as stream:
            if digest_stream(stream) != source["selected"]["sha256"]:
                raise ValueError("扫描期间 Arrow 数据变化")
    if cursor != limits[-1]:
        raise ValueError(f"Tokamak 总样本 {cursor} 与划分 {counts} 不符")
    for entry in stats.values():
        entry["outputs_vs_targets_objective"] = entry.pop("target_mse_sum") / entry["samples"]
    return {
        "status": "passed",
        "splits": stats,
        "sources": sources,
        "model_shape": [12, 128],
        "state_columns": [1, 4, 6],
        "scale": [2, 7, 2, 1, 2, 2, 2, 2, 1, 1, 2, 3],
        "target_semantics": "unresolved: source uses outputs; paper describes targets",
    }


def capture_source(root: Path, destination: Path) -> dict:
    """固定已跟踪研究源码、原始补丁和 KSTAR 资源，不改动外部仓库。"""
    root, destination = Path(root).resolve(), Path(destination).resolve()
    if destination == root or root in destination.parents:
        raise ValueError("参考快照不得写入原仓库")
    if destination.exists():
        raise FileExistsError(f"不覆盖已有参考快照: {destination}")
    required = (
        "1D/model/trainer.py",
        "1D/posttrain/post_train.py",
        "1D/inference/inference_ft.py",
        "tokamak/inference/pipeline.py",
        "tokamak/kstar_solver.py",
        "LICENSE",
    )
    for name in required:
        if not (root / name).is_file():
            raise FileNotFoundError(name)

    def git(*args):
        return subprocess.check_output(["git", "-C", str(root), *args])

    tracked = git("ls-files", "-z").decode().split("\0")
    selected = [
        name
        for name in tracked
        if name
        and (
            name.startswith(("1D/", "tokamak/"))
            or name in ("LICENSE", "README.md", "requirements.txt")
        )
        and "__pycache__" not in name
        and not name.endswith(".pyc")
    ]
    destination.mkdir(parents=True)
    files = {}
    try:
        for name in selected:
            original, copied = root / name, destination / name
            if not original.is_file() or original.is_symlink():
                raise ValueError(f"参考文件不是普通文件: {name}")
            before = digest_file(original)
            copied.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(original, copied)
            if digest_file(copied) != before or digest_file(original) != before:
                raise ValueError(f"快照期间源码变化: {name}")
            files[name] = before
        (destination / "source.patch").write_bytes(git("diff", "HEAD", "--binary"))
        manifest = {
            "source_root": str(root),
            "commit": git("rev-parse", "HEAD").decode().strip(),
            "files": files,
            "patch_sha256": digest_file(destination / "source.patch"),
            "untracked": git("ls-files", "--others", "--exclude-standard").decode().splitlines(),
            "scope": "1D and tokamak tracked sources and resources; not 2d",
            "status": "captured",
        }
        write_json(destination / "source.json", manifest)
    except BaseException:
        shutil.rmtree(destination)
        raise
    return manifest


def main() -> int:
    """执行独立准入审计；失败写明证据，不继续正式训练。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--burgers", type=Path, required=True)
    parser.add_argument("--tokamak", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("输出目录已存在；使用新的证据目录，不覆盖历史")
    for source in (args.source, args.burgers, args.tokamak):
        if args.output.resolve().is_relative_to(source.resolve()):
            parser.error("证据目录不得位于原始来源内")
    report = {
        "created_utc": datetime.now(UTC).isoformat(),
        "status": "running",
        "reference_reproduction": "not_run",
        "dojo_migration": "not_started",
    }
    args.output.mkdir(parents=True)
    try:
        print("固定参考源码", flush=True)
        report["source"] = capture_source(args.source, args.output / "source")
        write_json(args.output / "admission.json", report)
        print("扫描 Burgers 全部样本", flush=True)
        report["burgers"] = audit_burgers(args.burgers)
        write_json(args.output / "admission.json", report)
        print("扫描 Tokamak 全部样本和目标差异", flush=True)
        report["tokamak"] = audit_tokamak(args.tokamak)
        report["status"] = "data_passed_science_pending"
    except Exception as error:
        report.update(status="failed", error=f"{type(error).__name__}: {error}")
        raise
    finally:
        write_json(args.output / "admission.json", report)
    print(args.output / "admission.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
