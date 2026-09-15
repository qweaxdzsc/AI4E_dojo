"""迁移前独立比较原代码与物理导数解释；不导入或修改 Dojo 数值实现。

六组保持原数据、初始化、权重和轮数；Neumann 交叉检查更新分组。
标准物理导数是对论文物理 PDE 的数学解释，不声称消除了式12记号歧义。
"""

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

VARIANTS = {
    "neumann_source_epoch": ("neumann_diffusion", False, False, 5000, 5000),
    "neumann_physical_epoch": ("neumann_diffusion", True, False, 5000, 5000),
    "neumann_source_instance": ("neumann_diffusion", False, True, 5000, 250000),
    "neumann_physical_instance": ("neumann_diffusion", True, True, 5000, 250000),
    "advection_source": ("advection", False, True, 2000, 200000),
    "advection_physical": ("advection", True, True, 2000, 200000),
}

# 使用与原代码相同节点分布和次数，标准递推及定义域内单侧端点。
PHYSICAL = """
from scipy.interpolate import BSpline as _TrialBSpline
def BsKnots(n_cp, d, Ns):
    knots = np.r_[np.zeros(d), np.arange(n_cp-d+1), np.full(d, n_cp-d)]
    tk = np.linspace(0, n_cp-d, Ns)
    return tk, knots, _TrialBSpline(knots, np.eye(n_cp), d)(tk)
def BsKnots_derivatives(n_cp, d, Ns, Ln, tk):
    spline = _TrialBSpline(Ln, np.eye(n_cp), d)
    return spline(tk, nu=1), spline(tk, nu=2)
"""


def replace_once(source, old, new):
    """源码漂移或重复定位时立即失败。"""
    if source.count(old) != 1:
        raise ValueError(f"非唯一源码定位：{old[:90]}")
    return source.replace(old, new, 1)


def amend(source, case, label, variant):
    """只修改获批的导数解释和 Neumann 更新分组。"""
    expected_case, physical, instance, _, _ = VARIANTS[variant]
    if case != expected_case:
        raise ValueError("案例与实验不匹配")
    if case == "neumann_diffusion" and label == "script":
        if physical:
            source = replace_once(
                source, "tk_x, Ln_x, Bx_np = BsKnots", PHYSICAL + "\ntk_x, Ln_x, Bx_np = BsKnots"
            )
            source = replace_once(
                source,
                "Bx     = torch.tensor",
                "Bx_d1_np *= (n_cp_x-d)/(x1-x0)\nBx_d2_np *= ((n_cp_x-d)/(x1-x0))**2\n"
                "Bt_d1_np *= (n_cp_t-d)/T_max\nBt_d2_np *= ((n_cp_t-d)/T_max)**2\n\nBx     = torch.tensor",
            )
        if instance:
            source = replace_once(
                source,
                "        for sample in train_data:\n",
                "        for sample in train_data:\n            optimizer.zero_grad()\n",
            )
            source = replace_once(
                source,
                "            total_L = total_L + L",
                "            L.backward()\n            optimizer.step()\n            total_L = total_L + L.detach()",
            )
            source = replace_once(
                source,
                "        total_L.backward()\n        optimizer.step()",
                "        # 已按 Algorithm 1 在每个实例内更新。",
            )
    if case == "advection" and physical:
        if label == "cell-00":
            source += "\n" + PHYSICAL
        if label == "cell-10":
            source = replace_once(
                source,
                "# Convert them to PyTorch tensors",
                'Bit_x_derivative *= (n_cp_x-d)/float(training_data[0]["x"][-1]-training_data[0]["x"][0])\n'
                'Bit_t_derivative *= (n_cp_t-d)/float(training_data[0]["t"][-1]-training_data[0]["t"][0])\n'
                "# Convert them to PyTorch tensors",
            )
    return source


def sha(path):
    """冻结文件摘要。"""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write(path, value):
    """原子写实验状态。"""
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    temporary.replace(path)


