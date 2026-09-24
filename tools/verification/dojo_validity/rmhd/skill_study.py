"""单组、逐轮人工审查 Skill 的研究执行器；隐藏评价与研究会话严格分离。"""

import argparse
import shutil
import subprocess
import sys
import tarfile
import time
import uuid
from pathlib import Path

from ..io import digest, inventory, read_json, write_json
from .controller import freeze_environment, freeze_round, lock_final, verify_frozen
from .evaluate import evaluate_candidate
from .isolation import probe
from .materials import REPO, SUBMISSION
from .network import PublicProxy
from .protocol import gate
from .sessions import CliDriver, prompt

SKILL = Path(".agents/skills/dojo-research/SKILL.md")
OPPORTUNITIES = (
    "source_and_fields",
    "validation_and_identity",
    "statistics",
    "normalization",
    "sampling_and_batches",
    "model",
    "objective",
    "training_loop",
    "run_records",
    "checkpoint_and_resume",
    "inference",
    "evaluation",
    "postprocessing",
)


def prepare(source, base):
    """复用冻结原始分包和科学起点，绝不向研究会话交付旧处理代码或结论。"""
    source, base = Path(source).resolve(), Path(base).resolve()
    if not gate(read_json(source / "preflight/result.json"))["passed"]:
        raise ValueError("原真实预实验未通过")
    identity = str(uuid.uuid4())
    root = base / "jorek-rmhd-skill-study" / f"study-{identity}"
    workspace = base / f"jorek-rmhd-skill-dojo-{identity}"
    experiment = workspace / f"experiment-{uuid.uuid4()}"
    root.mkdir(parents=True, exist_ok=False)
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
        *[f"round-{n:02d}" for n in range(6)],
    ):
        (experiment / name).mkdir(parents=True)
    for name in (
        "private-split.json",
        "scientific.json",
        "preflight/statistics.json",
        "preflight/initial-checkpoint.pt",
        "preflight/result.json",
    ):
        destination = root / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source / name, destination)
    public = {}
    splits = read_json(root / "private-split.json")["splits"]
    for partition in ("train", "validation"):
        shutil.copyfile(source / f"delivery/{partition}.tar", experiment / f"data/{partition}.tar")
        public[partition] = [
            {
                "id": f"{partition}-{i + 1:03d}",
                "file": f"{partition}-{i + 1:03d}.h5",
                "sha256": row["sha256"],
            }
            for i, row in enumerate(splits[partition])
        ]
    write_json(experiment / "data/manifest.json", public)
    shutil.copyfile(Path(__file__).with_name("model.py"), experiment / "baseline/source/model.py")
    shutil.copyfile(
        root / "preflight/initial-checkpoint.pt", experiment / "baseline/initial-checkpoint.pt"
    )
    shutil.copyfile(root / "scientific.json", experiment / "baseline/scientific.json")
    for name in ("public-packages.tar", "dependency-versions.json"):
        shutil.copyfile(source / "delivery" / name, experiment / "installation" / name)
    shutil.copyfile(shutil.which("uv"), experiment / "tools/uv")
    (experiment / "tools/uv").chmod(0o755)
    shutil.copyfile(Path(__file__).parents[1] / "activity.py", experiment / "activity.py")
    (experiment / "SUBMISSION.md").write_text(
        SUBMISSION
        + "\n每轮另保存 DECISIONS.md：各实现决策的 Dojo 引用、Web 来源、选择及理由。训练内部的验证区间也需单独记录，不全部归入训练。\n"
    )
    (experiment / "installation/README.md").write_text(
        "public-packages.tar 是通用 site-packages 安装材料，自行创建 environment 并解包安装；不是已准备数据或环境。Dojo wheels 另行安装，不使用 editable。\n"
    )
    old = read_json(source / "comparison-protocol.json")
    runtime = [str(Path(sys.base_prefix).resolve())]
    config = {
        "experiments": {"dojo": str(experiment)},
        "workspace_root": str(workspace),
        "runtime_readonly_roots": runtime,
        "model": old["model"],
        "reasoning": old["reasoning"],
        "source_root_controller_only": str(REPO),
        "previous_study_controller_only": str(source),
        "study_kind": "single_group_adaptive_skill",
        "opportunities": list(OPPORTUNITIES),
        "reused_holdout": True,
        "framework_runtime_frozen": True,
    }
    write_json(root / "comparison-protocol.json", config)
    protocol = {
        "case": "jorek-rmhd-v1",
        "group": "dojo",
        "experiment_id": experiment.name,
        "session_workspace_root": str(workspace),
        "experiment_root": str(experiment),
        "model": config["model"],
        "reasoning": config["reasoning"],
        "rounds": 5,
        "runtime_readonly_roots": runtime,
        "python_executable": str(Path(sys.executable).resolve()),
    }
    write_json(experiment / "protocol.json", protocol)
    resources = experiment / "dojo-resources"
    resources.mkdir()
    shutil.copyfile(REPO / "DOJO_AGENT_GUIDE.md", resources / "DOJO_AGENT_GUIDE.md")
    for relative in (".agents/skills/dojo-research", "docs/agent-help", "examples"):
        shutil.copytree(
            REPO / relative,
            resources / relative,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    for package in ("spec", "core", "contrib", "task"):
        subprocess.run(
            [
                "uv",
                "build",
                "--wheel",
                "--no-sources",
                "--out-dir",
                str(resources / "wheels"),
                "--cache-dir",
                str(root / "cache/uv"),
                str(REPO / f"packages/ai4e-{package}"),
            ],
            check=True,
        )
        shutil.copytree(
            REPO / f"packages/ai4e-{package}",
            resources / f"packages/ai4e-{package}",
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "dist"),
        )
    write_json(root / "evidence/dojo-initial-materials.json", inventory(experiment))
    write_json(root / "evidence/dojo-materials.json", inventory(resources))
    write_json(
        root / "state.json",
        {"phase": "materials_prepared_isolation_pending", "formal_sessions_started": False},
    )
    print(root, flush=True)
    return root


