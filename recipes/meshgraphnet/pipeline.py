"""MeshGraphNet 研究流程的唯一顺序来源。"""

from configuration import load_configuration, validate
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run


def pipeline(cfg):
    """按固定研究顺序运行配置选择的阶段。"""
    cfg = validate(cfg)
    selected = cfg["pipeline"]["stages"]
    physical = prepared = trained = results = None
    if "rawprep" in selected:
        physical = run.stage("rawprep", rawprep, cfg)
    if "trainprep" in selected:
        prepared = run.stage("trainprep", trainprep, cfg, physical)
    if "train" in selected:
        trained = run.stage("train", train, cfg, prepared)
    if "infer" in selected:
        results = run.stage("infer", infer, cfg, prepared, trained)
    if "post" in selected:
        run.stage("post", post, cfg, results)
    return results or trained or prepared or physical


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
