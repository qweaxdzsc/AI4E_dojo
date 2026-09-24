"""SafeDiffCon 研究步骤，可独立执行或由 pipeline 交接。"""

from configuration import load_configuration

from ai4e_core import run


def rawprep(*args, **kwargs):
    from rawprep import rawprep as execute

    return execute(*args, **kwargs)


def trainprep(*args, **kwargs):
    from trainprep import trainprep as execute

    return execute(*args, **kwargs)


def train(*args, **kwargs):
    from train import train as execute

    return execute(*args, **kwargs)


def posttrain(*args, **kwargs):
    from posttrain import posttrain as execute

    return execute(*args, **kwargs)


def infer(*args, **kwargs):
    from infer import infer as execute

    return execute(*args, **kwargs)


def post(*args, **kwargs):
    from post import post as execute

    return execute(*args, **kwargs)


def pipeline(cfg):
    """Python 是实际研究顺序的唯一来源。"""
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
    for value in (results, calibrated, pretrained, prepared, physical):
        if value is not None:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            pipeline,
            script=__file__,
            config_loader=load_configuration,
        )
    )
