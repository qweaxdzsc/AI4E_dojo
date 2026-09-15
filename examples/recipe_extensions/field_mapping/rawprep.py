"""原始处理：登记单样本步骤，再统一执行和发布。"""

import sys

sys.dont_write_bytecode = True
from configuration import load_components, load_configuration
from custom_abilities import speed_magnitude

from ai4e_core import run
from ai4e_core.applications.aero_cfd import rawprep as pre


def rawprep(cfg):
    """交付本次成功处理的数据清单，检查模式不发布数据。"""
    components = load_components(cfg)
    source = pre.open_source(component=components.dataset, settings=cfg.dataset)

    # 仅登记；每个样本在 run.execute 中才读取和计算。
    data = pre.read(source, sources=cfg.rawprep.sources)
    data = pre.extract_fields(
        data, fields=cfg.rawprep.fields, extraction=cfg.rawprep.get("extraction")
    )
    data = pre.derive_geometry(data, features=cfg.rawprep.geometry)
    data = pre.map_fields(
        data,
        name="速度模长",
        operation=speed_magnitude,
        inputs=cfg.rawprep.speed.inputs,
        outputs=cfg.rawprep.speed.outputs,
    )
    data = pre.select_fields(
        data, fields=cfg.rawprep.save_fields, extraction=cfg.rawprep.get("extraction")
    )
    data = pre.validate_fields(data)
    data = pre.filter_points(data, filters=cfg.rawprep.filters)
    data = pre.validate_fields(data)
    data = pre.encode(data, format=cfg.rawprep.get("format", "pt"), vtkhdf=cfg.rawprep.vtkhdf)

    results = run.execute(data, save=pre.save_sample, output=cfg.paths.datasets)
    statistics = pre.compute_statistics(results, settings=cfg.rawprep.statistics)
    return pre.publish_dataset(results, statistics=statistics)


if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"rawprep": rawprep},
            script=__file__,
            only=["rawprep"],
            config_loader=load_configuration,
        )
    )
