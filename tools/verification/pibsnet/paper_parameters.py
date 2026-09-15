"""在冻结原仓库基线上执行经用户确认的三组论文参数实验。

不导入或修改 Dojo 算法。原执行器负责数据、训练、预测和记录；本工具只
生成严格计数的源码补丁、冻结实验协议，并检查完整预算与可重算指标。
样条、初边界及数据空间算子的未决差异不会被静默修正。
"""

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

VARIANTS = {
    "burgers": ("burgers", 5000, 500000),
    "trapezoid_10": ("diffusion_trapezoid", 3000, 30000),
    "trapezoid_50": ("diffusion_trapezoid", 3000, 150000),
}


def replace_once(source, old, new):
    """拒绝来源漂移或非唯一定位，不执行模糊替换。"""
    if source.count(old) != 1:
        raise ValueError(f"源码定位不唯一：{old[:100]!r}")
    return source.replace(old, new, 1)


def amend_cell(source, case, index, variant):
    """只应用确认的方程、损失、实例数、控制网格和权重变更。"""
    if case == "burgers" and index == 5:
        source = replace_once(
            source,
            "pde_residual = B_surface_t - mu * B_surface * B_surface_x - nu * B_surface_xx",
            "pde_residual = B_surface_t + mu * B_surface * B_surface_x - nu * B_surface_xx",
        )
        source = replace_once(
            source,
            "physics_loss = torch.norm(pde_residual)",
            "physics_loss = pde_residual.square().mean()",
        )
        source = replace_once(
            source,
            "data_loss = torch.norm(B_surface - U_tensor)",
            "data_loss = (B_surface - U_tensor).square().mean()",
        )
    elif case == "diffusion_trapezoid" and index == 2:
        count = {"trapezoid_10": 10, "trapezoid_50": 50}[variant]
        source = replace_once(
            source,
            "N_train = 20  # Increase this number for more training samples",
            f"N_train = {count}  # Paper main text / appendix variant",
        )
        source = replace_once(
            source,
            "n_cp_t = n_steps; n_cp_x = Nx; n_cp_y = Ny",
            "n_cp_t = 100; n_cp_x = 20; n_cp_y = 20",
        )
        source = replace_once(source, "lambda_phys=1e-5", "lambda_phys=0.001")
    return source


