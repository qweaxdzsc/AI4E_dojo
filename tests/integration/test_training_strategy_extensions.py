"""本地部件和训练策略：真实更新、恢复、安装复制及结果读回。"""

import copy
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import torch
import yaml

from tests.integration.test_wdno_recipe import fixture, run_script
from tests.integration.test_wdno_recipe import installed as installed_wdno  # noqa: F401

ROOT = Path(__file__).resolve().parents[2]


def test_local_model_block_changes_forward_and_resumes(tmp_path):
    from ai4e_contrib.ability.model.abupt.inference import InferenceContext
    from ai4e_core.abilities.training.loop import fit
    from tests.integration.test_abupt_multidomain import inputs, make_model, specs
    from tests.integration.test_train_loop import Run

    spec = importlib.util.spec_from_file_location(
        "block_variant", ROOT / "examples/recipe_extensions/model_block/variants.py"
    )
    variant = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(variant)
    data = specs()
    torch.manual_seed(7)
    original = make_model(data)
    torch.manual_seed(7)
    model = variant.construct(
        data_specs=data,
        dim=24,
        num_heads=3,
        geometry_depth=1,
        blocks="psc",
        num_domain_decoder_blocks={d: 1 for d in data["domains"]},
    )
    assert list(original.state_dict()) == list(model.state_dict())
    batch = inputs(data, queries=False)
    old = original(**batch)[0]
    new = model(**batch)[0]
    assert any(not torch.equal(old[key], new[key]) for key in old)
    initial = copy.deepcopy(model.state_dict())
    with torch.no_grad():
        model.eval()
        context = InferenceContext(model, batch, preparation_id="variant")
    full = copy.deepcopy(model)

    def step(current, values):
        return {"loss": sum(v.square().mean() for v in current(**values)[0].values())}

    def train(current, directory, epochs, resume=None):
        return fit(
            current,
            torch.optim.Adam(current.parameters(), lr=0.001),
            lambda e: [batch],
            step,
            lambda: {"loss": 1.0},
            Run(directory),
            config={"max_epochs": epochs, "resume": resume},
            contract={"variant": "silu"},
        )

    train(full, tmp_path / "full", 2)
    train(model, tmp_path / "first", 1)
    assert any(not torch.equal(initial[k], model.state_dict()[k]) for k in initial)
    model.eval()
    with torch.no_grad(), pytest.raises(ValueError):
        context.query({"surface": torch.rand(1, 2, 3)}, preparation_id="variant")
    checkpoint = tmp_path / "first/checkpoints/latest.pt"
    # Run 创建的实际目录由 writer 固定在传入目录中。
    if not checkpoint.exists():
        checkpoint = next((tmp_path / "first").rglob("latest.pt"))
    train(model, tmp_path / "resume", 2, str(checkpoint))
    for key, value in full.state_dict().items():
        torch.testing.assert_close(value, model.state_dict()[key], rtol=0, atol=0)
    with torch.no_grad():
        prediction = model.eval()(**batch)[0]
        path = tmp_path / "prediction.pt"
        torch.save(prediction, path)
        for key, value in prediction.items():
            torch.testing.assert_close(
                torch.load(path, weights_only=True)[key], value, rtol=0, atol=0
            )


