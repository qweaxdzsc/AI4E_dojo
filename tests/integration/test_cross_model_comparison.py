"""完整点身份、加权指标和不可定义相对误差的门禁。"""

import numpy as np
import pytest

from ai4e_core.abilities.eval.physical import PhysicalMetrics
from ai4e_core.applications.aero_cfd.post.comparison import align


def test_alignment_rejects_subsets_and_duplicates():
    np.testing.assert_array_equal(align([2, 0, 1], [1, 2, 0]), [1, 2, 0])
    for a, b in [([0, 1], [0]), ([0, 0], [0, 1]), ([0, 1], [0, 2])]:
        with pytest.raises(ValueError):
            align(a, b)


def test_weighted_elements_and_zero_norm():
    metric = PhysicalMetrics()
    metric.update("p", np.ones((1, 1)), np.zeros((1, 1)))
    metric.update("p", np.full((3, 1), 2), np.zeros((3, 1)))
    output = metric.finalize()["p"]
    assert output["mse"] == 13 / 4 and output["mae"] == 7 / 4
    assert output["relative_l2"] is None
    with pytest.raises(ValueError, match="非有限"):
        metric.update("p", np.array([[np.nan]]), np.ones((1, 1)))


def test_vector_magnitude_is_independent():
    metric = PhysicalMetrics()
    metric.update("v", np.array([[3, 4, 0]]), np.array([[-3, 4, 0]]))
    result = metric.finalize()
    assert result["v"]["mse"] == 12 and result["v/magnitude"]["mse"] == 0


def test_independent_runs_and_partial_failure(tmp_path):
    import json

    import torch

    from ai4e_core.abilities.data.validate.fingerprint import fingerprint
    from ai4e_core.applications.aero_cfd.post.comparison import compare

    paths = []
    for model in ("custom_a", "custom_b"):
        root = tmp_path / model
        root.mkdir()
        protocol = {
            "dataset": "same",
            "samples": ["s1", "s2"],
            "split": "test",
            "execution": {"device": "cpu"},
            "weights": model,
            "preparation": model,
            "model": model,
        }
        protocol["digest"] = fingerprint(protocol)
        results = []
        for name in protocol["samples"]:
            folder = root / name
            folder.mkdir()
            arrays = {
                "pos": torch.tensor([[0.0, 0, 0], [1, 0, 0]]),
                "ids": torch.arange(2),
                "p.truth": torch.ones(2, 1),
                "p.prediction": torch.full((2, 1), 2.0),
            }
            if model == "custom_b":
                arrays = {k: torch.flip(v, [0]) for k, v in arrays.items()}
            filemap = {k: k + ".pt" for k in arrays}
            for k, v in arrays.items():
                torch.save(v, folder / filemap[k])
            manifest = {
                "protocol": protocol["digest"],
                "filemap": filemap,
                "domains": {
                    "surface": {
                        "position": "pos",
                        "ids": "ids",
                        "targets": {"p": "p"},
                        "identity_basis": "artifact",
                    }
                },
            }
            path = folder / "manifest.json"
            path.write_text(json.dumps(manifest))
            results.append({"sample": name, "manifest": str(path)})
        path = root / "report.json"
        path.write_text(
            json.dumps({"status": "succeeded", "protocol": protocol, "results": results})
        )
        paths.append(path)
    report = compare(
        *paths,
        domain="surface",
        output=tmp_path / "ok",
        dataset_component=None,
        config={},
        cuts=[],
        labels=("custom_a", "custom_b"),
        visual_count=0,
    )
    assert report["metrics"]["custom_a"]["p"]["mse"] == 1
    assert report["metrics"]["custom_b"]["p"]["count"] == 4
    torch.save(torch.full((2, 1), float("nan")), tmp_path / "custom_b/s2/p.prediction.pt")
    with pytest.raises(ValueError, match="非有限"):
        compare(
            *paths,
            domain="surface",
            output=tmp_path / "failed",
            dataset_component=None,
            config={},
            cuts=[],
            visual_count=0,
        )
    failed = json.loads((tmp_path / "failed/comparison.json").read_text())
    assert failed["status"] == "failed" and len(failed["completed"]) == 1
    source = json.loads(paths[1].read_text())
    source["protocol"]["weights"] = "changed"
    paths[1].write_text(json.dumps(source))
    with pytest.raises(ValueError, match="摘要"):
        compare(
            *paths,
            domain="surface",
            output=tmp_path / "bad-source",
            dataset_component=None,
            config={},
            cuts=[],
            visual_count=0,
        )