def write_json(path, value):
    """原子保存状态，避免读取半个 JSON。"""
    path = Path(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    tmp.replace(path)


def sha(path):
    """计算冻结源码的内容摘要。"""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(root, baseline):
    """生成独立运行资产，拒绝覆盖；执行前必须先完成来源核查。"""
    original = baseline / "source"
    expected = json.loads((original / "hashes.json").read_text())
    for name in ("burgers.ipynb", "diffusion_trapezoid.ipynb", "run_original.py", "PI-BSNet.pdf"):
        if sha(original / name) != expected[name]:
            raise ValueError(f"冻结来源摘要不匹配：{name}")
    for variant, (case, _, _) in VARIANTS.items():
        notebook = json.loads((original / (case + ".ipynb")).read_text())
        for index, cell in enumerate(notebook["cells"]):
            if cell["cell_type"] == "code":
                amend_cell("".join(cell["source"]), case, index, variant)
    root.mkdir(parents=True, exist_ok=False)
    for folder in ("source/reference/src", "environment", "reports"):
        (root / folder).mkdir(parents=True)
    for name in ("burgers.ipynb", "diffusion_trapezoid.ipynb"):
        shutil.copy2(original / name, root / "source/reference/src" / name)
    shutil.copy2(original / "PI-BSNet.pdf", root / "source/PI-BSNet.pdf")
    shutil.copy2(__file__, root / "source/paper_parameters.py")
    shutil.copy2(original / "run_original.py", root / "source/run_original.frozen.py")
    shutil.copy2(baseline / "environment/runtime.json", root / "environment/baseline_runtime.json")
    protocol = {
        "purpose": "用户确认的论文参数差异验证，非完整论文算法复现",
        "commit": "40ffb6239d865b6b7a16538559939a990e6d9cd5",
        "baseline": str(baseline),
        "variants": VARIANTS,
        "changes": {
            "burgers": {
                "convection_sign": "+ (PDF41 Eq86)",
                "loss": "MSE (PDF5 Eq8/9)",
                "data_weight": "15 (source supplement)",
                "epochs": 5000,
            },
            "trapezoid_10": {
                "train_instances": "10 (PDF11 main text)",
                "controls_txy": [100, 20, 20],
                "pde_weight": 0.001,
                "epochs": 3000,
            },
            "trapezoid_50": {
                "train_instances": "50 (PDF36 D.3)",
                "controls_txy": [100, 20, 20],
                "pde_weight": 0.001,
                "epochs": 3000,
            },
        },
        "unchanged": [
            "原数据生成与求解器",
            "原样条、导数与端点",
            "原初边界实现",
            "原逐实例Adam更新与初始化",
            "原测试流程与随机流",
        ],
        "unresolved": [
            "样条物理尺度、二阶递推及论文阶数记号",
            "Burgers初值控制赋值",
            "梯形数据完整坐标变换",
            "论文随机种子与测试名单未提供",
            "CPU不是论文RTX4090环境",
            "梯形论文指标聚合细节未完全明确",
        ],
        "test_scope": "Burgers测试集与原基线相同；梯形保持原随机流，改变训练数量后测试参数会改变，三组不是共同测试名单的因果实验。",
        "source_hashes": {
            name: expected[name]
            for name in (
                "burgers.ipynb",
                "diffusion_trapezoid.ipynb",
                "run_original.py",
                "PI-BSNet.pdf",
            )
        },
        "acceptance": "完整预算与全部预测可重算；数值相近不自动判算法复现通过；不选优、重跑或调参。",
    }
    write_json(root / "protocol.json", protocol)
    template = (original / "run_original.py").read_text()
    for variant in VARIANTS:
        runner = replace_once(
            template,
            "ROOT = pathlib.Path('/Users/zonghui/work/project_simulation/dojo_train/pibsnet/original_baseline')",
            f"ROOT = pathlib.Path({str(root)!r})",
        )
        runner = replace_once(
            runner,
            "SOURCE = pathlib.Path('/Users/zonghui/work/new_code_project/PI-BSNet')",
            f"SOURCE = pathlib.Path({str(root / 'source/reference')!r})",
        )
        runner = replace_once(runner, "root = ROOT / case", f"root = ROOT / {variant!r}")
        runner = replace_once(
            runner,
            "original=''.join(notebook['cells'][index]['source']); edited=original",
            "original=''.join(notebook['cells'][index]['source']); edited=amend_cell(original, case, index, "
            + repr(variant)
            + ")",
        )
        runner = replace_once(
            runner,
            "import os, sys, json, time, hashlib, pathlib, shutil, difflib, traceback, subprocess",
            "import os, sys, json, time, hashlib, pathlib, shutil, difflib, traceback, subprocess\nfrom paper_parameters import amend_cell",
        )
        runner = replace_once(
            runner,
            "    if len(sys.argv)==1:batch()",
            "    if len(sys.argv)==1:raise SystemExit('explicit case required')",
        )
        runner = replace_once(
            runner,
            "value = ns.get('total_loss', ns.get('total_L'))",
            "value = ns.get('total_loss', ns.get('total_L', ns.get('avg_loss')))",
        )
        path = root / "source" / (variant + ".py")
        path.write_text(runner)
        path.with_suffix(".patch").write_text(
            "".join(
                difflib.unified_diff(
                    template.splitlines(True),
                    runner.splitlines(True),
                    fromfile="frozen_runner",
                    tofile=variant,
                )
            )
        )
        compile(runner, str(path), "exec")
    write_json(
        root / "source/hashes.json",
        {str(p.relative_to(root)): sha(p) for p in (root / "source").rglob("*") if p.is_file()},
    )


def batch(root, baseline, python):
    """顺序运行三组完整实验，记录退出状态，不覆盖失败或完成的目录。"""
    env = os.environ.copy()
    env.update(
        MPLBACKEND="Agg",
        MPLCONFIGDIR=str(root / "environment/matplotlib"),
        PYTHONDONTWRITEBYTECODE="1",
        PYTHONPATH=str(baseline / "environment/extra"),
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
    )
    finished = []
    for variant, (case, _, _) in VARIANTS.items():
        write_json(
            root / "batch.json", {"status": "running", "current": variant, "finished": finished}
        )
        with (root / (variant + ".console.log")).open("x") as log:
            code = subprocess.call(
                [
                    "uv",
                    "--no-cache",
                    "run",
                    "--no-project",
                    str(python),
                    str(root / "source" / (variant + ".py")),
                    case,
                ],
                stdout=log,
                stderr=subprocess.STDOUT,
                env=env,
            )
        finished.append({"variant": variant, "exit_code": code})
    write_json(root / "batch.json", {"status": "finished", "finished": finished})
    return int(any(item["exit_code"] for item in finished))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "batch"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--python", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.root.resolve(), args.baseline.resolve())
    else:
        if args.python is None:
            parser.error("batch requires --python")
        # 保留虚拟环境入口符号链接，避免绕过 pyvenv.cfg。
        sys.exit(batch(args.root.resolve(), args.baseline.resolve(), args.python.absolute()))
