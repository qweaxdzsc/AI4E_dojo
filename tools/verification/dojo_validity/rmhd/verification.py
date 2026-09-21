"""正式启动与 round00 协议核查；错误只反馈事实，研究代码仍由组会话修复。"""

import hashlib
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import numpy as np

from ..io import digest, read_json, write_json
from .isolation import probe
from .network import PublicProxy


def schedule_digest():
    """冻结抽样序列摘要：每epoch先70个起点、后70个排列，均 little-endian int64。"""
    result = hashlib.sha256()
    rng = np.random.Generator(np.random.PCG64(42))
    for _ in range(500):
        result.update(rng.integers(0, 162, size=70).astype("<i8").tobytes())
        result.update(rng.permutation(70).astype("<i8").tobytes())
    return result.hexdigest()


def verify_round_zero(comparison, group, source):
    """核科学设置、抽样、训练统计与身份，MPS权重不要求逐位一致。"""
    root, source = Path(comparison), Path(source)
    config = read_json(root / "comparison-protocol.json")
    experiment = Path(config["experiments"][group])
    evidence = read_json(source / "baseline-evidence.json")
    manifest = read_json(experiment / "data/manifest.json")
    stats = read_json(root / "preflight/statistics.json")
    initial = read_json(root / f"evidence/{group}-initial-materials.json")
    for relative in (
        "baseline/initial-checkpoint.pt",
        "baseline/source/model.py",
        "baseline/scientific.json",
        "data/manifest.json",
    ):
        if digest(experiment / relative) != initial[relative]:
            raise ValueError(f"初始冻结材料变化: {relative}")
    expected = {
        "epochs": 500,
        "updates": 2500,
        "device": "mps",
        "initial_checkpoint_sha256": digest(experiment / "baseline/initial-checkpoint.pt"),
        "model_source_sha256": digest(experiment / "baseline/source/model.py"),
        "sampling_schedule_sha256": schedule_digest(),
        "train_ids": [r["id"] for r in manifest["train"]],
        "validation_ids": [r["id"] for r in manifest["validation"]],
    }
    for key, value in expected.items():
        if evidence.get(key) != value:
            raise ValueError(f"round00 协议不符: {key}")
    for key in ("mean", "std"):
        value = np.asarray(evidence[key], dtype=np.float64)
        if value.shape != (6,) or not np.allclose(value, stats[key], rtol=1e-8, atol=1e-12):
            raise ValueError(f"round00 训练统计不符: {key}")
    write_json(
        root / "evidence" / f"{group}-round00-check.json",
        {
            "contract_passed": True,
            "evidence": evidence,
            "limit": "核科学合同与声明；执行真实性须合并原始进程观察、命令、源码和训练日志验收",
        },
    )


def verify_startup(comparison):
    """真实组根预检；临时诊断环境删除后再开正式会话，组内环境仍由agent创建。"""
    root = Path(comparison).resolve()
    if read_json(root / "state.json")["phase"] != "materials_prepared_isolation_pending":
        raise ValueError("启动预检阶段不符")
    config = read_json(root / "comparison-protocol.json")
    results = {}
    for group, location in config["experiments"].items():
        experiment = Path(location)
        protocol = read_json(experiment / "protocol.json")
        workspace = Path(protocol["session_workspace_root"])
        temporary = workspace / ".mps-precheck-runtime"
        if temporary.exists():
            raise FileExistsError("遗留诊断环境需要核对，不能自动覆盖")
        # 使用 canonical 解释器建立独立副本，避免宿主 opt symlink 与环境继承。
        subprocess.run(
            [
                "uv",
                "run",
                "--no-project",
                "--no-sync",
                "--python",
                protocol["python_executable"],
                "python",
                "-m",
                "venv",
                "--without-pip",
                "--copies",
                str(temporary),
            ],
            check=True,
        )
        site = (
            temporary
            / "lib"
            / f"python{sys.version_info.major}.{sys.version_info.minor}"
            / "site-packages"
        )
        with tarfile.open(experiment / "installation/public-packages.tar") as archive:
            archive.extractall(site, filter="data")
        other = Path(config["experiments"]["dojo" if group == "plain" else "plain"]).parent
        try:
            with PublicProxy(root / f"evidence/{group}-probe-network.jsonl") as proxy:
                results[group] = probe(
                    workspace,
                    protocol["runtime_readonly_roots"],
                    [
                        other,
                        root,
                        config["source_root_controller_only"],
                        Path(read_json(root / "private-split.json")["splits"]["test"][0]["path"]),
                    ],
                    root / f"evidence/{group}-isolation.json",
                    python=temporary / "bin/python",
                    proxy_port=proxy.port,
                )
        finally:
            shutil.rmtree(temporary)
    passed = all(r["passed"] and r["mps_probed"] for r in results.values())
    write_json(
        root / "state.json",
        {"phase": "ready" if passed else "isolation_gate_failed", "formal_sessions_started": False},
    )
    return results
