"""NASA 原始处理：来源读取、物理字段、校验、容器与事务发布。"""

import sys

sys.dont_write_bytecode = True
from configuration import application_parameters, load_components, load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd.rawprep import physical as pre
from ai4e_core.run import TrainingRun


def rawprep(cfg):
    """NASA 无体场，保留来源的完整表面字段与实体身份。"""
    component = load_components(cfg).dataset
    source = pre.open_source(application_parameters(cfg), component=component)
    data = pre.read(source)
    data = pre.extract_fields(data, component=component)
    data = pre.validate_fields(data)
    data = pre.select_fields(
        data,
        source=source,
        extraction=cfg.rawprep.get("extraction"),
        format=cfg.rawprep.get("format", "pt"),
    )
    results = run.execute(data, save=pre.save_strategy(source), output=cfg.paths.datasets)
    return pre.publish_dataset(results, source=source, session=TrainingRun())


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
