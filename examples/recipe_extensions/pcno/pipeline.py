"""PCNO 双分支地热研究流程；Python 明确决定阶段顺序。"""

from configuration import load_configuration, validate
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run
from pathlib import Path
from local_components import temperature_drop


def analyze(cfg, results):
    """新增显式分析步骤，产物交给独立后处理消费。"""
    session = run.TrainingRun()
    if session.dry_run:
        return results
    result = temperature_drop(results, session.output_dir("analysis"))
    root = Path(result).parent
    session.record_asset(
        "temperature_drop_results",
        result,
        kind="other",
        stage="analysis",
        dependencies=[*root.glob("*.pt"), *root.glob("*.npy")],
        bundle_root=root,
    )
    return result


def pipeline(cfg):
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
        last = results = run.stage("analysis", analyze, cfg, results)
    if "post" in selected:
        last = run.stage("post", post, cfg, results)
    return last


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            pipeline,
            script=__file__,
            config_loader=load_configuration,
        )
    )
