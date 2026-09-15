"""运行真实 recipe 并通过原 writer 额外保留轮次快照，供恢复验收使用。"""

import argparse
import shutil
import sys
from pathlib import Path


def main():
    """只观察已提交状态，不改训练数据、权重或更新步骤。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    from ai4e_core.run.training import TrainingRun

    original = TrainingRun.checkpoint

    def checkpoint(self, label, payload):
        result = original(self, label, payload)
        if label == "latest" and payload["epoch"] > 0:
            # 验收副本属于工具输出；运行目录仍只有原 writer 写入。
            folder = args.config.parent / "dojo-epoch-snapshots" / self.run_dir.name
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(result, folder / f"epoch-{payload['epoch']}.pt")
        return result

    TrainingRun.checkpoint = checkpoint
    recipe = Path(__file__).resolve().parents[3] / "recipes/aero_cfd"
    sys.path.insert(0, str(recipe))
    from configuration import application_parameters, load_configuration
    from omegaconf import OmegaConf

    from ai4e_contrib.application.aero_cfd import load
    from ai4e_core import run

    def pipeline(cfg):
        """历史 NPY 参考路线显式调用兼容入口，不冒充五例物理 PT 流程。"""
        components = load(cfg)
        config = OmegaConf.create(application_parameters(cfg))
        session = TrainingRun()
        common = {
            "dataset_component": components.dataset,
            "model_component": components.model,
            "session": session,
        }
        dataset = prepared = trained = None
        if "rawprep" in cfg.pipeline.stages:
            dataset = run.stage(
                "rawprep",
                lambda _: components.workflow.datapre(config, executor=run.execute, **common),
                cfg,
            )
        if "trainprep" in cfg.pipeline.stages:
            prepared = run.stage(
                "trainprep", lambda _: components.workflow.trainprep(config, dataset, **common), cfg
            )
        if "train" in cfg.pipeline.stages:
            trained = run.stage(
                "train", lambda _: components.workflow.train(config, prepared, **common), cfg
            )
        if "post" in cfg.pipeline.stages:
            return run.stage("post", lambda _: components.workflow.post(config, **common), cfg)
        return trained or prepared or dataset

    raise SystemExit(
        run.run_recipe(load_configuration(args.config), stages=pipeline, script=__file__)
    )


if __name__ == "__main__":
    main()
