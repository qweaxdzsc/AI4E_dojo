"""来源名单、物理读取及逐场 PT/VTKHDF 交付。"""

from configuration import validate

from ai4e_contrib.application.parametric_pde.geotransolver import binding
from ai4e_core import run
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.applications.parametric_pde.rawprep import prepare_named_fields


def rawprep(cfg):
    """原始字段和拓扑保存，采样及转点留到模型准备。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    source = binding.source(cfg["inputs"]["rawprep"]["source"])
    result = prepare_named_fields(
        source.samples(),
        source.read,
        session.output_dir("rawprep"),
        session=session,
        metadata={"dataset": "darcy"},
    )
    record_bundle(session, "physical", result, kind="dataset", stage="rawprep")
    session.report({"dataset": result}, stage="rawprep")
    return result


if __name__ == "__main__":
    from configuration import load_configuration

    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
