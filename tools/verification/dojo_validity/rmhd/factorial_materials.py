"""四单元冻结材料：指定网络与自主选模分开，研究资源只从冻结wheel交付。"""

import shutil
import subprocess
import sys
import tarfile
import tomllib
import uuid
import zipfile
from pathlib import Path

import numpy as np

from ..io import digest, inventory, read_json, write_json
from .materials import REPO, SUBMISSION, installed_dependencies
from .protocol import gate
from .runtime import independent_copy, readonly_runtime

CELLS = {
    "BP": {"baseline_provided": True, "dojo_available": False, "slug": "rmhd-unet-plain"},
    "BD": {"baseline_provided": True, "dojo_available": True, "slug": "rmhd-unet-dojo"},
    "NP": {"baseline_provided": False, "dojo_available": False, "slug": "rmhd-open-plain"},
    "ND": {"baseline_provided": False, "dojo_available": True, "slug": "rmhd-open-dojo"},
}

COMMON = """# 科学任务与提交

研究JOREK model600二维简化RMHD数值模拟。原始train/validation数据在data/中，
尚未处理。每轨迹六场Psi,u,zj,omega,rho,T，各[211,100,100]，按保存帧解释。
全部数据读取、校验、统计、窗口、训练装配由你实际完成，可复用公开库，不要求手写所有函数。
输入连续10帧，预测未来40帧；验证起点0、80、161，每轨迹三个窗口。
参数/统计/学习型处理只能拟合训练集；验证用于选方案，不参与梯度或统计拟合。
推理不能用未来真值回填。隐藏测试由主控在研究结束后评价，不提供给你。

精度第一，但最终完整预测P95必须<=50ms。主指标mean_field_relative_l2：
逐轨迹/窗口/字段在完整未来40帧100x100求||pred-truth||2/||truth||2，再等权平均。
使用FP64复算，不拼接量级不同的场，不用训练MSE替代。零真值范数、非有限、
缺样本或形状错误显式失败。字段顺序固定。只使用train/validation，不重新下载隐藏轨迹。
公共网络搜索可用，任何新增数据下载保存来源和用途。

在round-NN/submission/交付自包含候选，禁止链接和依赖可变工作区。
submission.json字段：interface="rmhd-predict-v1"、round整数、entrypoint、checkpoint、
statistics、method、dojo_usage列表（未用为空）。前三个文件路径在提交目录内相对定位；
不需要统计时statistics文件明确写无拟合统计及原因。不需要神经网络权重时checkpoint
可以是实际模型参数或状态文件，不能假造网络。保存完整配置、可复现命令、依赖、
训练/验证日志、参数量、更新数、设备、内存、失败恢复和引用来源。
入口模块提供load(assets: pathlib.Path)->predict。predict接收NumPy FP32
[1,10,6,100,100]原始量，返回有限FP32 [1,40,6,100,100]原始量。
模型常驻；转换、传输、全部模型调用和正反归一化在predict内。禁止缓存预测答案。
计时含统一IPC拷贝，冷启动另报。MPS同步、20次预热；三批，每批45窗口各五次，
按固定随机顺序，取三批P95中位数；禁止以单步或抽点耗时代替完整预测。

本组共round-00及五轮优化，每轮可失败重试、不限制优化训练预算或模型大小。
每轮结束即提交冻结候选并暂停；不要自行进入下一轮。最终仅按本组验证从既有
六份候选选择，不新增第六轮。每轮保存DECISIONS.md：方法、依据、公开资料及实际
采用的库/组件、选择自写的具体原因；保存实现与复现实验命令，不能以文档代替实跑。
另保存audit-replay.json：可独立重放的准备/短训练/验证/恢复/推理命令和所需输入，
用于主控在训练/验证材料上核验执行路径，不允许审计命令访问隐藏数据。

Python运行使用tools/uv run --no-project --no-sync --python environment/bin/python python <脚本或-c参数>。
自行创建environment，并安装installation中的通用材料，不使用宿主环境或editable安装。
通过activity.py显式标记environment_setup/data_preparation/training/evaluation/coding进程，
训练内验证额外保存起止事件，阶段混合如实注明。所有失败、命令、退出码与产物留档。
科学计算前台运行，等待结束，不遗留后台训练或定时作业。本组以外本机资料均不可访问。
"""