def prepare(root, baseline):
    """核验来源并生成只在独立目录执行的六份入口。"""
    hashes = json.loads((baseline / "source/hashes.json").read_text())
    names = ["neumann_bc.py", "advection.ipynb", "run_original.py", "PI-BSNet.pdf"]
    for name in names:
        if sha(baseline / "source" / name) != hashes[name]:
            raise ValueError(f"锁定来源漂移：{name}")
    root.mkdir(parents=True, exist_ok=False)
    (root / "source/reference/src").mkdir(parents=True)
    (root / "environment").mkdir()
    (root / "reports").mkdir()
    for name in names:
        shutil.copy2(baseline / "source" / name, root / "source" / name)
    for name in names[:2]:
        shutil.copy2(baseline / "source" / name, root / "source/reference/src" / name)
    shutil.copy2(__file__, root / "source/neumann_advection_trials.py")
    original = (baseline / "source/run_original.py").read_text()
    for variant, (case, *_rest) in VARIANTS.items():
        target = root / variant
        target.mkdir()
        runner = replace_once(
            original,
            "ROOT = pathlib.Path('/Users/zonghui/work/project_simulation/dojo_train/pibsnet/original_baseline')",
            f"ROOT = pathlib.Path({str(target)!r})",
        )
        runner = replace_once(
            runner,
            "SOURCE = pathlib.Path('/Users/zonghui/work/new_code_project/PI-BSNet')",
            f"SOURCE = pathlib.Path({str(root / 'source/reference')!r})",
        )
        runner = replace_once(
            runner,
            "    def execute(original, edited, label):",
            "    def execute(original, edited, label):\n"
            "        from neumann_advection_trials import amend\n"
            f"        edited = amend(edited, case, label, {variant!r})",
        )
        (root / "source" / f"{variant}.py").write_text(runner)
        (root / "source" / f"{variant}.patch").write_text(
            "".join(difflib.unified_diff(original.splitlines(True), runner.splitlines(True)))
        )
        # 启动前编译每个实际数值补丁，不用运行后才发现定位错误。
        if case == "neumann_diffusion":
            compile(
                amend((baseline / "source/neumann_bc.py").read_text(), case, "script", variant),
                variant,
                "exec",
            )
        else:
            notebook = json.loads((baseline / "source/advection.ipynb").read_text())
            for i in [0, 2, 4, 10, 13]:
                compile(
                    amend("".join(notebook["cells"][i]["source"]), case, f"cell-{i:02d}", variant),
                    variant,
                    "exec",
                )
    write(
        root / "protocol.json",
        {
            "variants": VARIANTS,
            "source_hashes": {n: hashes[n] for n in names},
            "baseline": str(baseline),
            "seed": 42,
            "threads": 1,
            "paper": {
                "neumann": {"mean_relative_l2": 0.01932, "location": "C.4 / Table1 / PDF31"},
                "advection": {
                    "mean_relative_l2": 0.1444,
                    "std_relative_l2": 0.1352,
                    "location": "5.2 / D.2",
                },
            },
            "unchanged": [
                "原生成数据与随机流",
                "原初始化顺序",
                "初边界与损失权重",
                "Adam .001",
                "完整轮数与全测试名单",
            ],
            "interpretation": "physical 使用标准样条物理导数及单侧端点；source 保留原递推、参数导数和端点。物理组也采用标准值基，FP64构造后FP32计算。",
            "unresolved": [
                "论文式12次数记号与具体离散实现不充分",
                "论文随机名单未公开",
                "CPU环境不同于论文RTX4090",
                "单种子不替代多次独立统计",
            ],
            "migration": "不改 Dojo 算法；完成测试后再决定迁移，数值接近不能单独证明算法正确。",
        },
    )


def batch(root, python):
    """每进程一个完整实验；两条独立单线程队列，失败保留并继续其余组。"""
    env = os.environ.copy()
    env.update(
        MPLBACKEND="Agg",
        MPLCONFIGDIR=str(root / "environment/matplotlib"),
        PYTHONDONTWRITEBYTECODE="1",
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MKL_NUM_THREADS="1",
        UV_CACHE_DIR=str(root / "environment/uv-cache"),
    )

    def one(variant):
        case = VARIANTS[variant][0]
        with (root / variant / "console.log").open("w") as log:
            return subprocess.call(
                [
                    "uv",
                    "run",
                    "--no-project",
                    str(python.absolute()),
                    str(root / "source" / f"{variant}.py"),
                    case,
                ],
                env=env,
                stdout=log,
                stderr=subprocess.STDOUT,
            )

    write(
        root / "batch.json",
        {"status": "running", "variants": list(VARIANTS), "python": str(python.absolute())},
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {v: pool.submit(one, v) for v in VARIANTS}
        outcomes = {v: f.result() for v, f in futures.items()}
    write(
        root / "batch.json",
        {"status": "complete" if not any(outcomes.values()) else "failed", "exit_codes": outcomes},
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["prepare", "run"])
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--python", type=Path)
    args = parser.parse_args()
    if args.action == "prepare":
        prepare(args.root, args.baseline)
    else:
        batch(args.root, args.python)
