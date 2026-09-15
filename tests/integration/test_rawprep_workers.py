"""原始处理并行线程：缺省顺序、多线程重叠、首错保留已提交结果。"""

import threading
import time

import pytest

from ai4e_contrib.application.datasets import shapenet_car
from ai4e_core.applications.aero_cfd.rawprep.descriptor import (
    resolve_rawprep,
    resolved_workers,
    validate_rawprep,
)
from ai4e_core.applications.base.dataset import Dataset
from ai4e_core.run.dataset import execute
from ai4e_core.run.execute import BatchExecutionError
from tests.integration.test_dataset_recipe import RECIPE, load_configuration


def _dataset(tmp_path, names, step):
    return Dataset(
        root=tmp_path,
        samples=tuple(names),
        partitions={"train": tuple(names)},
        metadata={},
        steps=(("work", step),),
        options={"config": {}},
    )


def _save(ctx, output):
    return {"names": [ctx["sample"]], "sample": ctx["sample"]}


def test_missing_workers_is_sequential():
    assert resolved_workers({}) == 1
    assert resolved_workers({"workers": 8}) == 8


def test_invalid_workers_rejected_on_load_and_validate():
    profile = shapenet_car.describe_rawprep()
    raw = {**profile["defaults"], "workers": 0}
    with pytest.raises(ValueError, match="workers"):
        validate_rawprep(raw, profile)
    with pytest.raises(ValueError, match="workers"):
        resolve_rawprep({"components": {"dataset": shapenet_car.__name__}, "rawprep": {"workers": 65}})
    with pytest.raises(ValueError, match="workers"):
        load_configuration(RECIPE / "config.yaml", {"rawprep.workers": 0})


def test_template_accepts_workers_override():
    public = load_configuration(RECIPE / "config.yaml", {"rawprep.workers": 4})
    assert public.rawprep.workers == 4


def test_workers_overlap_and_first_error_keeps_started(tmp_path):
    current = 0
    peak = 0
    lock = threading.Lock()

    def step(ctx):
        nonlocal current, peak
        with lock:
            current += 1
            peak = max(peak, current)
        time.sleep(0.15)
        with lock:
            current -= 1
        if ctx["sample"] == "c":
            raise RuntimeError("boom")
        return ctx

    with pytest.raises(BatchExecutionError) as raised:
        execute(
            _dataset(tmp_path, ["a", "b", "c", "d"], step),
            save=_save,
            output={},
            settings={"rawprep": {"workers": 2}},
        )
    summary = raised.value.summary
    assert peak >= 2
    assert summary["failed"] >= 1
    assert summary["success"] >= 1
    assert any(item["sample"] == "c" for item in summary["failures"])
    assert summary["success"] + summary["failed"] + summary["unexecuted"] == summary["total"]


def test_single_worker_does_not_overlap(tmp_path):
    current = 0
    peak = 0
    lock = threading.Lock()

    def step(ctx):
        nonlocal current, peak
        with lock:
            current += 1
            peak = max(peak, current)
        time.sleep(0.05)
        with lock:
            current -= 1
        return ctx

    summary = execute(
        _dataset(tmp_path, ["a", "b", "c"], step),
        save=_save,
        output={},
        settings={"rawprep": {"workers": 1}},
    )
    assert summary["success"] == 3
    assert peak == 1
