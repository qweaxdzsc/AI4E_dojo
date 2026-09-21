"""外流 GeoTransolver 测试共用的真实物理清单布局夹具。"""

import shutil
from pathlib import Path

import yaml

from tests.integration.test_meshgraphnet_aero_examples import setup_meshgraphnet_case

ROOT = Path(__file__).resolve().parents[1]


def setup_case(tmp_path, dataset):
    """复用网格夹具写入器，替换完整公开案例后固定小网络测试参数。"""
    case, platform = setup_meshgraphnet_case(tmp_path, dataset + "_meshgraphnet")
    shutil.copytree(
        ROOT / "examples/aero_cfd" / (dataset + "_geotransolver"), case, dirs_exist_ok=True
    )
    cfg = yaml.safe_load((case / "config.yaml").read_text())
    cfg["inputs"]["trainprep"]["dataset"] = str(platform / "manifest.json")
    cfg["data_root"] = str(tmp_path / "data")
    cfg["run_root"] = str(tmp_path / "runs")
    cfg["model"]["parameters"].update(n_layers=2, n_hidden=16, n_head=2, slice_num=4)
    cfg["train"].update(device="cpu", max_epochs=2)
    cfg["infer"].update(device="cpu", query_chunk_size=3)
    cfg["post"].update(figures=[])
    (case / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
    return case, platform, cfg
