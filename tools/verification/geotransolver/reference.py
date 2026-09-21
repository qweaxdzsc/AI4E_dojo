# ruff: noqa: S102
# 独立参考执行经版本核对的本地源码定义，不执行网络下载内容。
"""独立执行锁定上游定义；不从 Dojo 导入任何数值组件。"""

from __future__ import annotations

import ast
import subprocess
import types
from pathlib import Path

REVISION = "aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1"
DEFAULT_SOURCE = Path("/Users/zonghui/work/new_code_project/physicsnemo")


def locked_source(path, source=DEFAULT_SOURCE):
    """读取与固定提交逐字一致的源文件，防止工作树修改污染参考。"""
    path, source = Path(path).resolve(), Path(source).resolve()
    relative = path.relative_to(source).as_posix()
    raw = path.read_text()
    committed = subprocess.check_output(
        ["git", "-C", str(source), "show", f"{REVISION}:{relative}"], text=True
    )
    if raw != committed:
        raise ValueError(f"参考文件被改动: {relative}")
    return raw


def load_reference(source=DEFAULT_SOURCE):
    """剥离第三方导入和元数据，保留原函数/类 AST（包含原邻域及检查点定义）。"""
    source = Path(source)
    if (
        subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
        != REVISION
    ):
        raise ValueError("参考源码版本不匹配")
    module = types.ModuleType("geotransolver_independent_reference")
    header = """from __future__ import annotations
import torch, math, itertools
import torch.nn as nn
import torch.nn.functional as F
from abc import ABC, abstractmethod
from einops import rearrange
from torch.autograd.profiler import record_function
from torch.distributed.tensor.placement_types import Replicate
from collections.abc import Callable, Sequence
from typing import Any, Literal
te=None
TE_AVAILABLE=False
DEFAULT_CHECKPOINTING_COMPONENTS=frozenset({'blocks'})
CHECKPOINTABLE_COMPONENTS=frozenset({'blocks','context','preprocess','output'})
class Module(nn.Module):
    def __init__(self, meta=None):
        super().__init__()
        self._args={'__args__':{}}
def GeoTransolverMetaData(): return None
def get_activation(name):
    return {'gelu':nn.GELU,'relu':nn.ReLU,'silu':nn.SiLU,'tanh':nn.Tanh}[name]()
"""
    exec(header, module.__dict__)
    files = [
        ("physicsnemo/nn/functional/neighbors/radius_search/utils.py", None),
        ("physicsnemo/nn/functional/neighbors/radius_search/_torch_impl.py", None),
        ("physicsnemo/nn/module/ball_query.py", None),
        ("physicsnemo/nn/module/mlp_layers.py", ["Mlp"]),
        ("physicsnemo/nn/module/physics_attention.py", None),
        ("physicsnemo/nn/module/gale.py", None),
        ("physicsnemo/models/utils/activation_checkpointing.py", None),
        ("physicsnemo/models/geotransolver/activation_checkpointing.py", None),
        ("physicsnemo/models/transolver/transolver.py", ["_TransolverMlp"]),
        ("physicsnemo/models/geotransolver/context_projector.py", None),
        (
            "physicsnemo/models/geotransolver/geotransolver.py",
            [
                "_normalize_dim",
                "_normalize_tensor",
                "_structured_num_tokens",
                "_flatten_for_structured",
                "GeoTransolver",
            ],
        ),
    ]
    for relative, names in files:
        path = source / relative
        raw = path.read_text()
        # Detect dirty upstream definitions instead of trusting only HEAD.
        committed = subprocess.check_output(
            ["git", "-C", str(source), "show", f"{REVISION}:{relative}"], text=True
        )
        if raw != committed:
            raise ValueError(f"参考文件被改动: {relative}")
        tree = ast.parse(raw)
        selected = [
            n
            for n in tree.body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and (names is None or n.name in names)
        ]
        text = "from __future__ import annotations\n" + ast.unparse(
            ast.Module(body=selected, type_ignores=[])
        )
        exec(compile(text, str(path), "exec"), module.__dict__)
    return module


def cached_cpu_radius(reference, *, chunk_size=256):
    """独立上游 torch 查询按查询轴分块并缓存；MPS 仅用于学习计算。"""
    import hashlib

    import torch

    original = reference.radius_search
    cache = {}

    def query(points, queries, radius, max_points=None, return_dists=False, return_points=False):
        if max_points is None or not return_points or return_dists:
            raise ValueError("工程对照限定固定邻居和坐标返回")
        key = (
            hashlib.sha256(points.detach().cpu().numpy().tobytes()).hexdigest(),
            hashlib.sha256(queries.detach().cpu().numpy().tobytes()).hexdigest(),
            radius,
            max_points,
        )
        if key not in cache:
            p, q = points.detach().cpu(), queries.detach().cpu()
            pieces = [
                original(p, q[:, i : i + chunk_size], radius, max_points, return_points=True)
                for i in range(0, q.shape[1], chunk_size)
            ]
            cache[key] = (
                torch.cat([i for i, _ in pieces], 1),
                torch.cat([v for _, v in pieces], 1),
            )
        i, v = cache[key]
        return i.to(points.device), v.to(points.device)

    reference.radius_search = query
    return cache


def reference_optimizer(model, *, lr, weight_decay):
    """独立执行上游组合优化器定义，使用原二维分组和默认超参数。"""
    import torch

    namespace = {"torch": torch, "Optimizer": torch.optim.Optimizer}
    path = DEFAULT_SOURCE / "physicsnemo/optim/combined_optimizer.py"
    tree = ast.parse(locked_source(path))
    selected = [
        n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "CombinedOptimizer"
    ]
    exec(
        "from __future__ import annotations\n"
        + ast.unparse(ast.Module(body=selected, type_ignores=[])),
        namespace,
    )
    return namespace["CombinedOptimizer"](
        [
            torch.optim.Muon(
                [p for p in model.parameters() if p.ndim == 2],
                lr=lr,
                weight_decay=weight_decay,
                adjust_lr_fn="match_rms_adamw",
            ),
            torch.optim.AdamW(
                [p for p in model.parameters() if p.ndim != 2], lr=lr, weight_decay=weight_decay
            ),
        ]
    )
