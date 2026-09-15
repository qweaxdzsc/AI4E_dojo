"""推理设备占用只根据已有执行事实选择，自动选择避开训练。"""

from ai4e_task.tasks import inference


def test_known_training_device_is_busy(tmp_path, monkeypatch):
    monkeypatch.setattr(inference, "inspect_inference", lambda *_: ["cpu", "cuda:0", "cuda:1"])
    monkeypatch.setattr(
        inference,
        "list_runs",
        lambda *_: [
            {"status": "running", "run_dir": str(tmp_path), "metadata": {"device": "cuda"}},
            {"status": "succeeded", "run_dir": str(tmp_path), "metadata": {"device": "cuda:1"}},
        ],
    )
    options = {d["id"]: d for d in inference.inference_devices(tmp_path)}
    assert options["cuda:0"]["busy"] and not options["cuda:1"]["busy"]
    assert not options["cpu"]["busy"]
