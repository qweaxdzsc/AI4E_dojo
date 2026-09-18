"""后处理只消费固定推理结果。"""

import sys

sys.dont_write_bytecode = True
from configuration import load_configuration

from ai4e_core import run
from ai4e_core.run import TrainingRun


def post(cfg, trained=None):
    """连续或独立运行都消费固定结果。"""
    from ai4e_core.applications.aero_cfd.infer import open_results

    reference = cfg.inputs.post.get("results")
    if isinstance(trained, dict) and "protocol" in trained and "results" in trained:
        reference = trained
    if reference is not None:
        return open_results(reference, session=TrainingRun())
    raise ValueError("后处理需要固定推理结果，不能重新运行模型")


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
