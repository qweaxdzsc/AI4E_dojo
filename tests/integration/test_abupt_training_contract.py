"""新多域输入的训练、声明式评估与旧格式拒绝。"""

import copy

import pytest
import torch

from ai4e_contrib.ability.model.abupt.model import predict
from ai4e_core.abilities.constraint.supervised import supervised
from ai4e_core.abilities.eval.evaluation import evaluate
from ai4e_core.abilities.training.checkpoint import restore
from ai4e_core.applications.aero_cfd.trainprep.normalization import Normalization
from tests.integration.test_abupt_multidomain import inputs, make_model


def test_query_supervision_and_declared_evaluation():
    model = make_model()
    data = inputs(batch=2)
    terms = [
        {
            "name": "query",
            "prediction": "query_surface_value",
            "target": "truth",
            "normalization": "value",
            "weight": 1,
        }
    ]
    targets = {"truth": torch.zeros(2, 5, 1)}
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.01)
    before = copy.deepcopy(model.state_dict())
    loss = supervised(predict(model, data), targets, terms)["loss"]
    loss.backward()
    optimizer.step()
    assert any(not torch.equal(before[k], v) for k, v in model.state_dict().items())
    norm = Normalization(
        {"version": 1, "fields": {"value": {"method": "identity", "parameters": {}}}}
    )
    report = evaluate(model, [{"inputs": data, "targets": targets}], predict, terms, norm)
    assert set(report["metrics"]) == {
        "query_surface_value/mse",
        "query_surface_value/mae",
        "query_surface_value/relative_l2",
    }


def test_old_checkpoint_rejected(tmp_path):
    model = make_model()
    optimizer = torch.optim.AdamW(model.parameters())
    path = tmp_path / "old.pt"
    torch.save({"version": 1, "contract": {}, "model": model.state_dict()}, path)
    with pytest.raises(ValueError, match="冲突"):
        restore(path, model, optimizer, contract={})


@pytest.mark.parametrize("change", ["order", "features", "conditions"])
def test_layout_conflict_rejected_before_restore(tmp_path, change):
    from ai4e_core.abilities.training.checkpoint import capture
    from tests.integration.test_abupt_multidomain import specs

    data = specs()
    model = make_model(data)
    optimizer = torch.optim.AdamW(model.parameters())
    path = tmp_path / "new.pt"
    torch.save(
        capture(
            model,
            optimizer,
            epoch=1,
            updates=1,
            best=1,
            contract={"layout": model.layout.signature},
        ),
        path,
    )
    if change == "order":
        data["domains"] = dict(reversed(list(data["domains"].items())))
    if change == "features":
        data["domains"]["surface"]["feature_dim"] = {"sdf": 1}
    if change == "conditions":
        data["conditioning_dims"] = {"design": 2}
    changed = make_model(data)
    before = copy.deepcopy(changed.state_dict())
    with pytest.raises(ValueError, match="语义冲突"):
        restore(
            path,
            changed,
            torch.optim.AdamW(changed.parameters()),
            contract={"layout": changed.layout.signature},
        )
    for k, v in changed.state_dict().items():
        torch.testing.assert_close(v, before[k])


def test_relative_loss_is_mean_of_samples():
    predictions = {"p": torch.tensor([[[2.0]], [[20.0]]])}
    targets = {"truth": torch.tensor([[[1.0]], [[2.0]]])}
    terms = [
        {
            "name": "p",
            "prediction": "p",
            "target": "truth",
            "normalization": "p",
            "loss": "relative_l2",
        }
    ]
    norm = Normalization({"version": 1, "fields": {"p": {"method": "identity", "parameters": {}}}})
    report = evaluate(
        torch.nn.Linear(1, 1),
        [{"inputs": predictions, "targets": targets}],
        lambda _, x: x,
        terms,
        norm,
    )
    assert report["loss"] == pytest.approx(5.0)
