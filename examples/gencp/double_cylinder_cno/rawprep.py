"""读取原始来源，压缩包只解压到显式数据目录。"""

from configuration import load_configuration, plain

from ai4e_core import run
from ai4e_core.applications.coupled_physics.rawprep import materialize


def rawprep(cfg):
    """处理与检查共用来源入口；检查模式不解压。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    root = materialize(
        cfg["inputs"]["rawprep"]["source"], session.output_dir("rawprep"), execute=not session.dry_run
    )
    session.report({"physical_root": root}, stage="rawprep")
    return root


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