def instructions(baseline_provided):
    """无指定网络的说明不复用含模型配方的历史提交正文。"""
    if not baseline_provided:
        return (
            COMMON
            + """
## 自主初始方案
不提供任何参考模型。自行理解任务、搜索资料、选择模型和训练方法。
先写initial-plan.json，登记首个模型、科学依据、训练配方和验证选择规则，再执行。
round-00是该方案首个完整成功训练/提交，不要求满足延迟才冻结；失败可修复但要留证据。
成功后性能改进进入下一轮，不在round-00无限择优。不继承任何未交付的历史配方。
"""
        )
    start = SUBMISSION.index("round-00 另提供")
    end = SUBMISSION.index("每轮保存 validation.json")
    return (
        COMMON
        + "\n## 指定初始配方\n读取baseline/scientific.json与source/model.py，严格保持初始化和科学设置。\n"
        + SUBMISSION[start:end]
    )


def snapshot_framework(root):
    """只复制研究源码/案例/说明，构建与帮助生成均在主控私有快照。"""
    root = Path(root)
    snapshot = root / "framework-snapshot"
    snapshot.mkdir(exist_ok=False)
    ignore = shutil.ignore_patterns(
        "__pycache__", "*.pyc", ".hatch-resources", "dist", "node_modules"
    )
    for relative in (
        "packages/ai4e-spec",
        "packages/ai4e-core",
        "packages/ai4e-contrib",
        "packages/ai4e-task",
        "examples",
        "recipes",
        "docs/agent-help",
        "tools/docs",
        ".agents/skills/dojo-research",
    ):
        shutil.copytree(REPO / relative, snapshot / relative, ignore=ignore)
    for name in ("DOJO_AGENT_GUIDE.md", "pyproject.toml"):
        shutil.copyfile(REPO / name, snapshot / name)
    with (root / "framework-build.log").open("w") as log:
        subprocess.run(
            [sys.executable, str(snapshot / "tools/docs/build_agent_help.py"), "--write"],
            cwd=snapshot,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=True,
        )
        for package in ("spec", "core", "contrib", "task"):
            subprocess.run(
                [
                    "uv",
                    "build",
                    "--wheel",
                    "--no-sources",
                    "--out-dir",
                    str(root / "delivery/dojo-wheels"),
                    "--cache-dir",
                    str(root / "cache/uv"),
                    str(snapshot / f"packages/ai4e-{package}"),
                ],
                cwd=snapshot,
                stdout=log,
                stderr=subprocess.STDOUT,
                check=True,
            )
    resources = root / "delivery/dojo-resources"
    resources.mkdir()
    for wheel in (root / "delivery/dojo-wheels").glob("*.whl"):
        with zipfile.ZipFile(wheel) as archive:
            for name in archive.namelist():
                parts = Path(name).parts
                if name.endswith("/"):
                    continue
                if ".." in parts or name.startswith("/"):
                    raise ValueError("wheel资源越界")
                if name.startswith("ai4e_task/resources/"):
                    target = resources / name.removeprefix("ai4e_task/resources/")
                elif parts[0] in {"ai4e_spec", "ai4e_core", "ai4e_contrib", "ai4e_task"}:
                    target = (
                        resources / "packages" / parts[0].replace("_", "-", 1) / Path(*parts[1:])
                    )
                else:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(name))
    shutil.copytree(root / "delivery/dojo-wheels", resources / "wheels")
    names = inventory(resources)
    if any(
        token in name
        for name in names
        for token in ("recipe_probe", "dojo-compare", "private-split", "preflight")
    ):
        raise ValueError("研究资源混入主控或旧实验材料")
    write_json(root / "evidence/framework-materials.json", names)
    write_json(root / "evidence/framework-source.json", inventory(snapshot))
    return resources