class StudyDriver(CliDriver):
    """路径和权限只取自主控；每轮必须经过主会话审查与版本交付。"""

    def trusted_protocol(self, group, location):
        config = read_json(self.root / "comparison-protocol.json")
        experiment = Path(config["experiments"]["dojo"])
        workspace = Path(config["workspace_root"])
        if group != "dojo" or Path(location) != experiment or experiment.parent != workspace:
            raise ValueError("单组工作根不符")
        if experiment.resolve() != experiment or workspace.resolve() != workspace:
            raise ValueError("工作根不能经链接解析")
        checksum = read_json(self.root / "evidence/dojo-initial-materials.json")["protocol.json"]
        if digest(experiment / "protocol.json") != checksum:
            raise ValueError("协议被改写")
        return read_json(experiment / "protocol.json") | {
            "runtime_readonly_roots": config["runtime_readonly_roots"],
            "model": config["model"],
            "reasoning": config["reasoning"],
            "experiment_root": str(experiment),
            "session_workspace_root": str(workspace),
        }


def deliver(root, number, rationale):
    """只在两个研究轮次之间交付 Skill，不变更框架代码、Guide、科学设置或旧收据。"""
    root = Path(root)
    if (root / "active-round.json").exists():
        raise ValueError("研究轮正在执行，不能替换 Skill")
    if read_json(root / "state.json")["phase"] not in {"ready", "running"}:
        raise ValueError("当前阶段不能交付 Skill")
    if type(number) is not int or number not in range(6):
        raise ValueError("轮次非法")
    config = read_json(root / "comparison-protocol.json")
    if number:
        verify_frozen(root, "dojo", number - 1)
        review = read_json(root / f"reviews/round-{number - 1:02d}.json")
        if set(review["opportunities"]) != set(OPPORTUNITIES) or not review.get("evidence"):
            raise ValueError("主会话能力机会与证据审查不完整")
    receipt = root / f"skill-revisions/round-{number:02d}.json"
    if receipt.exists():
        raise FileExistsError("不能覆盖已交付 Skill 版本")
    experiment = Path(config["experiments"]["dojo"])
    source = REPO / SKILL
    frozen = root / f"skill-revisions/round-{number:02d}.md"
    frozen.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, frozen)
    targets = [experiment / "dojo-resources" / SKILL]
    # 导出入口、源码资源和安装资源都指向同一轮文本；wheel保持初始身份。
    targets += list(
        (experiment / "environment/lib").glob(
            "python*/site-packages/ai4e_task/resources/.agents/skills/dojo-research/SKILL.md"
        )
    )
    for target in targets:
        shutil.copyfile(source, target)
    write_json(
        receipt,
        {
            "round": number,
            "sha256": digest(frozen),
            "rationale": rationale,
            "delivered": [str(p.relative_to(experiment)) for p in targets],
            "framework_changed": False,
            "time": time.time(),
        },
    )
    return receipt


