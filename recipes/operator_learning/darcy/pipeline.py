"""研究流程正文：Python决定顺序，配置只选择范围和参数。"""

from configuration import load_configuration
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run


def pipeline(cfg):
    """显式交接上游返回；单独阶段从inputs对应位置读取。"""
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
