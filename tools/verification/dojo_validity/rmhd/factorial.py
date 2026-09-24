"""四会话主控：独立材料、可信权限、六轮冻结和全体最终锁后的隐藏评价。"""

import argparse
import json
import shutil
import subprocess
import sys
import tarfile
import time
import uuid
from pathlib import Path

from ..io import digest, inside, inventory, read_json, write_json
from .controller import freeze_environment, immutable_copy
from .evaluate import evaluate_candidate
from .factorial_materials import CELLS, material_audit, prepare
from .isolation import clean_environment, execute, policy, probe
from .network import PublicProxy
from .sessions import CliDriver
from .verification import verify_round_zero


def prompt(protocol, number):
    """每条任务只包含本组材料；无指定模型不透露另一因素配方。"""
    text = f"""你是独立研究会话。工作根{protocol["session_workspace_root"]}，
本次工作和全部产物放在{protocol["experiment_root"]}。只访问自己的工作根和
protocol登记的只读系统运行时，不读其他本机资料/服务。先读SUBMISSION.md、
protocol.json、data/manifest.json。这里所有相对路径均相对于experiment目录，命令的工作目录设为该目录；会话根仍保持组级目录。原始数据与通用安装材料尚未处理，请自行创建
environment、处理数据并实际研究。系统解释器是{protocol["python_executable"]}，
工具是tools/uv；科学运行按SUBMISSION经activity.py留档。主要目标是满足完整预测
P95<=50ms后尽可能降低验证误差，分别记录编码时间与token，不把复用比例当优化目标。
当前round-{number:02d}。完成本轮实跑并提交round-{number:02d}/submission后暂停，
不得自行进入下一轮，不得留下后台训练。搜索、失败、重试和决策均保留证据。"""
    if protocol["dojo_available"]:
        text += "\n先阅读dojo-resources/.agents/skills/dojo-research/SKILL.md，按其工作流开展本轮；GUIDE说明能力，帮助中心给当前签名。自行选择最近案例和工具，记录实际采用与自定义原因，不设采用率目标。框架、Skill与帮助为冻结版本，安装包在dojo-resources/wheels。"
    if number == 0:
        if protocol["baseline_provided"]:
            text += "\n读取baseline/，严格按交付网络、初始化与完整科学配方完成round-00，保存baseline-evidence.json，不以短训或验证最优替代规定末轮。"
        else:
            text += "\n不提供参考模型。自行理解、上网搜索并选择初始模型，先写initial-plan.json登记配方及选择规则，再完成首次训练和提交。成功初始方案即冻结，之后改进进入下一轮；首轮超延迟仍可提交并标明。"
    else:
        text += "\n基于本组已冻结结果完成一次实质优化。模型、训练预算和尝试次数自由，只使用训练与验证；不要改变已冻结历史提交。保存本轮方法、全部尝试及复现命令。"
    return text


def validate_cell_config(config):
    """主控四根互不包含，实验是其直接子目录；不接受组内授权扩大。"""
    if set(config["experiments"]) != set(CELLS):
        raise ValueError("四单元登记不完整")
    roots = []
    for name, location in config["experiments"].items():
        path = Path(location)
        if not path.name.startswith("experiment-") or path.resolve() != path:
            raise ValueError("实验必须为规范绝对路径下的独立ID")
        root = path.parent
        if not root.name.startswith(CELLS[name]["slug"] + "-"):
            raise ValueError("会话根不是登记的组级根")
        if any(root.is_relative_to(other) or other.is_relative_to(root) for other in roots):
            raise ValueError("会话工作根相互包含")
        roots.append(root)


def verify_frozen(root, group, number):
    """核候选与每轮环境，不信任可写组目录。"""
    root = Path(root)
    if group not in CELLS or type(number) is not int or number not in range(6):
        raise ValueError("组/轮次非法")
    receipt = read_json(root / f"receipts/{group}/round-{number:02d}.json")
    source = root / f"frozen/{group}/round-{number:02d}"
    if inventory(source) != receipt["files"]:
        raise ValueError("冻结提交变更")
    return source


