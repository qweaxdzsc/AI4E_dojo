"""阶段日志的切换、心跳继承、异常恢复与写入分流验收。"""

import threading

import pytest

from ai4e_core import run
from ai4e_core.base import events
from tests.integration.test_dataset_recipe import setup_case


def test_recipe_phases_and_console_summaries(tmp_path, capsys):
    folder, cfg = setup_case(tmp_path)
    cfg.pipeline.stages = ["rawprep", "train", "post"]

    def stage(cfg):
        events.event("数据集", "选择结果", 样本总数=2)
        events.event("统计", "开始")
        events.event("自定义能力", "进度", 完成=1)
        with events.operation("字段提取"):
            events.event("字段提取", "结果", 形状="(4, 1)")
        events.LOGGER.warning("提交警告：%s", "保留备份")

    assert (
        run.run_recipe(
            cfg, stages=dict.fromkeys(cfg.pipeline.stages, stage), script=folder / "pipeline.py"
        )
        == 0
    )
    record = next((tmp_path / "records").iterdir())
    log = (record / "logs/run.log").read_text()
    console = capsys.readouterr().err
    for phase in cfg.pipeline.stages:
        for item in ("阶段/开始", "阶段/结束", "数据集/选择结果", "统计/开始", "自定义能力/进度"):
            assert f"[{phase}/{item}]" in log
            assert f"[{phase}/{item}]" in console
        for state in ("开始", "结果", "结束"):
            assert f"[{phase}/字段提取/{state}]" in log
            assert f"[{phase}/字段提取/{state}]" not in console
        assert f"[{phase}] 提交警告：保留备份" in log
        assert f"[{phase}/{phase}/" not in log
        assert f"[{phase}/运行/" not in log
    assert "[运行/开始]" in log and "[运行/结束]" in log
    assert events.PHASE.get() == ""


def test_failure_and_next_run_restore_context(tmp_path, caplog, capsys):
    folder, cfg = setup_case(tmp_path)

    def fail(cfg):
        with events.operation("字段提取"):
            raise ValueError("缺失 Pressure")

    assert run.run_recipe(cfg, stages={"rawprep": fail}, script=folder / "rawprep.py") == 1
    record = next((tmp_path / "records").iterdir())
    log = (record / "logs/run.log").read_text()
    errors = (record / "logs/errors.log").read_text()
    assert "[rawprep/字段提取/失败]" in log
    assert "[rawprep/阶段/失败]" in log
    assert "[rawprep/阶段/结束]" not in log
    assert "Traceback" not in log
    assert "Traceback" in errors and "缺失 Pressure" in errors
    assert "[rawprep/字段提取/失败]" in capsys.readouterr().err
    assert events.PHASE.get() == ""
    with caplog.at_level("INFO", logger=events.LOGGER.name):
        events.event("独立能力", "结果")
    assert "[独立能力/结果]" in caplog.text
    assert "[rawprep/独立能力/结果]" not in caplog.text
    cfg.pipeline.stages = ["post"]
    assert (
        run.run_recipe(
            cfg,
            stages={"post": lambda cfg: events.event("报告", "结果")},
            script=folder / "pipeline.py",
        )
        == 0
    )
    assert "[post/报告/结果]" in caplog.text
    assert "[rawprep/报告/结果]" not in caplog.text
    assert events.PHASE.get() == ""


def test_heartbeat_inherits_phase_and_sample(caplog, monkeypatch):
    heartbeat = threading.Event()
    original = events.event

    def observe(name, state, /, **details):
        original(name, state, **details)
        if state == "运行中":
            heartbeat.set()

    monkeypatch.setattr(events, "event", observe)
    monkeypatch.setattr(events, "INTERVAL", 0.01)
    token = events.SAMPLE.set("car_001")
    try:
        with (
            caplog.at_level("INFO", logger=events.LOGGER.name),
            events.phase("train"),
            events.operation("慢能力"),
        ):
            assert heartbeat.wait(2), "未收到真实心跳"
    finally:
        events.SAMPLE.reset(token)
    records = [r for r in caplog.records if getattr(r, "operation", "") == "慢能力"]
    assert {r.event_state for r in records} == {"开始", "运行中", "结束"}
    assert all(r.recipe_phase == "train" for r in records)
    assert all("样本=car_001" in r.getMessage() for r in records)
    assert "[train/慢能力/运行中]" in caplog.text
    assert "%" not in caplog.text
    assert events.PHASE.get() == ""


def test_nested_phase_restores_outer_context():
    with events.phase("pre"):
        with pytest.raises(ValueError), events.phase("post"):
            raise ValueError("失败")
        assert events.PHASE.get() == "pre"
    assert events.PHASE.get() == ""
