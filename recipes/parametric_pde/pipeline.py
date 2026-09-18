"""参数化 PDE 的显式阶段调用，无算法或训练循环。"""

import sys

sys.dont_write_bytecode = True
from configuration import components, load_configuration, validate
from omegaconf import OmegaConf

from ai4e_core import run
from ai4e_core.applications import parametric_pde
from ai4e_core.run import TrainingRun


def execute(name, cfg, **inputs):
    """公共输入只在领域连接处转换，阶段执行仍为普通函数。"""
    from configuration import application_parameters
    cfg = OmegaConf.to_container(cfg, resolve=True) if OmegaConf.is_config(cfg) else cfg
    validate(cfg)
    session = TrainingRun()
    parameters = application_parameters(cfg, stage=name, session=session, **inputs)
    return getattr(parametric_pde, name)(parameters, **components(cfg), session=session)


def pipeline(cfg):
    selected = cfg.pipeline.stages
    dataset = prepared = trained = results = None
    if "rawprep" in selected:
        dataset = run.stage("rawprep", execute, "rawprep", cfg)
    if "trainprep" in selected:
        prepared = run.stage("trainprep", execute, "trainprep", cfg, dataset=dataset)
    if "train" in selected:
        trained = run.stage("train", execute, "train", cfg, prepared=prepared)
    if "infer" in selected:
        results = run.stage("infer", execute, "infer", cfg, prepared=prepared, trained=trained)
    if "post" in selected:
        return run.stage("post", execute, "post", cfg, results=results)
    return results if results is not None else trained if trained is not None else prepared


if __name__ == "__main__":
    raise SystemExit(run.launch(pipeline, script=__file__, config_loader=load_configuration))
