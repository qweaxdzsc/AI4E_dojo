"""Task 托管的显式控制流程；阶段选择只裁剪 Python 中的固定顺序。"""

from configuration import load_configuration
from infer import infer
from omegaconf import OmegaConf
from post import post
from posttrain import posttrain
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run

ORDER = ["rawprep", "trainprep", "train", "posttrain", "infer", "post"]


def load_task_configuration(path, overrides=None):
    """沿用案例参数检查，保留显式阶段范围；拒绝未知、重复或乱序选择。"""
    raw = OmegaConf.merge(OmegaConf.load(path), OmegaConf.from_dotlist(overrides or []))
    selected = list(OmegaConf.select(raw, "pipeline.stages", default=ORDER))
    if not selected or selected != [name for name in ORDER if name in selected]:
        raise ValueError("Task 阶段必须为非空、无重复的研究顺序子集")
    value = load_configuration(path, overrides)
    value["pipeline"] = {"stages": selected}
    return value


def execute(cfg):
    """前序产物直接交接，独立阶段由各步骤检查显式输入，不猜最近运行。"""
    selected = cfg.pipeline.stages
    physical = prepared = pretrained = calibrated = results = None
    if "rawprep" in selected:
        physical = run.stage("rawprep", rawprep, cfg)
    if "trainprep" in selected:
        prepared = run.stage("trainprep", trainprep, cfg, physical)
    if "train" in selected:
        pretrained = run.stage("train", train, cfg, prepared)
    if "posttrain" in selected:
        calibrated = run.stage("posttrain", posttrain, cfg, prepared, pretrained)
    if "infer" in selected:
        results = run.stage("infer", infer, cfg, prepared, calibrated)
    if "post" in selected:
        return run.stage("post", post, cfg, results)
    return results or calibrated or pretrained or prepared or physical


if __name__ == "__main__":
    raise SystemExit(run.launch(execute, script=__file__, config_loader=load_task_configuration))
