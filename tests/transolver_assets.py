"""NASA 合成数据夹具；源文件编号允许重名，来源和分片决定身份。"""

from pathlib import Path

import h5py
import numpy as np
import yaml

from ai4e_contrib.application.datasets.nasa_crm.constants import (
    CONDITION_FIELDS,
    GLOBAL_TARGET_FIELDS,
)


def write_source(path: Path, sample_count: int, point_count: int, *, offset: float) -> None:
    """Create a small, schema-complete NASA CRM HDF5 fixture."""
    coordinates = np.arange(point_count, dtype=np.float32)
    with h5py.File(path, "w") as output:
        for index in range(1, sample_count + 1):
            sample = output.create_group(f"Sample{index:03d}")
            sample_value = offset + index
            sample.create_dataset("CoordinateX", data=coordinates + sample_value)
            sample.create_dataset("CoordinateY", data=coordinates * 0.5 - sample_value)
            sample.create_dataset("CoordinateZ", data=coordinates * 0.1 + sample_value * 0.01)
            sample.create_dataset("NormalX", data=np.full(point_count, 1.0, dtype=np.float32))
            sample.create_dataset("NormalY", data=np.full(point_count, 0.25, dtype=np.float32))
            sample.create_dataset("NormalZ", data=np.full(point_count, -0.5, dtype=np.float32))
            sample.create_dataset(
                "Surface", data=np.linspace(0.1, 1.0, point_count, dtype=np.float32)
            )
            sample.create_dataset("PressureCoefficient", data=coordinates * 0.01 + sample_value)
            sample.create_dataset("cfx", data=coordinates * 0.001 + sample_value * 0.01)
            sample.create_dataset("cfy", data=coordinates * -0.002 + sample_value * 0.02)
            sample.create_dataset("cfz", data=coordinates * 0.003 - sample_value * 0.01)
            for condition_index, name in enumerate(CONDITION_FIELDS):
                sample.attrs[name] = sample_value * (condition_index + 1)
            for target_index, name in enumerate(GLOBAL_TARGET_FIELDS):
                sample.attrs[name] = sample_value * 0.1 * (target_index + 1)


def configuration(tmp_path):
    """生成完整 schema 的小数据和真实网络小配置用于快速契约测试。"""
    root = Path(__file__).resolve().parents[1]
    cfg = yaml.safe_load((root / "tests/fixtures/transolver3/reference-example.yaml").read_text())
    raw = tmp_path / "raw"
    raw.mkdir(parents=True)
    train, test = raw / "training.h5", raw / "test.h5"
    write_source(train, 5, 24, offset=0)
    write_source(test, 2, 24, offset=100)
    cfg["dataset"].update(root=str(raw), train_h5=str(train), test_h5=str(test), chunk_count=4)
    cfg["data_root"] = str(tmp_path / "data")
    cfg["run_root"] = str(tmp_path / "runs")
    cfg["model"]["parameters"].update(
        n_hidden=16, n_layers=2, n_head=4, slice_num=4, gradient_checkpointing=False
    )
    cfg["train"].update(device="cpu", max_epochs=2)
    cfg["post"].update(export_vtk=False, all_samples=True)
    config_dir = tmp_path / "configuration"
    config_dir.mkdir()
    path = config_dir / "config.yaml"
    path.write_text(yaml.safe_dump(cfg, sort_keys=False))
    from tests.integration.test_dataset_recipe import load_internal

    return load_internal(path), path
