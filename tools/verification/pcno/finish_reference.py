"""衔接已启动的双分支参考训练，完成后串行运行两组固定预测并记录结果。"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

from tools.verification.pcno.reference import digest


def training_ready(root: Path) -> bool:
    """只接受两个明确完成的250轮状态；失败或停滞不会冒充完成。"""
    complete = True
    for branch in ["pres", "temp"]:
        path = root / f"{branch}-250" / "status.json"
        if not path.is_file():
            raise ValueError(f"Missing training status: {path}")
        state = json.loads(path.read_text())
        if state["state"] == "failed":
            raise RuntimeError(f"{branch} reference failed: {state.get('traceback')}")
        if state["state"] != "complete":
            if time.time() - path.stat().st_mtime > 1800:
                raise RuntimeError(
                    f"{branch}: no progress for 30 minutes; inspect the original run before resuming"
                )
            complete = False
        elif state.get("epoch") != 250 or state.get("updates") != 5250:
            raise ValueError(f"{branch}: invalid complete state")
    return complete


def main():
    """在当前计算任务中等待训练产物；不创建定时任务或自动扩大预算。"""
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "data", "reference"]:
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    args.source, args.data, args.reference = (
        args.source.resolve(),
        args.data.resolve(),
        args.reference.resolve(),
    )
    record = args.reference / "continuation.json"
    # Refuse duplicate consumers; no overwrite of existing inference directories.
    with record.open("x") as stream:
        json.dump({"state": "waiting", "pid": os.getpid()}, stream)

    def status(state, **values):
        tmp = record.with_suffix(".tmp")
        tmp.write_text(json.dumps({"state": state, **values}, indent=2))
        tmp.replace(record)

    try:
        snapshot = args.reference / "continuation-tools"
        package = snapshot / "tools/verification/pcno"
        package.mkdir(parents=True, exist_ok=False)
        hashes = {}
        for name in ["predict.py", "reference.py", "finish_reference.py"]:
            target = package / name
            target.write_bytes(Path(__file__).with_name(name).read_bytes())
            hashes[name] = digest(target)
        (snapshot / "sha256.json").write_text(json.dumps(hashes, indent=2))
        while not training_ready(args.reference):
            time.sleep(10)
        for selection in ["training24", "demonstration18"]:
            output = args.reference / ("prediction-" + selection)
            status("predicting", selection=selection)
            cmd = [
                sys.executable,
                "-m",
                "tools.verification.pcno.predict",
                "--source",
                str(args.source),
                "--data",
                str(args.data),
                "--pressure",
                str(args.reference / "pres-250/latest.pt"),
                "--temperature",
                str(args.reference / "temp-250/latest.pt"),
                "--output",
                str(output),
                "--selection",
                selection,
            ]
            with (args.reference / f"prediction-{selection}.log").open("x") as stream:
                subprocess.run(
                    cmd, check=True, cwd=snapshot, stdout=stream, stderr=subprocess.STDOUT
                )
        status(
            "reference_complete",
            scope="reference training and predictions only; Dojo migration remains pending",
        )
    except BaseException as exc:
        status("failed", error=repr(exc))
        raise


if __name__ == "__main__":
    main()
