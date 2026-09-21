"""正式网络五次预热加二十次更新的本机测速；不扩大训练预算。"""

import json
import resource

from ai4e_contrib.application.spatiotemporal_pde.pcno.configuration import load_configuration
from ai4e_contrib.application.spatiotemporal_pde.pcno.training import train_branch
from ai4e_core import run
from ai4e_core.abilities.data.save.arrays import save_json


def benchmark(cfg):
    session = run.TrainingRun()
    preparation = cfg["inputs"]["train"]["preparation"]
    warm = train_branch(cfg, preparation, "fluid", "physics", session=session, stop_after=5)
    measured = train_branch(
        cfg,
        preparation,
        "fluid",
        "physics",
        session=session,
        resume=warm["checkpoint"],
        stop_after=25,
    )
    # 测速阶段须覆盖已激活物理项，另用小目标执行同样的25次更新。
    report = {
        "warmup_seconds": warm["seconds"],
        "twenty_updates_seconds": measured["seconds"],
        "seconds_per_update": measured["seconds"] / 20,
        "max_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "schedule_note": "500-update schedule; physics inactive before update 100; active objective is also computed",
        "checkpoint": measured["checkpoint"],
    }
    save_json(session.output_dir("benchmark") / "timing.json", report)
    session.report(report, stage="benchmark")
    print(json.dumps(report), flush=True)
    return report


if __name__ == "__main__":
    raise SystemExit(run.launch(benchmark, script=__file__, config_loader=load_configuration))