def precheck(root):
    """当前新工作根真实探测；诊断环境移除后研究 Agent 自行安装。"""
    root = Path(root)
    config = read_json(root / "comparison-protocol.json")
    experiment = Path(config["experiments"]["dojo"])
    protocol = StudyDriver(root).trusted_protocol("dojo", experiment)
    temporary = experiment.parent / ".mps-precheck-runtime"
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
    previous = Path(config["previous_study_controller_only"])
    forbidden = [
        root,
        REPO,
        previous,
        previous.parent.parent / "jorek-rmhd-plain",
        previous.parent.parent / "jorek-rmhd-dojo",
        Path(read_json(root / "private-split.json")["splits"]["test"][0]["path"]).parent,
    ]
    try:
        with PublicProxy(root / "evidence/probe-network.jsonl") as proxy:
            result = probe(
                experiment.parent,
                config["runtime_readonly_roots"],
                forbidden,
                root / "evidence/dojo-isolation.json",
                python=temporary / "bin/python",
                proxy_port=proxy.port,
            )
    finally:
        shutil.rmtree(temporary)
    if not result["passed"]:
        raise ValueError("新根隔离预检失败")
    write_json(root / "state.json", {"phase": "ready", "formal_sessions_started": False})
    return result


def run_round(root, number):
    """仅执行指定轮，等待主会话分析再继续，隐藏评分没有调用路径。"""
    root = Path(root)
    state = read_json(root / "state.json")
    if state["phase"] not in {"ready", "running"}:
        raise ValueError("未通过隔离门槛或已最终冻结")
    if number not in range(6) or (root / f"receipts/dojo/round-{number:02d}.json").exists():
        raise ValueError("轮次非法或已冻结")
    active = root / "active-round.json"
    if active.exists() and read_json(active)["round"] != number:
        raise ValueError("另一轮尚未完成")
    driver = StudyDriver(root)
    config = read_json(root / "comparison-protocol.json")
    location = config["experiments"]["dojo"]
    protocol = driver.trusted_protocol("dojo", location)
    revision = read_json(root / f"skill-revisions/round-{number:02d}.json")
    if digest(Path(location) / "dojo-resources" / SKILL) != revision["sha256"]:
        raise ValueError("Skill 与本轮交付不符")
    if number:
        verify_frozen(root, "dojo", number - 1)
        read_json(root / f"reviews/round-{number - 1:02d}.json")
    else:
        if not read_json(root / "evidence/dojo-isolation.json")["passed"]:
            raise ValueError("隔离失败")
        for name, checksum in read_json(root / "evidence/dojo-initial-materials.json").items():
            if digest(Path(location) / name) != checksum:
                raise ValueError(f"初始材料变化: {name}")
    message = prompt(protocol, number).replace(
        "你必须自行编写原始数据读取、校验、统计、窗口构造、训练和评价流程",
        "你必须自行装配并执行原始数据读取、校验、统计、窗口构造、训练和评价流程；可以复用已有库，不要求重新实现已有工具",
    )
    message += f"\n本轮先阅读 dojo-resources/{SKILL.as_posix()}（SHA256 {revision['sha256']}），按该 Skill 做实现决策：每次实质编写同时参考 Dojo 能力和 Web 资料，综合判断；不是必须采用 Dojo。新训练先评估框架职责，适配缺口可自写。记录 DECISIONS.md 和可核验调用、产物，不能把导入或阅读算作实际采用。各阶段独立计时，训练内部验证用活动工具或原始起止事件单列。公开网络可用，禁止取得隐藏轨迹或历史实验结果。"
    write_json(root / "state.json", {"phase": "running", "formal_sessions_started": True})
    write_json(active, {"round": number, "skill_sha256": revision["sha256"]})
    while True:
        driver.call("dojo", location, f"round-{number:02d}", message)
        try:
            source = driver.check_round("dojo", number, location, protocol)
            break
        except (ValueError, FileNotFoundError, KeyError) as error:
            message = f"本轮 round-{number:02d} 协议/开发验证未通过：{error}。在同轮修复并保留成本，先按本轮 Skill 参考 Dojo 和 Web；不改 baseline 科学设置，不访问隐藏数据。"
    receipt = freeze_round(root, "dojo", number, source)
    active.unlink()
    return receipt


