"""GenCP 完整研究顺序：处理、准备、分场训练、耦合生成、固定评价。"""

from configuration import load_configuration
from infer import infer
from post import post
from rawprep import rawprep
from single import single
from train import train
from trainprep import trainprep

from ai4e_core import run


def pipeline(cfg):
    """显式交接各阶段返回值；阶段失败时由运行器记录。"""
    selected = cfg.pipeline.stages
    physical = prepared = weights = predictions = None
    if "rawprep" in selected:
        physical = run.stage("rawprep", rawprep, cfg)
    if "trainprep" in selected:
        prepared = run.stage("trainprep", trainprep, cfg, physical)
    if "train" in selected:
        weights = run.stage("train", train, cfg, prepared)
    if "single" in selected:
        run.stage("single", single, cfg, prepared, weights)
    if "infer" in selected:
        predictions = run.stage("infer", infer, cfg, prepared, weights)
    if "post" in selected:
        return run.stage("post", post, cfg, predictions)
    return predictions if predictions is not None else weights if weights is not None else prepared


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            pipeline,
            script=__file__,
            config_loader=load_configuration,
        )
    )
