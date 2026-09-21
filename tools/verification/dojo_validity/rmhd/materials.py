"""两组最小初始交付：模型与原始分片；安装材料不是已安装环境或训练缓存。"""

import shutil
import subprocess
import sys
import tarfile
import tomllib
import uuid
from pathlib import Path

from ..environment import dependency_closure
from ..io import inventory, read_json, write_json
from .protocol import gate

REPO = Path(__file__).resolve().parents[4]

SUBMISSION = """# 统一提交约定

“自行完成/编写处理和训练流程”指各组实际安装、装配并执行这些工作，不是要求
重新实现已经可用的函数。可以调用本组可获得的已有库、数据处理工具和训练工具；
只是不提前提供本案例已完成的处理代码、统计、张量或训练装配。自行选择复用或自定义。

官方精度主指标为 mean_field_relative_l2。每条轨迹、每个固定窗口、每个字段分别
在完整40帧100x100网格计算 ||prediction-target||2 / ||target||2，再对六字段、
三个窗口、全部轨迹等权平均；FP64复算，越低越好。不把六场拼在一起求范数，
也不以归一化MSE替代主指标。完整场真值零范数、缺样本、错形状或非有限预测
都不能删除后平均，必须报告不可评价。验证反馈遵循同口径；隐藏测试只在最终冻结后由主控评价。

每轮在 round-NN/submission/ 提交自包含候选。submission.json 包含：
interface=rmhd-predict-v1、round(整数)、entrypoint、checkpoint、statistics、method、dojo_usage(列表)。
路径均为提交目录内相对路径；禁止链接、外部路径或依赖可变工作区。
入口模块提供 load(assets: pathlib.Path) -> predict；predict 接受 NumPy FP32
[1,10,6,100,100] 原始物理量，返回有限 FP32 [1,40,6,100,100]。
顺序为时间、字段(Psi,u,zj,omega,rho,T)、R、Z。不提供未来真值。
模型常驻，全部输入处理、模型调用、逆变换均在 predict 内计时。
不得保存或缓存跨请求预测结果、按样本身份查表，或影响计时通信。
主控计时还包含统一 IPC 数组拷贝开销，P95 必须 <=50ms。
保存完整有效配置、依赖清单、训练日志、参数量、更新数、内存、设备、失败记录。
round-00 另提供 baseline-evidence.json，包含 epochs=500、updates=2500、device=mps、
initial_checkpoint_sha256、model_source_sha256、train_ids、validation_ids、mean、std、
sampling_schedule_sha256、每次训练命令和完整日志位置；不得变更 baseline 科学设置。
sampling_schedule_sha256 的算法为：PCG64(42)，每epoch先 integers(0,162,size=70)，
后 permutation(70)；按顺序把这两个数组转成 little-endian int64 字节加入同一个 SHA256，
累计500epoch。先从 manifest 的 train 顺序抽各轨迹起点，再按排列分批；最后一批不丢弃。
每条窗口原始轴 [time,field,R,Z]，前10帧输入、后40帧目标。八次模型调用每次输出5帧，
丢弃历史最早5帧并接上预测的5帧，不能teacher forcing或detach。总损失为全部预测
时空点/字段的归一化MSE（等价八个块MSE平均），一次backward后一次Adam更新。
统计仅在70条完整训练轨迹上计算，FP64总体标准差、ddof=0；不能逐窗口拟合统计。
baseline 使用 epoch500 权重，不能换成验证最优。实际精度不要求与其他运行逐位一致。
每轮保存 validation.json 与方法说明。正式优化只可使用训练和验证数据；禁止重下载
隐藏轨迹及网络副本来开发。所有新数据下载记来源和用途，不允许跨组访问。
第五轮后 final/selection.json 仅指定 round=0..5 与 validation_reason，不得新增改进。
"""


def installed_dependencies(destination):
    """冻结当前公开科学依赖为通用安装包；组内仍须自行建立环境并安装。"""
    requirements = ["torch", "numpy", "h5py", "scipy", "matplotlib", "PyYAML", "packaging"]
    for name in ("core", "contrib", "task"):
        project = tomllib.loads((REPO / f"packages/ai4e-{name}/pyproject.toml").read_text())
        requirements += [r for r in project["project"]["dependencies"] if not r.startswith("ai4e-")]
    distributions = dependency_closure(requirements)
    seen, versions = set(), {}
    with tarfile.open(destination, "w") as archive:
        for name, distribution in sorted(distributions.items()):
            versions[name] = distribution.version
            for relative in distribution.files or []:
                path = Path(relative)
                if path.is_absolute() or ".." in path.parts or "__pycache__" in path.parts:
                    continue
                if path.suffix == ".pth":
                    if path.name == "distutils-precedence.pth":
                        continue
                    raise ValueError(f"安装材料含隐式外部加载器: {path}")
                source = Path(distribution.locate_file(relative))
                if not source.is_file() or path.as_posix() in seen:
                    continue
                archive.add(source, arcname=path.as_posix(), recursive=False)
                seen.add(path.as_posix())
    return versions


