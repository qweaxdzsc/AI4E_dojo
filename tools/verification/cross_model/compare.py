"""从五个真实运行生成两个数据集比较报告；不启动训练。"""

import argparse
import json
from importlib import import_module
from pathlib import Path

import yaml
from ai4e_viz.compose.comparison import compose

from ai4e_core.applications.aero_cfd.post.comparison import compare


def main():
    """比较阶段单独运行，报告与预测分别保存并保留失败记录。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--dataset", choices=["nasa", "shapenet", "all"], default="all")
    parser.add_argument("--render-only", action="store_true")
    args = parser.parse_args()
    runs = json.loads((args.root / "post-runs.json").read_text())
    groups = {
        "nasa": [
            (
                "nasa_crm_abupt",
                "nasa_crm_transolver3",
                "surface",
                [{"axis": 1, "fraction": 0.5 + f / 2, "span_fraction": f} for f in (0.2, 0.5, 0.8)],
            )
        ],
        "shapenet": [
            ("shapenet_car_abupt", "shapenet_car_transolver3_surface", "surface", []),
            (
                "shapenet_car_abupt",
                "shapenet_car_transolver3_volume",
                "volume",
                [{"axis": 1, "fraction": 0.5}, {"axis": 2, "fraction": 0.5}],
            ),
        ],
    }
    for family, pairs in groups.items():
        if args.dataset not in ("all", family):
            continue
        reports = []
        for left, right, domain, cuts in pairs:
            if any(runs[name]["status"] != "succeeded" for name in (left, right)):
                raise ValueError("预测尚未完成")
            config = yaml.safe_load((args.root / "examples" / left / "config.yaml").read_text())
            output = args.root / "comparison" / family / domain
            if not args.render_only:
                compare(
                    runs[left]["manifest"],
                    runs[right]["manifest"],
                    domain=domain,
                    output=output,
                    dataset_component=import_module(config["components"]["dataset"]),
                    config=config,
                    cuts=cuts,
                    labels=("abupt", "transolver3"),
                )
            reports.append(output / "comparison.json")
        path = compose(
            reports, args.root / "reports" / family, title=family + " | AB-UPT vs Transolver-3"
        )
        print(path, flush=True)


if __name__ == "__main__":
    main()
