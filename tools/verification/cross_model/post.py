"""消费明确登记的训练运行，独立执行全点推理，保留既有后处理登记。"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main():
    """按最后检查点后处理；成功产物登记后不重复评价。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    training = json.loads((args.root / "training-runs.json").read_text())
    registry = args.root / "post-runs.json"
    results = json.loads(registry.read_text()) if registry.exists() else {}
    for name, record in training.items():
        if record["status"] != "succeeded":
            raise ValueError(f"{name}: 训练未完成")
        if results.get(name, {}).get("status") == "succeeded":
            continue
        previous = Path(record["run"])
        output = args.root / "runs" / name
        before = set(output.iterdir())
        example = args.root / "examples" / name
        native = (example / "infer.py").is_file()
        stage = "infer" if native else "post"
        command = [
            sys.executable,
            str(example / (stage + ".py")),
            "--set",
            stage + ".checkpoint=" + str(previous / "checkpoints/last.pt"),
            "--set",
            "train.preparation=" + str(previous / "artifacts/preparation.json"),
        ]
        if native:
            command += ["--set", "infer.preparation=" + str(previous / "artifacts/preparation.json")]
        result = subprocess.run(command, check=False)
        created = set(output.iterdir()) - before
        if len(created) != 1:
            raise ValueError("后处理运行身份不唯一")
        run = created.pop()
        manifest = run / "artifacts/inference-results.json"
        if not manifest.is_file():
            manifest = run / "artifacts/physical-predictions.json"
        complete = result.returncode == 0 and manifest.exists()
        results[name] = {
            "status": "succeeded" if complete else "failed",
            "run": str(run),
            "manifest": str(manifest),
        }
        registry.write_text(json.dumps(results, indent=2))
        if not complete:
            raise SystemExit(result.returncode or 1)


if __name__ == "__main__":
    main()
