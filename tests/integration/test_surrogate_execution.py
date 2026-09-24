"""非神经预测批量及数值状态持久化：尾批、精度、完整发布和损坏拒绝。"""

import json
import shutil

import numpy as np
import pytest

from ai4e_core.abilities.data.save.surrogate import read_state, save_state
from ai4e_core.abilities.inference.callable_prediction import predict_batches


def test_callable_tail_precision_and_variance():
    x = np.arange(21, dtype=np.float64).reshape(7, 3)
    sizes = []

    def operation(chunk):
        sizes.append(len(chunk))
        return chunk.sum(-1), chunk[:, 0] ** 2

    mean, variance = predict_batches(x, operation, batch_size=3)
    assert sizes == [3, 3, 1]
    assert mean.dtype == np.float64
    np.testing.assert_array_equal(mean, x.sum(-1))
    np.testing.assert_array_equal(variance, x[:, 0] ** 2)


@pytest.mark.parametrize("operation", [lambda x: x[:-1], lambda x: x * np.nan])
def test_callable_rejects_invalid_output(operation):
    with pytest.raises(ValueError):
        predict_batches(np.ones((5, 2)), operation, batch_size=2)


def test_callable_rejects_changing_dtype():
    count = 0

    def operation(x):
        nonlocal count
        count += 1
        return x.astype(np.float64 if count == 1 else np.float32)

    with pytest.raises(ValueError, match="精度"):
        predict_batches(np.ones((5, 2)), operation, batch_size=2)


def test_callable_reused_buffer_is_snapshotted():
    buffer = np.zeros((2, 1))

    def predict(x):
        buffer[:] = x
        return buffer

    x = np.arange(4).reshape(4, 1)
    np.testing.assert_array_equal(predict_batches(x, predict, batch_size=2), x)


def test_native_text_change_is_rejected(tmp_path):
    path = save_state(tmp_path / "trees", {"native": "leaf=1"}, context={})
    from pathlib import Path

    record = json.loads(Path(path).read_text())
    record["metadata"]["state"][1][0][1][1] = "leaf=2"
    Path(path).write_text(json.dumps(record))
    with pytest.raises(ValueError, match="摘要"):
        read_state(path)


def test_state_portable_exact_and_damage(tmp_path):
    state = {
        "kind": "example",
        "weights": np.arange(12, dtype=np.float64).reshape(4, 3),
        "native": "tree\nsize=2",
        "options": (None, True, [2, 1.5]),
    }
    context = {"fields": ["lift", "drag"], "identity": "train-a"}
    path = save_state(tmp_path / "original", state, context=context)
    shutil.copytree(tmp_path / "original", tmp_path / "moved")
    shutil.rmtree(tmp_path / "original")
    restored, got = read_state(tmp_path / "moved/manifest.json")
    assert got == context and restored["options"] == state["options"]
    assert restored["native"] == state["native"]
    np.testing.assert_array_equal(restored["weights"], state["weights"])
    assert restored["weights"].dtype == np.float64
    with pytest.raises(FileExistsError):
        save_state(tmp_path / "moved", state, context=context)
    array = tmp_path / "moved/array_0.npy"
    array.write_bytes(array.read_bytes() + b"changed")
    with pytest.raises(ValueError, match="内容"):
        read_state(tmp_path / "moved/manifest.json")
    assert path.endswith("manifest.json")


def test_state_failed_save_does_not_publish(tmp_path):
    with pytest.raises(ValueError):
        save_state(tmp_path / "broken", {"x": np.array([np.nan])}, context={})
    assert not list(tmp_path.iterdir())
    with pytest.raises(TypeError):
        save_state(tmp_path / "object", {"fn": lambda x: x}, context={})
    assert not list(tmp_path.iterdir())
