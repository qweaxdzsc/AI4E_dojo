"""Python 决定原始准备、模型准备、训练、预测与固定结果报告顺序。"""

from configuration import load_configuration, validate
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run


def pipeline(cfg):
    """同一正文由 direct-core 与 Task 执行。"""
    cfg = validate(cfg)
    selected = cfg["pipeline"]["stages"]
    physical = prepared = trained = results = last = None
    if "rawprep" in selected:
        last = physical = run.stage("rawprep", rawprep, cfg)
    if "trainprep" in selected:
        last = prepared = run.stage("trainprep", trainprep, cfg, physical)
    if "train" in selected:
        last = trained = run.stage("train", train, cfg, prepared)
    if "infer" in selected:
        last = results = run.stage("infer", infer, cfg, prepared, trained)
    if "post" in selected:
        last = run.stage("post", post, cfg, results)
    return last


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
