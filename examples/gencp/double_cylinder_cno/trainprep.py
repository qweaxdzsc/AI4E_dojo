"""显式描述分场样本，再冻结源文件、窗口与归一化。"""


from configuration import load_configuration, plain

from ai4e_contrib.application.coupled_physics.gencp.cases import descriptions
from ai4e_core import run
from ai4e_core.applications.coupled_physics.trainprep import open_preparation, prepare
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg, physical=None):
    """独立阶段复用 rawprep；没有原始来源时拒绝准备。"""
    cfg = plain(cfg)
    session = run.TrainingRun()
    root = resolve_input(physical, cfg["inputs"]["trainprep"]["dataset"], name="trainprep.dataset")
    if not root:
        raise ValueError("trainprep 需要明确数据来源")
    if session.dry_run:
        return None
    fields = descriptions(cfg, root)
    reference = prepare(
        fields, session.output_dir("trainprep") / "preparation.json", dataset=cfg["dataset"]["name"]
    )
    session.record_asset("preparation", reference, kind="preparation", stage="trainprep",
                         dependencies=open_preparation(reference)["sources"])
    session.report({"preparation": reference}, stage="trainprep")
    return reference


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
