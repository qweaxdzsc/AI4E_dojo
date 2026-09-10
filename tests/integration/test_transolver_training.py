"""C1—C4：真实模型算术、参数分组、描述契约和恢复历史。"""

import importlib.util
import sys
from pathlib import Path

import pytest
import torch

from ai4e_contrib.ability.model.transolver3.model import construct, predict
from ai4e_core.abilities.data.validate.fingerprint import fingerprint
from ai4e_core.abilities.training.optimization import parameter_groups, update
from ai4e_spec.components.model import describe_model
from tools.verification.transolver3.compare import require

ROOT = Path(__file__).resolve().parents[2]


def reference_module(filename):
    """仅验收工具动态读取参考算法，正式包没有这个依赖。"""
    path = ROOT.parent / "Transolver-3/models" / filename
    if not path.is_file():
        pytest.skip("缺少只读参考源码")
    spec = importlib.util.spec_from_file_location("transolver_reference_" + path.stem, path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT.parent / "Transolver-3"))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return module


@pytest.mark.parametrize("checkpointing", [False, True])
def test_model_gradient_update(checkpointing):
    """C1/C3：原算法和 Dojo 独立初始化，同批次梯度及非零衰减更新逐元素比较。"""
    reference = reference_module("Transolver_chunk_opt_matrix_mul.py")
    parameters = {
        "n_hidden": 16,
        "n_layers": 2,
        "n_head": 4,
        "mlp_ratio": 2,
        "slice_num": 4,
        "space_dim": 12,
        "fun_dim": 0,
        "out_dim": 4,
        "unified_pos": False,
    }
    torch.manual_seed(2)
    expected = reference.Model(**parameters)
    torch.manual_seed(2)
    actual = construct(**parameters, gradient_checkpointing=checkpointing)
    assert list(actual.state_dict()) == list(expected.state_dict())
    assert describe_model(construct, actual)["outputs"] == ["fields"]
    generator = torch.Generator().manual_seed(7)
    x = torch.randn(1, 17, 12, generator=generator)
    y = torch.randn(1, 17, 4, generator=generator)
    expected_optimizer = torch.optim.AdamW(expected.parameters(), lr=0.001, weight_decay=0.1)
    actual_optimizer = torch.optim.AdamW(
        parameter_groups(actual, weight_decay=0.1, policy="all"), lr=0.001, weight_decay=0.1
    )
    loss = (expected([x], use_checkpoint=checkpointing)[0] - y).square().mean()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(expected.parameters(), 1.0)
    expected_optimizer.step()
    result, _ = update(
        actual,
        actual_optimizer,
        lambda model, _: {"loss": (predict(model, {"features": x})["fields"] - y).square().mean()},
        None,
    )
    require(result["loss"].detach().numpy(), loss.detach().numpy(), identity="loss")
    for (key, left), (_, right) in zip(
        actual.named_parameters(), expected.named_parameters(), strict=True
    ):
        require(left.detach().numpy(), right.detach().numpy(), identity=f"parameter/{key}")
        if left.grad is not None:
            require(left.grad.numpy(), right.grad.numpy(), identity=f"gradient/{key}")


def test_singleton_stride_fingerprint():
    """单点抽稀张量可计算摘要，形状与类型仍参与摘要。"""
    values = torch.arange(8, dtype=torch.long)[1::7]
    assert values.stride() == (7,)
    assert fingerprint(values) == fingerprint(torch.tensor([1], dtype=torch.long))
    assert fingerprint(values) != fingerprint(values.float())
    assert fingerprint(torch.ones(1, dtype=torch.bfloat16))


def test_resume_keeps_previous_best_when_validation_worsens(tmp_path):
    """C4：新运行目录恢复后没有改善，最佳产物仍对应恢复前选择。"""
    from copy import deepcopy

    from ai4e_core.abilities.training.checkpoint import capture, restore_selection
    from ai4e_core.abilities.training.loop import fit

    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
    state = capture(model, optimizer, epoch=1, updates=1, best=0.1, contract={})
    state["history"] = [{"epoch": 1, "evaluation": {"loss": 0.1}}]
    path = tmp_path / "epoch-1.pt"
    torch.save(state, path)
    saved = {}

    class Run:
        def checkpoint(self, key, value):
            saved[key] = deepcopy(value)

    fit(
        model,
        optimizer,
        lambda _: [None],
        lambda network, _: {"loss": network(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 0.2},
        Run(),
        config={"resume": str(path), "max_epochs": 2, "restore_history": True},
        contract={},
        preserve_selection=True,
    )
    assert saved["best"]["epoch"] == 1 and saved["last"]["epoch"] == 2
    assert saved["last"]["selection"]["epoch"] == 1
    for key, value in state["model"].items():
        torch.testing.assert_close(saved["best"]["model"][key], value, rtol=0, atol=0)
    assert restore_selection(saved["last"], tmp_path / "missing.pt")["epoch"] == 1
    incomplete = deepcopy(saved["last"])
    incomplete.pop("selection")
    with pytest.raises(ValueError, match="缺少"):
        restore_selection(incomplete, tmp_path / "missing.pt")


@pytest.mark.parametrize("best_on_equal", [False, True])
def test_best_tie_policy_and_legacy_resume(tmp_path, best_on_equal):
    """C4：相等选优策略决定保存轮次，历史相等不能猜测最新即最佳。"""
    from copy import deepcopy

    from ai4e_core.abilities.training.checkpoint import restore_selection
    from ai4e_core.abilities.training.loop import fit

    model = torch.nn.Linear(1, 1)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
    saved = {}

    class Run:
        def checkpoint(self, key, value):
            saved[key] = deepcopy(value)

    fit(
        model,
        optimizer,
        lambda _: [None],
        lambda network, _: {"loss": network(torch.ones(1, 1)).square().mean()},
        lambda: {"loss": 0.1},
        Run(),
        config={"max_epochs": 2, "best_on_equal": best_on_equal, "restore_history": True},
        contract={},
        preserve_selection=True,
    )
    assert saved["best"]["epoch"] == (2 if best_on_equal else 1)
    legacy = deepcopy(saved["last"])
    legacy.pop("selection")
    if best_on_equal:
        assert restore_selection(legacy, tmp_path / "last.pt", best_on_equal=True)["epoch"] == 2
    else:
        with pytest.raises(ValueError, match="缺少"):
            restore_selection(legacy, tmp_path / "last.pt")
        torch.save(saved["best"], tmp_path / "best.pt")
        assert restore_selection(legacy, tmp_path / "last.pt")["epoch"] == 1