def freeze(root, group, number, source):
    """候选与运行依赖逐轮冻结，后续环境变化不改变历史候选。"""
    root, source = Path(root), Path(source)
    if read_json(root / "state.json")["phase"] != "running":
        raise ValueError("当前阶段不可冻结")
    if group not in CELLS or type(number) is not int or number not in range(6):
        raise ValueError("非法单元或轮次")
    if number and not (root / f"receipts/{group}/round-{number - 1:02d}.json").exists():
        raise ValueError("前轮未冻结")
    manifest = read_json(source / "submission.json")
    if manifest.get("interface") != "rmhd-predict-v1" or manifest.get("round") != number:
        raise ValueError("提交接口或轮次错误")
    for key in ("entrypoint", "checkpoint", "statistics"):
        if not inside(source, manifest[key]).is_file():
            raise ValueError(f"缺少{key}")
    if not manifest.get("method") or not isinstance(manifest.get("dojo_usage"), list):
        raise ValueError("缺少方法/组件记录")
    config = read_json(root / "comparison-protocol.json")
    environment = root / f"frozen-environments/{group}/round-{number:02d}"
    environment.parent.mkdir(parents=True, exist_ok=True)
    env_files = freeze_environment(
        Path(config["experiments"][group]) / "environment",
        environment,
        config["runtime_readonly_roots"],
    )
    write_json(root / f"environment-receipts/{group}/round-{number:02d}.json", env_files)
    files = immutable_copy(source, root / f"frozen/{group}/round-{number:02d}")
    receipt = {
        "group": group,
        "round": number,
        "files": files,
        "source_manifest": manifest,
        "environment_receipt_sha256": digest(
            root / f"environment-receipts/{group}/round-{number:02d}.json"
        ),
        "frozen_at": time.time(),
    }
    write_json(root / f"receipts/{group}/round-{number:02d}.json", receipt)
    exp = Path(config["experiments"][group])
    for folder in (exp / "workspace", exp / f"round-{number:02d}"):
        for file in folder.rglob("*"):
            if (
                file.is_file()
                and not file.is_symlink()
                and file.suffix in {".py", ".json", ".yaml", ".yml", ".toml", ".sh", ".md"}
            ):
                destination = (
                    root / f"research-source/{group}/round-{number:02d}" / file.relative_to(exp)
                )
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(file, destination)
    return receipt


def lock(root, group, selection):
    """全体六候选检查后锁定最终选择；选择一旦保存不可覆盖。"""
    root = Path(root)
    if read_json(root / "state.json")["phase"] != "running":
        raise ValueError("不能修改最终选择")
    if (
        group not in CELLS
        or type(selection.get("round")) is not int
        or selection["round"] not in range(6)
    ):
        raise ValueError("最终候选非法")
    for n in range(6):
        verify_frozen(root, group, n)
    target = root / f"final-selections/{group}.json"
    if target.exists():
        raise ValueError("最终选择不可覆盖")
    write_json(
        target,
        selection
        | {
            "receipt_sha256": digest(root / f"receipts/{group}/round-{selection['round']:02d}.json")
        },
    )
    if all((root / f"final-selections/{g}.json").exists() for g in CELLS):
        write_json(
            root / "state.json", {"phase": "all_finals_locked", "formal_sessions_started": True}
        )


