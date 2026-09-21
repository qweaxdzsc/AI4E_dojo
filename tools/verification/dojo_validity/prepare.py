"""生成相同 baseline，分开物化组级根、实验 ID 和 Dojo 使用材料。"""

import ast
import importlib.util
import shutil
import uuid
from pathlib import Path

import numpy as np
import torch
import yaml

from .io import digest, inventory, read_json, write_json

REPO = Path(__file__).resolve().parents[3]
BASELINE = {
    "case": "neumann_diffusion",
    "train_samples": 50,
    "test_samples": 10,
    "grid": [128, 128],
    "control_points": [40, 40],
    "degree": 5,
    "hidden_dim": 128,
    "seed": 42,
    "epochs": 5000,
    "learning_rate": 0.001,
    "device": "cpu",
    "threads": 1,
    "precision": "fp32",
    "loss_weights": {"pde": 1, "data": 5, "initial": 2, "boundary": 2},
}


def build_baseline(destination, reference_source):
    """从摘要锁定原源码抽取普通函数，生成原随机流的数据与初始权重。"""
    destination, reference_source = Path(destination), Path(reference_source)
    expected = read_json(REPO / "packages/ai4e-contrib/ability/model/pibsnet/source.json")
    if digest(reference_source) != expected["reference_files"]["src/neumann_bc.py"]:
        raise ValueError("Neumann 参考源码摘要不匹配")
    destination.mkdir(parents=True, exist_ok=False)
    source_dir = destination / "source"
    source_dir.mkdir()
    names = {
        "BsFun",
        "BsFun_derivative",
        "BsFun_second_derivative",
        "BsKnots",
        "BsKnots_derivatives",
        "bspline_eval",
        "bspline_derivs",
        "ControlPointNet",
        "BSNetLoss",
        "VanillaPINN",
        "PIDeepONet",
    }
    tree = ast.parse(reference_source.read_text())
    nodes = [
        n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names
    ]
    if {n.name for n in nodes} != names:
        raise ValueError("参考源码缺定义")
    source = (
        '"""PI-BSNet 原始 Neumann 数值定义；参数坐标导数。"""\n'
        "import numpy as np\nimport torch\nimport torch.nn as nn\n"
        'device = torch.device("cpu")\n\n' + "\n\n".join(ast.unparse(n) for n in nodes) + "\n"
    )
    (source_dir / "numerics.py").write_text(source)
    shutil.copyfile(Path(__file__).with_name("baseline_runtime.py"), source_dir / "baseline.py")
    spec = importlib.util.spec_from_file_location("baseline_numerics", source_dir / "numerics.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    torch.manual_seed(42)
    module.VanillaPINN(hidden=128)
    module.PIDeepONet(branch_hidden=128, trunk_hidden=128)
    model = module.BSNetLoss(40, 40, 128)
    assert sum(p.numel() for p in model.parameters()) == 223168
    torch.save({"model": model.state_dict(), "updates": 0}, destination / "initial-checkpoint.pt")
    rng = np.random.RandomState(42)
    axis = np.linspace(0, 1, 128, dtype=np.float32)
    x, t = np.meshgrid(axis, axis, indexing="xy")
    data = {"x": axis, "t": axis}
    for split, count in (("train", 50), ("test", 10)):
        nu, values = [], []
        for _ in range(count):
            parameter = rng.uniform(0.1, 1.5)
            values.append(np.cos(np.pi * x) * np.exp(-parameter * (np.pi**2) * t))
            nu.append(parameter)
        data[f"{split}_nu"] = np.asarray(nu, dtype=np.float32)
        data[f"{split}_u"] = np.asarray(values, dtype=np.float32)
    coordinates, knots, basis = module.BsKnots(40, 5, 128)
    d1, d2 = module.BsKnots_derivatives(40, 5, 128, knots, coordinates)
    data.update(basis=basis, basis_d1=d1, basis_d2=d2)
    np.savez(destination / "dataset.npz", **data)
    truth = destination / "truth"
    truth.mkdir()
    records = []
    for i, field in enumerate(data["test_u"]):
        path = truth / f"test-{i:05d}.npy"
        np.save(path, field, allow_pickle=False)
        records.append({"id": path.stem, "path": path.name, "sha256": digest(path)})
    write_json(truth / "manifest.json", {"samples": records})
    (destination / "config.yaml").write_text(yaml.safe_dump(BASELINE, sort_keys=False))
    write_json(
        destination / "dataset-manifest.json",
        {
            "samples": [
                {"id": f"{split}-{i:05d}", "split": split}
                for split, n in (("train", 50), ("test", 10))
                for i in range(n)
            ],
            "dataset_sha256": digest(destination / "dataset.npz"),
        },
    )
    write_json(
        destination / "evaluator-manifest.json",
        {
            "metric": "mean_full_field_relative_l2",
            "precision": "float64",
            "evaluator_sha256": digest(Path(__file__).with_name("metrics.py")),
        },
    )
    write_json(
        destination / "provenance.json",
        {
            "source_sha256": digest(reference_source),
            "reference_commit": expected["reference_commit"],
            "initialization": "seed42 PINN, DeepONet constructors consumed before BSNetLoss",
            "derivatives": "original parameter-coordinate derivatives, not physical rescaling",
        },
    )
    # importlib 生成的字节码含制备路径，不能作为实验输入。
    shutil.rmtree(source_dir / "__pycache__", ignore_errors=True)
    return inventory(destination)


def initial_prompt(protocol):
    """生成仅含本组位置的首轮任务说明；不向白板组暴露框架和对方路径。"""
    experiment = protocol["experiment_id"]
    text = f"""你的会话工作根是 {protocol["session_workspace_root"]}。
本次实验目录是该根下的 {experiment}/，不得更改工作根或访问未授权本机目录。
以提供的 PI-BSNet Neumann baseline 开始，连续进行五轮改进。本消息启动第一轮。
第一目标是降低固定十个实例的完整时空场平均相对 L2；其次减少编码时间和 token。
允许自由搜索公共互联网、修改架构、损失、优化器和训练预算，不设时间或 token 上限。
所有尝试、失败、训练、评价与代码变动均需留档；每轮结束提交冻结源码、配置、
checkpoint、推理入口、预测及总结。不得读写其他会话或利用本机服务获取目录外资料。
baseline/ 保存共同起点；在 workspace/ 修改；environment/ 为本组独立环境。
阶段时间及供应商 usage 由执行器记录，缺失不得填零。每轮提交后等待下一轮指令。
"""
    if protocol["group"] == "dojo":
        text += """
你可以使用 Dojo。入口是本次实验的 dojo-resources/DOJO_AGENT_GUIDE.md。
使用前先阅读入口及 docs/agent-help/index.md；支持 skills 时可用本地 dojo-research。
按任务检索工作流和现行 API 签名，先 direct-core，再按需使用 Task。
文档学习计入编码成本。使用案例时不得无记录替换 baseline 或初始权重。
"""
    return text


def prepare_pair(base, reference_source):
    """仅首次创建干净组根；拒绝已有内容，不删除或覆盖历史实验。"""
    base = Path(base).resolve()
    for group in ("plain", "dojo"):
        root = base / f"neumann-{group}"
        if root.is_symlink() or (root.exists() and any(root.iterdir())):
            raise FileExistsError(f"组级工作根非空，不能混入历史材料: {root}")
    comparison = base / "neumann-comparison" / f"comparison-{uuid.uuid4()}"
    comparison.mkdir(parents=True)
    baseline = comparison / "baseline"
    hashes = build_baseline(baseline, reference_source)
    mapping = {}
    for group in ("plain", "dojo"):
        root = base / f"neumann-{group}"
        experiment_id = f"experiment-{uuid.uuid4()}"
        experiment = root / experiment_id
        experiment.mkdir(parents=True)
        for name in (
            "workspace",
            "environment",
            "data",
            "cache",
            "tmp",
            "agent-state",
            "evidence",
            "final",
            "results",
            *[f"round-{n:02d}" for n in range(6)],
        ):
            (experiment / name).mkdir()
        shutil.copytree(baseline, experiment / "baseline")
        shutil.copytree(baseline / "source", experiment / "workspace", dirs_exist_ok=True)
        protocol = {
            "version": 1,
            "group": group,
            "experiment_id": experiment_id,
            "session_workspace_root": str(root),
            "experiment_root": str(experiment),
            "rounds": 5,
            "baseline": BASELINE,
            "baseline_files": hashes,
            "shared_readonly_roots": [],
            "status": "prepared",
            "session_id": None,
            "model": None,
            "reasoning": None,
            "isolation_verified": False,
            "environment_ready": False,
        }
        write_json(experiment / "protocol.json", protocol)
        (experiment / "TASK.md").write_text(initial_prompt(protocol))
        (root / "AGENTS.md").write_text(
            "# 实验工作根\n仅在本根内执行本次实验；实验说明见子目录 TASK.md。\n"
            "禁止访问父目录资料、其他会话和本机资料连接器；公共互联网搜索开放。\n"
        )
        if group == "dojo":
            resources = experiment / "dojo-resources"
            resources.mkdir()
            shutil.copy2(REPO / "DOJO_AGENT_GUIDE.md", resources / "DOJO_AGENT_GUIDE.md")
            for relative in (
                ".agents/skills/dojo-research",
                "docs/agent-help",
                "examples",
                "recipes",
            ):
                shutil.copytree(
                    REPO / relative,
                    resources / relative,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            write_json(experiment / "evidence/dojo-resources.json", inventory(resources))
        mapping[group] = str(experiment)
    write_json(
        comparison / "comparison-protocol.json",
        {
            "version": 1,
            "experiments": mapping,
            "baseline_files": hashes,
            "truth_manifest": str(baseline / "truth/manifest.json"),
            "status": "prepared_not_started",
        },
    )
    return comparison


def seal_preparation(comparison):
    """首次运行前封存最终工具副本；保留准备期旧摘要，任何训练开始后拒绝更新。"""
    comparison = Path(comparison)
    config = read_json(comparison / "comparison-protocol.json")
    if config.get("sealed"):
        raise ValueError("材料已封存，不得改写起点")
    roots = [Path(p) for p in config["experiments"].values()]
    for root in roots:
        if any((root / "round-00").iterdir()) or (root / "evidence/execution.json").exists():
            raise ValueError("实验已执行，禁止刷新初始材料")
    write_json(comparison / "evidence/preparation-before-seal.json", config)
    for baseline in [comparison / "baseline", *[p / "baseline" for p in roots]]:
        shutil.rmtree(baseline / "source/__pycache__", ignore_errors=True)
        shutil.copyfile(
            Path(__file__).with_name("baseline_runtime.py"), baseline / "source/baseline.py"
        )
        info = read_json(baseline / "evaluator-manifest.json")
        info["evaluator_sha256"] = digest(Path(__file__).with_name("metrics.py"))
        write_json(baseline / "evaluator-manifest.json", info)
    hashes = inventory(comparison / "baseline")
    for root in roots:
        if inventory(root / "baseline") != hashes:
            raise ValueError("最终两组 baseline 不一致")
        shutil.copyfile(root / "baseline/source/baseline.py", root / "workspace/baseline.py")
        protocol = read_json(root / "protocol.json")
        protocol.update(baseline_files=hashes, inputs_sealed=True)
        write_json(root / "protocol.json", protocol)
        if protocol["group"] == "dojo":
            write_json(root / "evidence/dojo-resources.json", inventory(root / "dojo-resources"))
    (comparison / "evaluator").mkdir(exist_ok=True)
    for name in ("metrics.py", "io.py"):
        shutil.copyfile(Path(__file__).with_name(name), comparison / "evaluator" / name)
    config.update(baseline_files=hashes, sealed=True)
    write_json(comparison / "comparison-protocol.json", config)
