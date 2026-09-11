"""五组正式实验顺序执行；只消费明确产生的新运行，不推测旧目录成功。"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    """每组只运行一次，非零退出立即停止并记录未完成项。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument(
        "--names",
        nargs="+",
        default=[
            "nasa_crm_abupt",
            "nasa_crm_transolver3",
            "shapenet_car_abupt",
            "shapenet_car_transolver3_surface",
            "shapenet_car_transolver3_volume",
        ],
    )
    args = parser.parse_args()
    registry = args.root / "training-runs.json"
    results = json.loads(registry.read_text()) if registry.exists() else {}
    for name in args.names:
        if name in results and results[name]["status"] == "succeeded":
            print(f"已完成，保持原训练：{name}", flush=True)
            continue
        output = args.root / "runs" / name
        before = set(output.iterdir()) if output.exists() else set()
        command = [
            sys.executable,
            str(args.root / "examples" / name / "pipeline.py"),
            "--set",
            "pipeline.stages=[trainprep,train]",
        ]
        result = subprocess.run(command, check=False)
        created = set(output.iterdir()) - before
        if len(created) != 1:
            raise RuntimeError(f"{name}: 本次运行身份不唯一")
        run = created.pop()
        summary = json.loads((run / "summary.json").read_text())
        complete = result.returncode == 0 and (run / "checkpoints/last.pt").exists()
        results[name] = {
            "status": "succeeded" if complete else "failed",
            "run": str(run),
            "returncode": result.returncode,
            "summary": summary,
        }
        registry.write_text(json.dumps(results, indent=2, ensure_ascii=False))
        if not complete:
            raise SystemExit(result.returncode or 1)


if __name__ == "__main__":
    main()
