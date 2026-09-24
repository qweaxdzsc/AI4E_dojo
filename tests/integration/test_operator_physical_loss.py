"""最大值原理约束的尺度、有效域及两种算子梯度；不执行优化更新。"""

import pytest
import torch

from ai4e_contrib.application.operator_learning.binding import OperatorField, build_network
from ai4e_contrib.application.operator_learning.objectives import FieldObjective, physical_terms


def test_physical_scale_mask_and_independent_formula():
    prediction = torch.tensor([[[[-2.0], [0.0]], [[1.0], [-100.0]]]], requires_grad=True)
    target = torch.zeros_like(prediction)
    valid = torch.tensor([[[True, True], [True, False]]])
    terms = physical_terms(prediction, target, valid, mean=[1.0], scale=[2.0])
    # 物理预测为 -3,1,3；归一化违约平方为2.25,0,0，最后一个无效点不参与。
    torch.testing.assert_close(terms["nonnegative"], torch.tensor(0.75))
    terms["nonnegative"].backward()
    torch.testing.assert_close(prediction.grad.flatten(), torch.tensor([-1.0, 0, 0, 0]))
    with pytest.raises(ValueError, match="有效域"):
        physical_terms(prediction, target, torch.zeros_like(valid), mean=0, scale=1)
    with pytest.raises(ValueError, match="尺度"):
        physical_terms(prediction, target, valid, mean=0, scale=0)


def test_unconstrained_objective_rejects_broadcasting():
    item = {
        "input": torch.ones(1, 3, 1),
        "target": torch.zeros(1, 3, 3),
        "valid": torch.ones(1, 3, dtype=torch.bool),
    }
    with pytest.raises(ValueError, match="广播"):
        FieldObjective({})(lambda x, *args: x, item)


@pytest.mark.parametrize("family", ["deeponet", "fno"])
def test_same_constraint_reaches_two_model_parameter_sets(family):
    torch.manual_seed(13)
    params = (
        {"latent_dim": 4, "sensor_stride": 2, "branch_hidden": [6], "trunk_hidden": [6]}
        if family == "deeponet"
        else {"modes": [2, 2], "width": 4, "depth": 1, "padding": [1, 1], "projection_hidden": []}
    )
    definition = {
        "family": family,
        "spatial_dims": 2,
        "grid_shape": [5, 5],
        "in_channels": 3,
        "out_channels": 1,
        "history": 1,
        "parameters": params,
    }
    model = OperatorField(build_network(definition), definition)
    item = {
        "input": torch.randn(2, 5, 5, 3),
        "coordinates": torch.rand(2, 5, 5, 2),
        "target": torch.zeros(2, 5, 5, 1),
        "valid": torch.ones(2, 5, 5, dtype=torch.bool),
    }
    stats = {"target": {"mean": [-10.0], "scale": [1.0]}}
    baseline = FieldObjective(stats)(model, item)
    constrained = FieldObjective(stats, physical_weight=0.1)(model, item)
    delta = constrained - baseline
    assert delta.item() > 0
    delta.backward()
    gradients = [p.grad for p in model.parameters() if p.grad is not None]
    assert gradients and all(torch.isfinite(g).all() for g in gradients)
    assert sum(float(g.abs().sum()) for g in gradients) > 0
