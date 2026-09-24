"""经典网络的真实组合与依赖方向门禁；不执行训练或优化器更新。"""

import ast
import copy
import importlib.util
from pathlib import Path

import pytest
import torch
from torch import nn

from ai4e_core.abilities.modeling.models.cnn import CNN2d
from ai4e_core.abilities.modeling.models.gnn import GraphNetwork
from ai4e_core.abilities.modeling.models.mlp import MLP
from ai4e_core.abilities.modeling.models.resnet import ResNet2d
from ai4e_core.abilities.modeling.models.rnn import RNN
from ai4e_core.abilities.modeling.models.transformer import PatchTransformer
from ai4e_core.abilities.modeling.models.unet import UNet2d
from ai4e_core.abilities.modeling.modules.feed_forward import FeedForward

ROOT = Path(__file__).resolve().parents[2]
MODELING = ROOT / "packages/ai4e-core/abilities/modeling"
MODULES = (
    "attention",
    "convolution",
    "feed_forward",
    "graph_encoding",
    "graph_message_passing",
    "patch_embedding",
    "patch_reconstruction",
    "recurrent",
    "residual",
    "skip_fusion",
    "spatial_resampling",
    "transformer",
)
MODELS = ("mlp", "rnn", "cnn", "resnet", "unet", "transformer", "gnn")


def _imports(path, package):
    for node in ast.walk(ast.parse(path.read_text())):
        if isinstance(node, ast.Import):
            yield from (alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            name = "." * node.level + (node.module or "")
            base = importlib.util.resolve_name(name, package) if node.level else name
            yield base
            yield from (base + "." + alias.name for alias in node.names)


def test_new_modeling_dependencies_flow_toward_components():
    groups = {
        "modules": [MODELING / "modules" / (name + ".py") for name in MODULES],
        "stages": sorted((MODELING / "stages").glob("*.py")),
        "models": [MODELING / "models" / (name + ".py") for name in MODELS],
    }
    for layer, paths in groups.items():
        forbidden = [
            "ai4e_contrib",
            "ai4e_task",
            "ai4e_server",
            "ai4e_viz",
            "recipes",
            "ai4e_core.applications",
            "ai4e_core.run",
            "ai4e_core.abilities.training",
        ]
        if layer == "modules":
            forbidden += [
                "ai4e_core.abilities.modeling.stages",
                "ai4e_core.abilities.modeling.models",
            ]
        if layer == "stages":
            forbidden += ["ai4e_core.abilities.modeling.models"]
        for path in paths:
            for dependency in _imports(path, "ai4e_core.abilities.modeling." + layer):
                assert not any(
                    dependency == prefix or dependency.startswith(prefix + ".")
                    for prefix in forbidden
                ), (path, dependency)


@pytest.fixture(autouse=True)
def small_threads():
    previous = torch.get_num_threads()
    torch.set_num_threads(2)
    yield
    torch.set_num_threads(previous)


def _case(family):
    if family == "mlp":
        return MLP(3, 2, (4,)), (torch.randn(2, 5, 3),), ("feed_forward",)
    if family == "rnn":
        return (
            RNN(3, 2, 4, 1),
            (torch.randn(2, 5, 3),),
            ("input_mapping", "recurrent_stage", "output_mapping"),
        )
    if family == "transformer":
        return (
            PatchTransformer(
                3, 2, patch_shape=(2, 2), dim=8, num_heads=2, num_layers=2, feed_forward_dim=12
            ),
            (torch.randn(2, 5, 7, 3),),
            ("embedding", "encoder", "reconstruction", "position_encoding"),
        )
    if family == "gnn":
        return (
            GraphNetwork(3, 2, 2, hidden_dim=4, processor_layers=2),
            (torch.randn(4, 3), torch.randn(4, 2), torch.tensor([[0, 1, 2, 3], [1, 2, 3, 0]])),
            ("encoder", "processor", "readout"),
        )
    factories = {
        "cnn": lambda: CNN2d(3, 2, hidden_channels=4, hidden_layers=2),
        "resnet": lambda: ResNet2d(3, 2, base_channels=2),
        "unet": lambda: UNet2d(3, 2, base_channels=2, levels=2),
    }
    slots = (
        ("encoder", "bottleneck", "decoder", "head") if family == "unet" else ("encoder", "head")
    )
    return factories[family](), (torch.randn(2, 3, 17, 19),), slots


@pytest.mark.parametrize("family,expected_count", [("mlp", 1), ("transformer", 2), ("gnn", 7)])
def test_shared_feed_forward_is_actually_executed(family, expected_count):
    model, args, _ = _case(family)
    shared = [part for part in model.modules() if type(part) is FeedForward]
    assert len(shared) == expected_count
    called = []
    handles = [
        part.register_forward_hook(lambda module, _, __: called.append(id(module)))
        for part in shared
    ]
    try:
        model.eval()(*args)
    finally:
        for handle in handles:
            handle.remove()
    assert sorted(called) == sorted(map(id, shared))


class TracedReplacement(nn.Module):
    """保持各子结构本地签名，不引入全局组件协议。"""

    def __init__(self, module):
        super().__init__()
        self.implementation = copy.deepcopy(module)
        self.calls = 0

    def forward(self, *args, **kwargs):
        self.calls += 1
        return self.implementation(*args, **kwargs)


@pytest.mark.parametrize("family", MODELS)
def test_replacement_slots_execute_and_register_state(family):
    model, args, slots = _case(family)
    model.eval()
    with torch.no_grad():
        expected = model(*args)
    removed = {id(parameter) for slot in slots for parameter in getattr(model, slot).parameters()}
    replacements = {slot: TracedReplacement(getattr(model, slot)) for slot in slots}
    for slot, replacement in replacements.items():
        setattr(model, slot, replacement)
    model.eval()
    with torch.no_grad():
        actual = model(*args)
    torch.testing.assert_close(actual, expected)
    assert all(part.calls == 1 for part in replacements.values())
    assert removed.isdisjoint(map(id, model.parameters()))
    registered = dict(model.named_parameters())
    state = model.state_dict()
    for slot, part in replacements.items():
        for name, parameter in part.named_parameters():
            assert registered[slot + "." + name] is parameter
            assert slot + "." + name in state
    restored = copy.deepcopy(model)
    restored.load_state_dict(state, strict=True)
    with torch.no_grad():
        torch.testing.assert_close(restored(*args), actual)


@pytest.mark.parametrize("case", ("darcy", "shapenet_volume", "double_cylinder"))
def test_recipe_delegates_updates_to_shared_training(case):
    path = ROOT / "recipes/classic_networks" / case / "train.py"
    tree = ast.parse(path.read_text())
    shared = "ai4e_core.applications.base.iteration_training"
    aliases = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module == shared
        for alias in node.names
        if alias.name == "train_model"
    }
    calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
    assert (
        len([node for node in calls if isinstance(node.func, ast.Name) and node.func.id in aliases])
        == 1
    )
    assert not any(
        isinstance(node.func, ast.Attribute) and node.func.attr in {"backward", "step", "zero_grad"}
        for node in calls
    )
    assert not any(isinstance(node, (ast.For, ast.AsyncFor, ast.While)) for node in ast.walk(tree))


def test_contrib_binding_contains_no_training_engine():
    directory = ROOT / "packages/ai4e-contrib/application/classic_networks"
    for path in directory.glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in {"backward", "zero_grad", "step"}, path