class Driver(CliDriver):
    """每个独立单元一个CLI会话；复用原始事件采集，不复用旧组语义。"""

    def trusted_protocol(self, group, location):
        config = read_json(self.root / "comparison-protocol.json")
        validate_cell_config(config)
        if group not in CELLS or str(location) != config["experiments"][group]:
            raise ValueError("组地址未登记")
        experiment = Path(location)
        frozen = read_json(self.root / f"evidence/{group}-initial-materials.json")
        for name in ("protocol.json", "SUBMISSION.md", "activity.py"):
            if digest(inside(experiment, name)) != frozen[name]:
                raise ValueError(f"初始协议已修改:{name}")
        if CELLS[group]["dojo_available"]:
            expected = read_json(self.root / "evidence/framework-materials.json")
            for name in (
                ".agents/skills/dojo-research/SKILL.md",
                "DOJO_AGENT_GUIDE.md",
                "docs/agent-help/manifest.json",
            ):
                if digest(inside(experiment / "dojo-resources", name)) != expected[name]:
                    raise ValueError("冻结研究入口已改变")
        protocol = read_json(experiment / "protocol.json")
        protocol.update(
            model=config["model"],
            reasoning=config["reasoning"],
            runtime_readonly_roots=config["runtime_readonly_roots"],
            experiment_root=str(experiment),
            session_workspace_root=str(experiment.parent),
            **{k: CELLS[group][k] for k in ("baseline_provided", "dojo_available")},
        )
        return protocol

    def select_final(self, group, location):
        """最终选择只按验证门槛与精度，不允许生成新候选。"""
        self.call(
            group,
            location,
            "final-selection",
            "五轮已完成。只从round-00..05冻结候选中选择：先筛验证P95<=50ms的候选，"
            "再按验证主指标最低选最终轮；若没有合格候选仍选择并明确不合格。"
            "写final/selection.json，字段round、validation_reason。不新增训练/优化，不改候选，"
            "不使用隐藏数据。所有路径相对本组experiment目录。",
        )
        return read_json(Path(location) / "final/selection.json")

    def round(self, group, number, location):
        protocol = self.trusted_protocol(group, location)
        message = prompt(protocol, number)
        while True:
            self.call(group, location, f"round-{number:02d}", message)
            try:
                if number == 0 and protocol["baseline_provided"]:
                    verify_round_zero(self.root, group, Path(location) / "round-00/submission")
                if (
                    number == 0
                    and not protocol["baseline_provided"]
                    and not (Path(location) / "initial-plan.json").is_file()
                ):
                    raise ValueError("缺首个模型训练前登记的initial-plan.json")
                # 母类仅check_round中的round00特殊检查需绕开，评价由下方统一执行。
                source = Path(location) / f"round-{number:02d}/submission"
                manifest = read_json(source / "submission.json")
                if manifest.get("round") != number:
                    raise ValueError("提交轮次错误")
                split = read_json(self.root / "private-split.json")["splits"]["validation"]
                aliases = read_json(Path(location) / "data/manifest.json")["validation"]
                samples = [s | {"id": a["id"]} for s, a in zip(split, aliases, strict=True)]
                output = self.root / f"validation/{group}/round-{number:02d}" / str(uuid.uuid4())
                result = evaluate_candidate(
                    source,
                    Path(location) / "environment",
                    protocol["runtime_readonly_roots"],
                    samples,
                    output,
                    latency_seed=42,
                )
                write_json(output / "result.json", result)
                # 反馈只含本组验证科学数据，不泄露主控文件路径、环境或异常内部信息。
                feedback = {
                    k: result[k]
                    for k in (
                        "status",
                        "eligible",
                        "latency_p95_seconds",
                        "accuracy",
                        "persistence",
                        "latency_limit_seconds",
                    )
                    if k in result
                }
                write_json(Path(location) / f"round-{number:02d}/validation.json", feedback)
                if result["status"] != "evaluated":
                    raise ValueError("开发验证预测接口执行失败，检查本组相同接口及输出形状/有限性")
                return source
            except (ValueError, FileNotFoundError, KeyError) as error:
                message = f"本轮提交未通过协议核查：{error}。继续同一round-{number:02d}修复并实际验证，不进入下一轮；保留失败记录。只用本组训练/验证，不改变round-00的已给定配方（如有）。"


def probe_all(root):
    """实际探测每组与其他三组、主控和数据源的边界。"""
    root = Path(root)
    material_audit(root)
    cfg = read_json(root / "comparison-protocol.json")
    validate_cell_config(cfg)
    results = {}
    for group, location in cfg["experiments"].items():
        exp = Path(location)
        workspace = exp.parent
        temporary = workspace / ".mps-precheck-runtime"
        protocol = read_json(exp / "protocol.json")
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
            temporary / f"lib/python{sys.version_info.major}.{sys.version_info.minor}/site-packages"
        )
        with tarfile.open(exp / "installation/public-packages.tar") as archive:
            archive.extractall(site, filter="data")
        try:
            forbidden = [Path(p).parent for g, p in cfg["experiments"].items() if g != group]
            forbidden += [
                root,
                Path(cfg["source_root_controller_only"]),
                Path(read_json(root / "private-split.json")["splits"]["test"][0]["path"]),
            ]
            with PublicProxy(root / f"evidence/{group}-probe-network.jsonl") as proxy:
                results[group] = probe(
                    workspace,
                    cfg["runtime_readonly_roots"],
                    forbidden,
                    root / f"evidence/{group}-isolation.json",
                    python=temporary / "bin/python",
                    proxy_port=proxy.port,
                )
                readonly = root / f"readonly-probe-{group}"
                readonly.mkdir(exist_ok=True)
                sentinel = readonly / "sentinel"
                sentinel.write_text("readonly")
                script = """import json,pathlib
p=pathlib.Path(__import__('sys').argv[1]); checks={'read':p.read_text()=='readonly'}
for name,action in [('write',lambda:p.write_text('bad')),('create',lambda:(p.parent/'new').touch()),('delete',p.unlink)]:
    try:action()
    except PermissionError:checks[name]=True
    else:checks[name]=False
print(json.dumps(checks));assert all(checks.values())
"""
                test = execute(
                    policy(
                        [workspace],
                        [*cfg["runtime_readonly_roots"], readonly],
                        proxy_port=proxy.port,
                    ),
                    [protocol["python_executable"], "-c", script, str(sentinel)],
                    workspace,
                    clean_environment(exp),
                )
                write_json(
                    root / f"evidence/{group}-readonly-probe.json",
                    {
                        "script": script,
                        "returncode": test.returncode,
                        "stdout": test.stdout,
                        "stderr": test.stderr,
                        "diagnostic_only_allowance": str(readonly),
                    },
                )
                if test.returncode != 0 or sentinel.read_text() != "readonly":
                    raise ValueError("只读前提探针未通过")
        finally:
            shutil.rmtree(temporary)
    if not all(r["passed"] and r["mps_probed"] for r in results.values()):
        raise ValueError("至少一组隔离或MPS预检失败")
    write_json(root / "evidence/isolation-all.json", {"passed": True, "groups": list(results)})
    return results


