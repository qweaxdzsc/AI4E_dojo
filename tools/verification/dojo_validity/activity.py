"""实验组共用的进程计时入口；每次尝试单独保存命令、日志和退出码。"""

import argparse
import json
import subprocess
import time
import uuid
from pathlib import Path


def main():
    """运行明确阶段的命令，不设训练时长上限。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "phase",
        choices=["coding", "training", "evaluation", "environment_setup", "data_preparation"],
    )
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ["--"] else args.command
    root = Path(__file__).resolve().parent
    event_id = str(uuid.uuid4())
    out = root / "evidence/activities" / event_id
    out.mkdir(parents=True)
    record = {
        "event_id": event_id,
        "phase": args.phase,
        "start": time.monotonic(),
        "wall_start": time.time(),
        "command": command,
        "cwd": str(Path.cwd()),
    }
    (out / "started.json").write_text(json.dumps(record))
    with (out / "stdout.log").open("w") as log:
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        record["pid"] = process.pid
        for line in process.stdout:
            log.write(line)
            log.flush()
            print(line, end="", flush=True)
        record.update(exit_code=process.wait(), end=time.monotonic(), wall_end=time.time())
    (out / "completed.json").write_text(json.dumps(record, indent=2) + "\n")
    raise SystemExit(record["exit_code"])


if __name__ == "__main__":
    main()
