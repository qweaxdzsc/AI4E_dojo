"""从锁定参考提取数值定义；只转换依赖、类型标注、说明和未支持分支门禁。"""

from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path

REVISION = "aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1"


class Port(ast.NodeTransformer):
    """保留计算表达式，去掉第三方标注及框架元数据。"""

    def visit_Assign(self, node):
        unsupported = {"ConcreteDropout", "GALE_FA", "GALEStructuredMesh3D", "gumbel_softmax"}
        if any(isinstance(x, ast.Name) and x.id in unsupported for x in ast.walk(node.value)):
            return ast.parse('raise NotImplementedError("此扩展分支不在当前移植范围")').body[0]
        return self.generic_visit(node)

    def visit_Subscript(self, node):
        if isinstance(node.value, ast.Name) and node.value.id == "Float":
            return ast.parse("torch.Tensor", mode="eval").body
        return self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.generic_visit(node)
        doc = ast.get_docstring(node)
        if doc:
            node.body[0].value.value = (
                "执行" + node.name + "；张量布局、参数与返回值见下列参考说明。\n\n" + doc
            )
        return node

    def visit_ClassDef(self, node):
        self.generic_visit(node)
        doc = ast.get_docstring(node)
        if doc:
            node.body[0].value.value = "可独立使用的" + node.name + "计算组件。\n\n" + doc
        init = next(
            (x for x in node.body if isinstance(x, ast.FunctionDef) and x.name == "__init__"), None
        )
        if init:
            offset = len(init.args.args) - len(init.args.defaults)
            for i, argument in enumerate(init.args.args[offset:]):
                if argument.arg == "use_te":
                    init.args.defaults[i] = ast.Constant(False)
            args = {x.arg for x in init.args.args + init.args.kwonlyargs}
            conditions = [
                x
                for x in [
                    "use_te",
                    "plus",
                    "concrete_dropout",
                    "time_input",
                    "activation_checkpointing",
                ]
                if x in args
            ]
            checks = []
            if conditions:
                checks += ast.parse(
                    "if "
                    + " or ".join(conditions)
                    + ':\n raise NotImplementedError("当前移植仅支持普通 PyTorch GALE、无混合精度扩展及无时间条件")'
                ).body
            if "attention_type" in args:
                checks += ast.parse(
                    'if attention_type != "GALE":\n raise NotImplementedError("当前仅支持 GALE")'
                ).body
            if "structured_shape" in args:
                checks += ast.parse(
                    'if structured_shape is not None and len(structured_shape) != 2:\n raise NotImplementedError("当前仅支持二维结构网格")'
                ).body
            if "spatial_shape" in args:
                checks += ast.parse(
                    'if spatial_shape is not None and len(spatial_shape) != 2:\n raise NotImplementedError("当前仅支持二维结构网格")'
                ).body
            at = 1 if ast.get_docstring(init) else 0
            init.body[at:at] = checks
        return node


HEADER = '''# SPDX-FileCopyrightText: Copyright (c) 2023 - 2026 NVIDIA CORPORATION & AFFILIATES.
# SPDX-License-Identifier: Apache-2.0
"""{doc}；参考定义和本地修正记录见包内 Notice/physicsnemo/source.json。"""
from __future__ import annotations
import torch
from torch import nn
from einops import rearrange
from torch.distributed.tensor.placement_types import Replicate
te = None
TE_AVAILABLE = False
'''