def run(root, driver=None):
    """只调度研究，不接收隐藏评价回调；所有组结束后另调用隐藏入口。"""
    root = Path(root)
    driver = driver or Driver(root)
    state = read_json(root / "state.json")
    if state["phase"] not in {"ready", "running"}:
        raise ValueError("启动门槛未通过或已最终冻结")
    cfg = read_json(root / "comparison-protocol.json")
    if state["phase"] == "ready":
        for name in (
            "material-audit",
            "isolation-all",
            "cli-capability",
            "worker-check",
            "runtime-capability",
        ):
            if not read_json(root / f"evidence/{name}.json").get("passed"):
                raise ValueError(f"缺实际启动证据:{name}")
    write_json(root / "state.json", {"phase": "running", "formal_sessions_started": True})
    for number in range(6):
        for group in cfg["round_orders"][str(number)]:
            if (root / f"receipts/{group}/round-{number:02d}.json").exists():
                verify_frozen(root, group, number)
                continue
            print(json.dumps({"event": "round_start", "group": group, "round": number}), flush=True)
            source = driver.round(group, number, cfg["experiments"][group])
            freeze(root, group, number, source)
            print(
                json.dumps({"event": "round_frozen", "group": group, "round": number}), flush=True
            )
    for group, location in cfg["experiments"].items():
        if not (root / f"final-selections/{group}.json").exists():
            lock(root, group, driver.select_final(group, location))


def hidden(root, evaluator=None):
    """全体最终锁定后才取隐藏输入，候选失败不能进入重选。"""
    root = Path(root)
    if read_json(root / "state.json")["phase"] not in {"all_finals_locked", "hidden_evaluating"}:
        raise ValueError("四组最终冻结之前禁止隐藏评价")
    cfg = read_json(root / "comparison-protocol.json")
    for group in CELLS:
        chosen = read_json(root / f"final-selections/{group}.json")
        if (
            digest(root / f"receipts/{group}/round-{chosen['round']:02d}.json")
            != chosen["receipt_sha256"]
        ):
            raise ValueError("最终收据变化")
        for n in range(6):
            verify_frozen(root, group, n)
    samples = read_json(root / "private-split.json")["splits"]["test"]
    for sample in samples:
        if digest(sample["path"]) != sample["sha256"]:
            raise ValueError("隐藏数据摘要变化")
    write_json(root / "state.json", {"phase": "hidden_evaluating", "formal_sessions_started": True})
    for group in CELLS:
        for n in range(6):
            out = root / f"hidden-results/{group}/round-{n:02d}"
            if (out / "result.json").exists():
                continue
            candidate = verify_frozen(root, group, n)
            environment = root / f"frozen-environments/{group}/round-{n:02d}"
            if evaluator is None:
                if inventory(environment) != read_json(
                    root / f"environment-receipts/{group}/round-{n:02d}.json"
                ):
                    raise ValueError("轮末依赖变化")
                result = evaluate_candidate(
                    candidate,
                    environment,
                    cfg["runtime_readonly_roots"],
                    samples,
                    out,
                    latency_seed=42,
                )
            else:
                result = evaluator(group, n, candidate, out)
            write_json(out / "result.json", result)
    write_json(
        root / "state.json",
        {"phase": "hidden_evaluated_audit_pending", "formal_sessions_started": True},
    )


def main():
    """显式分开交付、权限预检、研究和隐藏评价。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["materials", "probe", "run", "hidden"])
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    {"materials": prepare, "probe": probe_all, "run": run, "hidden": hidden}[args.action](args.root)


if __name__ == "__main__":
    main()
