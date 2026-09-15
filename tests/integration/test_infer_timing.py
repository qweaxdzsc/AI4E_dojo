"""计时只涵盖预测区域，设备同步在两侧执行。"""

import pytest

from ai4e_core.abilities.inference import timing


def test_sync_brackets_prediction_even_on_error(monkeypatch):
    events = []
    monkeypatch.setattr(timing, "synchronize", lambda device: events.append(("sync", str(device))))
    with timing.measure("cpu") as value:
        events.append(("predict", "cpu"))
    assert events == [("sync", "cpu"), ("predict", "cpu"), ("sync", "cpu")]
    assert value["seconds"] >= 0
    with pytest.raises(ValueError), timing.measure("cpu") as failed:
        raise ValueError("prediction failed")
    assert failed["seconds"] >= 0
