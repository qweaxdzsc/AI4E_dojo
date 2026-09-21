"""在推理与后处理之间插入本地速度模长分析。"""

from configuration import load_configuration
from infer import infer
from local_components import speed
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.window_results import extend_windows
from ai4e_core.base.config.conventions import resolve_input


def derive(cfg, results):
    """读取固定结果，保存派生数组及新清单。"""
    source = resolve_input(results, cfg["inputs"]["post"]["results"], name="post.results")
    return extend_windows(source, speed, run.TrainingRun().output_dir("speed"))


def pipeline(cfg):
    selected = cfg["pipeline"]["stages"]
    dataset = prepared = trained = results = None
    if "rawprep" in selected:
        dataset = run.stage("rawprep", rawprep, cfg)
    if "trainprep" in selected:
        prepared = run.stage("trainprep", trainprep, cfg, dataset)
    if "train" in selected:
        trained = run.stage("train", train, cfg, prepared)
    if "infer" in selected:
        results = run.stage("infer", infer, cfg, prepared, trained)
    if "post" in selected:
        extended = run.stage("speed", derive, cfg, results)
        # 明确消费新产物，外部旧post输入只供derive使用。
        from copy import deepcopy

        post_cfg = deepcopy(cfg)
        post_cfg["inputs"]["post"]["results"] = None
        return run.stage("post", post, post_cfg, extended)
    return results or trained or prepared or dataset


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
