"""贡献包正式网络验收：依赖缺失应失败，不使用替身或跳过。"""

import torch

from ai4e_contrib.ability.model.abupt.model import construct, predict
from tests.integration.test_abupt_multidomain import inputs as make_inputs
from tests.integration.test_abupt_multidomain import specs


def test_real_network_fit():
    torch.manual_seed(7)
    device = torch.device("cpu")
    model = construct(
        data_specs=specs(),
        dim=24,
        geometry_depth=1,
        num_heads=3,
        blocks="psc",
        num_domain_decoder_blocks={"surface": 1, "volume": 1},
        radius=9.0,
    ).to(device)
    inputs = make_inputs(queries=False)
    assert next(model.parameters()).device.type == device.type
    assert inputs["geometry_position"].device.type == device.type
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.003)
    initial = None
    for _ in range(1000):
        optimizer.zero_grad()
        output = predict(model, inputs)
        loss = sum((value - 0.25).square().mean() for value in output.values())
        if initial is None:
            initial = loss.detach().item()
        assert torch.isfinite(loss)
        loss.backward()
        optimizer.step()
        if loss.item() < initial * 0.1:
            break
    assert loss.item() < initial * 0.1


def test_real_network_epoch_resume(tmp_path):
    from ai4e_core.abilities.training.loop import fit
    from tests.integration.test_train_loop import Run

    torch.manual_seed(19)
    device = torch.device("cpu")
    inputs = make_inputs(queries=False)

    def execute(root, epochs, resume=None):
        torch.manual_seed(17)
        model = construct(
            data_specs=specs(),
            dim=24,
            geometry_depth=1,
            num_heads=3,
            blocks="psc",
            num_domain_decoder_blocks={"surface": 1, "volume": 1},
            radius=9.0,
        ).to(device)
        optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
        run = Run(root)

        def step(network, batch):
            return {
                "loss": sum(value.square().mean() for value in predict(network, batch).values())
            }

        def evaluation():
            with torch.no_grad():
                return {"loss": step(model, inputs)["loss"].item()}

        report = fit(
            model,
            optimizer,
            lambda _: iter([inputs]),
            step,
            evaluation,
            run,
            config={"max_epochs": epochs, "resume": resume},
            contract={"model": "actual-abupt"},
        )
        return model, run, report

    full, _, full_report = execute(tmp_path / "full", 2)
    _, one, _ = execute(tmp_path / "one", 1)
    resumed, _, resumed_report = execute(
        tmp_path / "resumed", 2, one.writer.run_dir / "checkpoints/latest.pt"
    )
    for name, value in full.state_dict().items():
        torch.testing.assert_close(value, resumed.state_dict()[name], rtol=1e-5, atol=1e-6)
    assert abs(full_report["history"][-1]["loss"] - resumed_report["history"][-1]["loss"]) < 1e-6