def prepare_groups(comparison):
    """科学门槛通过后才物化两个独立组根；不创建正式会话、不预装组环境。"""
    root = Path(comparison).resolve()
    result = read_json(root / "preflight/result.json")
    if not gate(result)["passed"] or read_json(root / "state.json")["phase"] != "science_passed":
        raise ValueError("真实预实验未通过，不得准备正式组")
    base = root.parent.parent
    groups = {g: base / f"jorek-rmhd-{g}" for g in ("plain", "dojo")}
    for path in groups.values():
        if path.exists() and any(path.iterdir()):
            raise FileExistsError(f"组级工作根非空: {path}")
    split = read_json(root / "private-split.json")["splits"]
    delivery = root / "delivery"
    delivery.mkdir(exist_ok=False)
    public = {}
    for partition in ("train", "validation"):
        public[partition] = []
        with tarfile.open(delivery / f"{partition}.tar", "w") as archive:
            for i, sample in enumerate(split[partition]):
                alias = f"{partition}-{i + 1:03d}"
                archive.add(sample["path"], arcname=f"{alias}.h5", recursive=False)
                original = Path(sample["path"])
                input_file = original.with_name(
                    original.name.replace("jorek_run", "jorek_input_run")
                ).with_suffix(".txt")
                archive.add(input_file, arcname=f"{alias}.txt", recursive=False)
                public[partition].append(
                    {"id": alias, "file": f"{alias}.h5", "sha256": sample["sha256"]}
                )
    versions = installed_dependencies(delivery / "public-packages.tar")
    write_json(delivery / "dependency-versions.json", versions)
    wheels = delivery / "dojo-wheels"
    for package in ("spec", "core", "contrib", "task"):
        subprocess.run(
            [
                "uv",
                "build",
                "--wheel",
                "--no-sources",
                "--out-dir",
                str(wheels),
                "--cache-dir",
                str(root / "cache/uv"),
                str(REPO / f"packages/ai4e-{package}"),
            ],
            check=True,
        )
    host = tomllib.loads((Path.home() / ".codex/config.toml").read_text())
    experiments = {}
    for group, workspace in groups.items():
        workspace.mkdir(exist_ok=True)
        experiment = workspace / f"experiment-{uuid.uuid4()}"
        for name in (
            "baseline/source",
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
            *[f"round-{i:02d}" for i in range(6)],
        ):
            (experiment / name).mkdir(parents=True)
        for partition in public:
            shutil.copyfile(delivery / f"{partition}.tar", experiment / "data" / f"{partition}.tar")
        shutil.copyfile(
            Path(__file__).with_name("model.py"), experiment / "baseline/source/model.py"
        )
        shutil.copyfile(
            root / "preflight/initial-checkpoint.pt", experiment / "baseline/initial-checkpoint.pt"
        )
        shutil.copyfile(root / "scientific.json", experiment / "baseline/scientific.json")
        write_json(experiment / "data/manifest.json", public)
        for name in ("public-packages.tar", "dependency-versions.json"):
            shutil.copyfile(delivery / name, experiment / "installation" / name)
        shutil.copyfile(shutil.which("uv"), experiment / "tools/uv")
        (experiment / "tools/uv").chmod(0o755)
        # 仅活动证据工具，无数据加载/训练逻辑；可信计时另在父进程记录。
        shutil.copyfile(Path(__file__).parents[1] / "activity.py", experiment / "activity.py")
        (experiment / "SUBMISSION.md").write_text(SUBMISSION)
        (experiment / "installation/README.md").write_text(
            "public-packages.tar 是同版本公共科学包的 site-packages 文件副本，非已安装环境。"
            "请自行创建独立 environment，安装或解包这些通用依赖，再检验版本；"
            "安装和修复时间计入本组。不能引用宿主环境或使用 editable 安装。\n"
        )
        protocol = {
            "case": "jorek-rmhd-v1",
            "group": group,
            "experiment_id": experiment.name,
            "session_workspace_root": str(workspace),
            "experiment_root": str(experiment),
            "model": host["model"],
            "reasoning": host.get("model_reasoning_effort", "high"),
            "runtime_readonly_roots": [str(Path(sys.base_prefix).resolve())],
            "python_executable": str(Path(sys.executable).resolve()),
            "rounds": 5,
        }
        write_json(experiment / "protocol.json", protocol)
        if group == "dojo":
            resources = experiment / "dojo-resources"
            resources.mkdir()
            shutil.copyfile(REPO / "DOJO_AGENT_GUIDE.md", resources / "DOJO_AGENT_GUIDE.md")
            for relative in (".agents/skills/dojo-research", "docs/agent-help", "examples"):
                shutil.copytree(
                    REPO / relative,
                    resources / relative,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            shutil.copytree(wheels, resources / "wheels")
            for package in ("spec", "core", "contrib", "task"):
                shutil.copytree(
                    REPO / f"packages/ai4e-{package}",
                    resources / f"packages/ai4e-{package}",
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "dist"),
                )
            write_json(root / "evidence/dojo-materials.json", inventory(resources))
        write_json(root / f"evidence/{group}-initial-materials.json", inventory(experiment))
        experiments[group] = str(experiment)
    write_json(
        root / "comparison-protocol.json",
        {
            "experiments": experiments,
            "runtime_readonly_roots": [str(Path(sys.base_prefix).resolve())],
            "model": host["model"],
            "reasoning": host.get("model_reasoning_effort", "high"),
            "source_root_controller_only": str(REPO),
        },
    )
    write_json(
        root / "state.json",
        {"phase": "materials_prepared_isolation_pending", "formal_sessions_started": False},
    )
    return experiments
