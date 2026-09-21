"""固定结果、用户新增输出和下游消费，禁止隐式网络调用。"""

import json
from pathlib import Path

import numpy as np

from ai4e_contrib.application.spatiotemporal_pde.pcno.post import metrics
from ai4e_core.abilities.data.save.array_manifest import save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.applications.spatiotemporal_pde.window_results import analyze_windows, extend_windows


def test_fixed_results_and_speed_consumption(tmp_path):
    x, y = np.meshgrid(np.arange(16), np.arange(16), indexing="ij")
    field = np.stack((x, -y, x + y, np.ones_like(x)), axis=-1).astype("float32")
    truth = np.broadcast_to(field, (4, *field.shape)).copy()
    arrays = {
        name: truth.copy() for name in ("truth", "initial", "persistence", "supervised", "physics")
    }
    path = save_arrays(
        tmp_path / "original", arrays, kind="field-window-result-v1", metadata={"id": "case"}
    )
    original = (tmp_path / "original" / "physics.npy").read_bytes()
    source = tmp_path / "results.json"
    save_json(source, {"kind": "field-window-list-v1", "windows": [path]})
    extended = extend_windows(
        source,
        lambda a: {"speed": np.linalg.norm(a["physics"][..., :2], axis=-1)},
        tmp_path / "derived",
    )
    report = json.loads(Path(analyze_windows(extended, metrics, tmp_path / "post")).read_text())
    m = report["results"][0]["metrics"]
    assert m["physics"]["divergence_rms"] == 0
    assert np.asarray(m["physics"]["fluid"]["rmse"]).max() == 0
    assert m["derived_speed"]["mean"] > 0
    assert (tmp_path / "original" / "physics.npy").read_bytes() == original
