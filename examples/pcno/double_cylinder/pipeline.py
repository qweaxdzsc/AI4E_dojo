"""圆柱研究流程：Python表达阶段顺序，配置仅提供选择与参数。"""

from configuration import load_configuration
from infer import infer
from post import post
from rawprep import rawprep
from train import train
from trainprep import trainprep

from ai4e_core import run


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
        return run.stage("post", post, cfg, results)
    return results or trained or prepared or dataset


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
