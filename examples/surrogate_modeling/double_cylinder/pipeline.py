"""Python 正文决定四阶段顺序，配置只选择执行范围。"""

from configuration import load_configuration
from infer import infer
from post import post
from train import train
from trainprep import trainprep

from ai4e_core import run


def pipeline(cfg):
    """显式传递准备、拟合状态与固定结果，独立步骤由 inputs 指定输入。"""
    selected = cfg["pipeline"]["stages"]
    prepared = trained = results = last = None
    if "trainprep" in selected:
        last = prepared = run.stage("trainprep", trainprep, cfg)
    if "train" in selected:
        last = trained = run.stage("train", train, cfg, prepared)
    if "infer" in selected:
        last = results = run.stage("infer", infer, cfg, prepared, trained)
    if "post" in selected:
        last = run.stage("post", post, cfg, results)
    return last


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