def prepare(root, *, reuse_delivery=None):
    """真实预实验通过后准备四组，初始环境与数据处理仍由研究会话完成。"""
    root = Path(root).resolve()
    if not gate(read_json(root / "preflight/result.json"))["passed"]:
        raise ValueError("真实预实验未通过")
    study = read_json(root / "study.json")["study_id"]
    delivery = root / "delivery"
    delivery.mkdir(exist_ok=False)
    split = read_json(root / "private-split.json")["splits"]
    public = {}
    for partition in ("train", "validation"):
        public[partition] = []
        with tarfile.open(delivery / f"{partition}.tar", "w") as archive:
            for i, sample in enumerate(split[partition]):
                alias = f"{partition}-{i + 1:03d}"
                archive.add(sample["path"], arcname=f"{alias}.h5", recursive=False)
                public[partition].append(
                    {"id": alias, "file": f"{alias}.h5", "sha256": sample["sha256"]}
                )
    if reuse_delivery is None:
        write_json(
            delivery / "dependency-versions.json",
            installed_dependencies(delivery / "public-packages.tar"),
        )
        resources = snapshot_framework(root)
    else:
        prior = Path(reuse_delivery)
        for name in ("public-packages.tar", "dependency-versions.json", "dojo-resources"):
            independent_copy(prior / name, delivery / name)
        resources = delivery / "dojo-resources"
        if inventory(resources) != read_json(prior.parent / "evidence/framework-materials.json"):
            raise ValueError("重开时冻结框架资源不一致")
        write_json(root / "evidence/framework-materials.json", inventory(resources))
        write_json(
            root / "evidence/framework-reused.json",
            {"source": str(prior), "same_frozen_version": True},
        )
    host = tomllib.loads((Path.home() / ".codex/config.toml").read_text())
    runtime = readonly_runtime()
    config = {
        "experiments": {},
        "cells": CELLS,
        "runtime_readonly_roots": runtime,
        "model": host["model"],
        "reasoning": host.get("model_reasoning_effort", "high"),
        "source_root_controller_only": str(REPO),
        "study_id": study,
        "framework_runtime_frozen": True,
        "skill_frozen": True,
        "reused_holdout": True,
    }
    order = np.random.Generator(np.random.PCG64(20260922)).permutation(list(CELLS)).tolist()
    config["round_orders"] = {str(n): order[n % 4 :] + order[: n % 4] for n in range(6)}
    for group, cell in CELLS.items():
        workspace = root.parent.parent / f"{cell['slug']}-{study[:8]}"
        workspace.mkdir(exist_ok=False)
        experiment = workspace / f"experiment-{uuid.uuid4()}"
        for name in (
            "workspace",
            "data",
            "cache",
            "tmp",
            "home",
            "agent-state",
            "evidence",
            "tools",
            "installation",
            "final",
            "results",
            *[f"round-{n:02d}" for n in range(6)],
        ):
            (experiment / name).mkdir(parents=True)
        for partition in public:
            independent_copy(delivery / f"{partition}.tar", experiment / f"data/{partition}.tar")
        write_json(experiment / "data/manifest.json", public)
        for name in ("public-packages.tar", "dependency-versions.json"):
            independent_copy(delivery / name, experiment / "installation" / name)
        (experiment / "installation/README.md").write_text(
            "自行创建environment，再解包public-packages.tar到该环境site-packages；这是同版公开依赖的安装材料，不是已安装环境或准备数据。安装与修复时间计环境。可自行安装其他公开依赖。\n"
        )
        shutil.copyfile(shutil.which("uv"), experiment / "tools/uv")
        (experiment / "tools/uv").chmod(0o755)
        if shutil.which("rg"):
            shutil.copyfile(shutil.which("rg"), experiment / "tools/rg")
            (experiment / "tools/rg").chmod(0o755)
        shutil.copyfile(Path(__file__).parents[1] / "activity.py", experiment / "activity.py")
        (experiment / "SUBMISSION.md").write_text(instructions(cell["baseline_provided"]))
        if cell["baseline_provided"]:
            (experiment / "baseline/source").mkdir(parents=True)
            shutil.copyfile(
                root / "controller-source/dojo_validity/rmhd/model.py",
                experiment / "baseline/source/model.py",
            )
            for src, dest in (
                ("preflight/initial-checkpoint.pt", "initial-checkpoint.pt"),
                ("scientific.json", "scientific.json"),
            ):
                shutil.copyfile(root / src, experiment / "baseline" / dest)
            science = read_json(experiment / "baseline/scientific.json")
            science.update(
                optimizer_betas=[0.9, 0.999],
                optimizer_eps=1e-8,
                optimizer_weight_decay=0,
                optimizer_amsgrad=False,
                gradient_clipping=None,
                drop_last=False,
                checkpoint_epoch=500,
                loss_reduction="all batch/time/field/spatial elements mean; equal eight blocks",
            )
            write_json(experiment / "baseline/scientific.json", science)
        if cell["dojo_available"]:
            independent_copy(resources, experiment / "dojo-resources")
        protocol = {
            "case": "rmhd-factorial-v1",
            "experiment_id": experiment.name,
            "experiment_root": str(experiment),
            "session_workspace_root": str(workspace),
            "baseline_provided": cell["baseline_provided"],
            "dojo_available": cell["dojo_available"],
            "runtime_readonly_roots": runtime,
            "python_executable": str(Path(sys.executable).resolve()),
            "optimization_rounds": 5,
            "fields": ["Psi", "u", "zj", "omega", "rho", "T"],
            "history": 10,
            "future": 40,
            "device": "mps",
            "cpu_threads": 6,
            "evaluation_starts": [0, 80, 161],
            "latency_limit_seconds": 0.05,
        }
        write_json(experiment / "protocol.json", protocol)
        write_json(root / f"evidence/{group}-initial-materials.json", inventory(experiment))
        config["experiments"][group] = str(experiment)
    write_json(root / "comparison-protocol.json", config)
    write_json(
        root / "state.json",
        {"phase": "materials_prepared_isolation_pending", "formal_sessions_started": False},
    )
    return config