def select(root):
    """五轮冻结且审查后锁定最终选择，无额外研究轮次。"""
    root = Path(root)
    if (
        read_json(root / "state.json")["phase"] != "running"
        or (root / "active-round.json").exists()
    ):
        raise ValueError("研究尚未结束或选择已锁定")
    for number in range(6):
        verify_frozen(root, "dojo", number)
        read_json(root / f"reviews/round-{number:02d}.json")
    config = read_json(root / "comparison-protocol.json")
    chosen = StudyDriver(root).select_final("dojo", config["experiments"]["dojo"])
    lock_final(root, "dojo", chosen)
    freeze_environment(
        Path(config["experiments"]["dojo"]) / "environment",
        root / "frozen-environments/dojo",
        config["runtime_readonly_roots"],
    )
    write_json(
        root / "state.json", {"phase": "single_final_locked", "formal_sessions_started": True}
    )


def hidden(root):
    """单组最终锁定后才可评分，结果永不返回实验目录。"""
    root = Path(root)
    if read_json(root / "state.json")["phase"] not in {
        "single_final_locked",
        "single_hidden_evaluating",
    }:
        raise ValueError("单组最终冻结前禁止隐藏评价")
    selected = read_json(root / "final-selections/dojo.json")
    if (
        digest(root / f"receipts/dojo/round-{selected['round']:02d}.json")
        != selected["receipt_sha256"]
    ):
        raise ValueError("选择收据变化")
    config = read_json(root / "comparison-protocol.json")
    samples = read_json(root / "private-split.json")["splits"]["test"]
    for sample in samples:
        if digest(sample["path"]) != sample["sha256"]:
            raise ValueError("隐藏来源变化")
    write_json(
        root / "state.json", {"phase": "single_hidden_evaluating", "formal_sessions_started": True}
    )
    for number in range(6):
        candidate = verify_frozen(root, "dojo", number)
        output = root / f"hidden-results/dojo/round-{number:02d}"
        if (output / "result.json").exists():
            continue
        result = evaluate_candidate(
            candidate,
            root / "frozen-environments/dojo",
            config["runtime_readonly_roots"],
            samples,
            output,
        )
        write_json(output / "result.json", result)
    write_json(
        root / "state.json",
        {"phase": "single_hidden_evaluated_review_pending", "formal_sessions_started": True},
    )


def main():
    """命令行每次只推进一个显式阶段；不后台自动跳过人工观察。"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "action", choices=["prepare", "probe", "deliver", "round", "select", "hidden"]
    )
    parser.add_argument("--root", type=Path)
    parser.add_argument("--source", type=Path)
    parser.add_argument("--base", type=Path)
    parser.add_argument("--number", type=int)
    parser.add_argument("--rationale", default="初始训练框架优先评估与双来源决策")
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.source, args.base)
    elif args.action == "probe":
        print(precheck(args.root)["passed"])
    elif args.action == "deliver":
        print(deliver(args.root, args.number, args.rationale))
    elif args.action == "round":
        print(run_round(args.root, args.number)["round"])
    elif args.action == "select":
        select(args.root)
    else:
        hidden(args.root)


if __name__ == "__main__":
    main()