def test_installed_training_strategy_resume_and_fixed_readback(tmp_path, installed_wdno):  # noqa: F811
    installed = installed_wdno
    from tools.verification.training_execution import _equal

    case = tmp_path / "case"
    cfg = fixture(case)
    for name in ("variant_training.py", "variants.py", "configure_variant.py"):
        shutil.copy2(ROOT / "examples/recipe_extensions/wdno" / name, case / name)
    (case / "config.yaml").write_text(yaml.safe_dump(cfg))
    subprocess.run([sys.executable, str(case / "configure_variant.py")], check=True)
    configured = yaml.safe_load((case / "config.yaml").read_text())
    assert configured["inputs"]["rawprep"] == cfg["inputs"]["rawprep"]
    assert configured["components"]["update"] == "variant_training.update"
    # 真正消费配置脚本产出的组件组合，仅把验收预算和输出位置缩小。
    configured["run_root"], configured["data_root"] = cfg["run_root"], cfg["data_root"]
    configured["train"]["updates"] = 2
    cfg = configured
    cfg["components"].update(
        optimizer="variant_training.optimizer",
        scheduler="variant_training.scheduler",
        update="variant_training.update",
        derived="variants.energy",
    )
    summary = run_script(case, "pipeline", cfg, installed)
    reports = summary["reports"]
    first = torch.load(reports["train"]["checkpoint"], weights_only=False)
    assert set(first["contract"]["strategies"]) == {"optimizer", "scheduler", "update"}
    assert first["optimizer"]["param_groups"][0]["weight_decay"] == 0.01
    for stage in ("train", "infer"):
        cfg["inputs"][stage].update(
            preparation=reports["trainprep"]["train"],
            validation=reports["trainprep"]["validation"],
            test=reports["trainprep"]["test"],
        )
    cfg["inputs"]["train"]["resume"] = reports["train"]["checkpoint"]
    cfg["train"]["updates"] = 3
    resumed = run_script(case, "train", cfg, installed)
    cfg["inputs"]["train"]["resume"] = None
    full = run_script(case, "train", cfg, installed)
    a = torch.load(resumed["reports"]["train"]["checkpoint"], weights_only=False)
    b = torch.load(full["reports"]["train"]["checkpoint"], weights_only=False)
    for key in (
        "model",
        "optimizer",
        "scheduler",
        "ema",
        "history",
        "stream",
        "torch_rng",
        "contract",
    ):
        _equal(a[key], b[key])
    # 固定权重推理也不应导入仅在训练时使用的局部策略。
    cfg["inputs"]["infer"]["checkpoint"] = reports["train"]["checkpoint"]
    cfg["components"]["optimizer"] = "nonexistent.optimizer"
    inferred = run_script(case, "infer", cfg, installed)
    assert inferred["reports"]["infer"]["test"]
    # 固定结果的 post 不重新构建模型或训练函数。
    cfg["inputs"]["post"] = reports["infer"]
    cfg["components"]["network"] = "nonexistent.network"
    cfg["components"]["optimizer"] = "nonexistent.optimizer"
    post = run_script(case, "post", cfg, installed)
    assert post["reports"]["post"] == reports["post"]


def test_installed_copied_block_recipe_resume_and_post(tmp_path, installed_wdno, monkeypatch):  # noqa: F811
    from tests.integration.test_recipe_explicit_equivalence import case
    from tests.integration.test_recipe_extensions import script
    from tools.verification.training_execution import _equal

    monkeypatch.setenv("PYTHONPATH", str(installed_wdno))
    folder, cfg = case(tmp_path, "shapenet_car_abupt")
    shutil.copy2(
        ROOT / "examples/recipe_extensions/model_block/variants.py", folder / "variants.py"
    )
    cfg["components"]["model"] = "variants"
    cfg["pipeline"]["stages"] = ["trainprep", "train", "infer", "post"]

    def execute(name, entry="pipeline.py"):
        cfg["run_root"] = str(tmp_path / name)
        (folder / "config.yaml").write_text(yaml.safe_dump(cfg))
        result = script(folder, entry)
        assert result.returncode == 0, result.stdout + result.stderr
        directory = max(Path(cfg["run_root"]).iterdir(), key=lambda p: p.stat().st_mtime_ns)
        return directory, json.loads((directory / "summary.json").read_text())

    # 固定两轮总计划，捕获第一轮完整边界；不能改变余弦调度总目标来模拟中断。
    (folder / "capture.py").write_text("""from pathlib import Path
import shutil
from pipeline import pipeline
from configuration import load_configuration
from ai4e_core import run
from ai4e_core.run import TrainingRun
original = TrainingRun.checkpoint
def checkpoint(self, label, payload):
    result = original(self, label, payload)
    if label == "latest" and payload["epoch"] == 1:
        shutil.copyfile(result, Path(__file__).parent / "epoch1.pt")
    return result
TrainingRun.checkpoint = checkpoint
raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
""")
    full, summary = execute("full", "capture.py")
    cfg["inputs"]["train"]["resume"] = str(folder / "epoch1.pt")
    cfg["inputs"]["train"]["preparation"] = str(full / "artifacts/preparation.json")
    resumed, _ = execute("resumed", "train.py")
    a, b = [torch.load(p / "checkpoints/last.pt", weights_only=False) for p in (full, resumed)]
    for key in ("model", "optimizer", "scheduler", "ema", "updates"):
        _equal(a[key], b[key])
    assert "variants" in json.dumps(a["contract"])
    cfg["inputs"]["post"]["results"] = str(full / "artifacts/inference-results.json")
    # 移走权重证明 post 只读已保存预测；不改来源文件使固定资产仍可核验。
    os.rename(full / "checkpoints", full / "saved-checkpoints")
    _, result = execute("post", "post.py")
    assert not result["failed"] and summary["reports"]["infer"]