def main(source: Path, root: Path):
    """按显式参考根和目标仓库提取；不安装或修改参考仓库。"""
    core = root / "packages/ai4e-core/abilities/modeling/modules"
    records = []

    def emit(rel, names, target, imports="", doc="中立张量计算"):
        path = source / rel
        raw = path.read_text()
        tree = ast.parse(raw)
        selected = [
            n
            for n in tree.body
            if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names
        ]
        assert {n.name for n in selected} == set(names), (rel, names)
        tree = ast.Module(body=selected, type_ignores=[])
        tree = Port().visit(tree)
        ast.fix_missing_locations(tree)
        text = HEADER.format(doc=doc) + imports + "\n" + ast.unparse(tree) + "\n"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        records.append(
            {
                "source": rel,
                "source_sha256": hashlib.sha256(raw.encode()).hexdigest(),
                "symbols": names,
                "target": str(target.relative_to(root)),
            }
        )

    emit(
        "physicsnemo/nn/module/mlp_layers.py",
        ["Mlp"],
        core / "projected_mlp.py",
        '''import itertools

def get_activation(name):
    """按显式名称构造激活，不猜测未知名称。"""
    choices = {"gelu": nn.GELU, "tanh": nn.Tanh, "relu": nn.ReLU, "silu": nn.SiLU, "sigmoid": nn.Sigmoid, "softplus": nn.Softplus, "ELU": nn.ELU}
    if name not in choices: raise ValueError(f"不支持激活 {name}")
    return choices[name]()
''',
        "可配置投影与前馈网络",
    )
    emit(
        "physicsnemo/nn/module/physics_attention.py",
        [
            "_project_input",
            "_compute_slices_from_projections",
            "PhysicsAttentionBase",
            "PhysicsAttentionIrregularMesh",
            "PhysicsAttentionStructuredMesh2D",
        ],
        core / "physics_attention.py",
        "from abc import ABC, abstractmethod\nfrom torch.autograd.profiler import record_function\n",
        "物理切片与反切片",
    )
    emit(
        "physicsnemo/nn/module/gale.py",
        [
            "_mix_self_and_cross",
            "_gale_compute_slice_attention_cross",
            "_gale_forward_impl",
            "GALE",
            "_gale_cross_init",
            "_GALEStructuredForwardMixin",
            "GALEStructuredMesh2D",
            "GALEBlock",
        ],
        core / "geometry_attention.py",
        "from .projected_mlp import Mlp\nfrom .physics_attention import PhysicsAttentionIrregularMesh, PhysicsAttentionStructuredMesh2D\n",
        "几何上下文自注意力和交叉注意力",
    )
    emit(
        "physicsnemo/models/geotransolver/context_projector.py",
        [
            "_structured_grid_to_conv_input",
            "_SliceToContextMixin",
            "ContextProjector",
            "StructuredContextProjector",
            "GlobalContextBuilder",
        ],
        core / "context_projection.py",
        "from .physics_attention import _project_input, _compute_slices_from_projections\n",
        "结构化与点云上下文投影",
    )
    p = core / "context_projection.py"
    s = p.read_text()
    s = s.replace(
        "self.local_extractors = nn.ModuleList(",
        "from .multiscale_local import MultiScaleFeatureExtractor\n            self.local_extractors = nn.ModuleList(",
    )
    p.write_text(s)
    emit(
        "physicsnemo/models/geotransolver/context_projector.py",
        ["GeometricFeatureProcessor", "MultiScaleFeatureExtractor"],
        core / "multiscale_local.py",
        "from .projected_mlp import Mlp\nfrom .context_projection import ContextProjector\nfrom ai4e_core.abilities.geometry.radius_query import BallQuery as BQWarp\n",
        "多尺度局部邻域编码",
    )
    network = root / "packages/ai4e-contrib/ability/model/geotransolver/network.py"
    emit(
        "physicsnemo/models/geotransolver/geotransolver.py",
        [
            "_normalize_dim",
            "_normalize_tensor",
            "_structured_num_tokens",
            "_flatten_for_structured",
            "GeoTransolver",
        ],
        network,
        """import math
from collections.abc import Callable, Sequence
from typing import Any, Literal
from ai4e_core.abilities.modeling.modules.projected_mlp import Mlp as _TransolverMlp
from ai4e_core.abilities.modeling.modules.context_projection import GlobalContextBuilder
from ai4e_core.abilities.modeling.modules.geometry_attention import GALEBlock
""",
        "GeoTransolver 网络组合；实际计算来自 core",
    )
    s = (
        network.read_text()
        .replace("class GeoTransolver(Module):", "class GeoTransolver(nn.Module):")
        .replace("super().__init__(meta=GeoTransolverMetaData())", "super().__init__()")
    )
    t = ast.parse(s)
    for cls in t.body:
        if not isinstance(cls, ast.ClassDef) or cls.name != "GeoTransolver":
            continue
        for f in cls.body:
            if isinstance(f, ast.FunctionDef) and f.name == "__init__":
                f.body = [
                    n
                    for n in f.body
                    if not (
                        isinstance(n, ast.Assign)
                        and (
                            "resolve_checkpointing_ratio" in ast.unparse(n)
                            or "parse_checkpointing_components" in ast.unparse(n)
                            or "self._args[" in ast.unparse(n)
                        )
                    )
                ]
            if isinstance(f, ast.FunctionDef) and f.name in [
                "_should_checkpoint_block",
                "_should_checkpoint_component",
            ]:
                f.body = ast.parse('"""本地基线关闭激活检查点。"""\nreturn False').body
            if isinstance(f, ast.FunctionDef) and f.name == "_run_checkpointed_component":
                f.body = ast.parse(
                    '"""直接调用公开子组件；保留原算术。"""\nreturn function(*inputs)'
                ).body
            if isinstance(f, ast.FunctionDef) and f.name == "_checkpoint_block":
                f.body = ast.parse(
                    '"""当前分支不支持激活检查点。"""\nraise NotImplementedError("activation checkpointing")'
                ).body
    ast.fix_missing_locations(t)
    s = ast.unparse(t) + "\n"
    network.write_text("# SPDX-License-Identifier: Apache-2.0\n" + s)
    package = network.parent
    (package / "__init__.py").write_text(
        '"""GeoTransolver 完整网络入口。"""\nfrom .network import GeoTransolver\n\n__all__ = ["GeoTransolver"]\n'
    )
    meta = {
        "revision": REVISION,
        "records": records,
        "changes": [
            "imports and framework metadata removed",
            "plain torch GALE/2D supported; other options rejected",
            "Chinese docstrings added",
            "radius query relocated with equivalent torch fallback",
        ],
    }
    for base in [root / "packages/ai4e-core/Notice/physicsnemo", package]:
        base.mkdir(parents=True, exist_ok=True)
        (base / "LICENSE").write_text(
            (source / "LICENSE.txt").read_text()
            if (source / "LICENSE.txt").exists()
            else (source / "LICENSE").read_text()
        )
        (base / "source.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")
    (package / "source.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--root", type=Path, default=Path.cwd())
    a = p.parse_args()
    main(a.source, a.root)
