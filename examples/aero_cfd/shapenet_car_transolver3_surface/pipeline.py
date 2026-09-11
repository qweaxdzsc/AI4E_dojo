"""四阶段流水线：显式交接 rawprep、trainprep、train 与 post 的结果。"""

import sys

sys.dont_write_bytecode = True

from configuration import load_configuration
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run
from ai4e_core.run.training import TrainingRun


def pipeline(cfg):
    """按声明顺序执行阶段；已有数据或准备产物允许省略上游。"""
    stages = list(cfg.pipeline.stages)
    if any(name in {"pre", "datapre"} for name in stages):
        raise ValueError("pre 已更名为 rawprep，请改用 rawprep")
    allowed = ["rawprep", "trainprep", "train", "post"]
    names = list(stages)
    if len(set(names)) != len(names) or any(name not in allowed for name in names):
        raise ValueError("未知或重复阶段")
    if names != sorted(names, key=allowed.index):
        raise ValueError("阶段必须按 rawprep → trainprep → train → post 顺序声明")
    dataset = prepared = result = None
    if "rawprep" in names:
        dataset = run.stage("rawprep", rawprep, cfg)
        if TrainingRun().dry_run:
            TrainingRun().report(
                {
                    "mode": "pipeline_check",
                    "deferred": names[1:],
                    "reason": "rawprep 检查不发布数据，下游须在数据交付后验证",
                },
                stage="pipeline",
            )
            return dataset
    if "trainprep" in names:
        prepared = run.stage("trainprep", trainprep, cfg, dataset)
    if "train" in names:
        result = run.stage("train", train, cfg, prepared)
    if "post" in names:
        result = run.stage("post", post, cfg)
    return result if result is not None else prepared if prepared is not None else dataset


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
