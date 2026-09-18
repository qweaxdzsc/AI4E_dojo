"""显式流水线：交接 rawprep、trainprep、train、infer 与固定结果 post。"""

import sys

sys.dont_write_bytecode = True

from configuration import load_configuration
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run
from ai4e_core.run import TrainingRun


def pipeline(cfg):
    """按声明顺序执行阶段；已有数据或准备产物允许省略上游。"""
    stages = list(cfg.pipeline.stages)
    names = stages
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
    if "infer" in names:
        result = run.stage("infer", infer, cfg, result)
    if "post" in names:
        result = run.stage("post", post, cfg, result)
    return result if result is not None else prepared if prepared is not None else dataset


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