def material_audit(root):
    """核验四组起点差异、公共数据一致及无模型组不含指定配方。"""
    root = Path(root)
    config = read_json(root / "comparison-protocol.json")
    for group, location in config["experiments"].items():
        exp = Path(location)
        actual = inventory(exp)
        if actual != read_json(root / f"evidence/{group}-initial-materials.json"):
            raise ValueError(f"初始材料变更:{group}")
        cell = CELLS[group]
        if (exp / "baseline").exists() != cell["baseline_provided"] or (
            exp / "dojo-resources"
        ).exists() != cell["dojo_available"]:
            raise ValueError("材料因素不匹配")
        if not cell["baseline_provided"]:
            text = (exp / "SUBMISSION.md").read_text() + (exp / "protocol.json").read_text()
            if any(t in text.lower() for t in ("u-net", "unet", "500epoch", "2500", "495998")):
                raise ValueError("无模型组收到指定配方")
    paths = {g: Path(p) for g, p in config["experiments"].items()}
    for name in (
        "data/train.tar",
        "data/validation.tar",
        "data/manifest.json",
        "installation/public-packages.tar",
        "activity.py",
    ):
        if len({digest(p / name) for p in paths.values()}) != 1:
            raise ValueError(f"共同材料不一致:{name}")
    for name in (
        "baseline/source/model.py",
        "baseline/initial-checkpoint.pt",
        "baseline/scientific.json",
    ):
        if digest(paths["BP"] / name) != digest(paths["BD"] / name):
            raise ValueError(f"指定起点不同:{name}")
    if inventory(paths["BD"] / "dojo-resources") != inventory(paths["ND"] / "dojo-resources"):
        raise ValueError("Dojo资源版本不同")
    result = {
        "passed": True,
        "cells": list(paths),
        "common_data_equal": True,
        "given_baseline_equal": True,
        "open_model_hint_absent": True,
        "prepared_environment_or_data": False,
    }
    write_json(root / "evidence/material-audit.json", result)
    return result
