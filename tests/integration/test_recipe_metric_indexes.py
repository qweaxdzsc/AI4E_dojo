"""指标比较身份随真值变化，不随模型预测变化。"""

import json

import numpy as np

from ai4e_contrib.ability.eval.safediffcon.control import metrics
from ai4e_contrib.application.pde_control.safediffcon.handoff import register_metrics
from ai4e_core.abilities.data.save.array_manifest import save_arrays
from ai4e_core.run.writer import RunWriter


def test_control_metrics_index_truth_and_reduction(tmp_path):
    rows = []
    for name, predicted, truth in (("a", 0.1, 0.0), ("b", 0.2, 0.0), ("c", 0.2, 0.3)):
        target = np.full((2, 11, 128), truth)
        response = np.full_like(target, predicted)
        reference = save_arrays(tmp_path / name / "data", {
            "ids": np.arange(2), "response": response, "target": target,
            "paper_target": target,
        }, kind="control_results_v1", metadata={"case": "burgers"})
        writer = RunWriter.create(tmp_path / name / "run")
        register_metrics(writer, reference, metrics(response, target, case="burgers"), evaluate=metrics)
        rows.append(json.loads((writer.run_dir / "artifacts/metrics.json").read_text())["items"])
    assert rows[0]["post/J"]["value"] != rows[1]["post/J"]["value"]
    assert rows[0]["post/J"]["semantics"] == rows[1]["post/J"]["semantics"]
    assert rows[1]["post/J"]["semantics"] != rows[2]["post/J"]["semantics"]
    assert rows[0]["post/R_point"]["semantics"]["unit"] == "1"
    assert len(rows[0]["post/J"]["assets"]) == 2
