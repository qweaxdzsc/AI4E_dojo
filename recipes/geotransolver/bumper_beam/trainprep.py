"""显式连接字段抽取、训练统计、编码和几何缓存。"""

from configuration import validate

from ai4e_contrib.application.spatiotemporal_pde.geotransolver import binding
from ai4e_core import run
from ai4e_core.abilities.geometry.radius_query import build_radius_cache_arrays
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.applications.spatiotemporal_pde.trainprep import prepare_trajectory_inputs
from ai4e_core.base.config.conventions import resolve_input


def trainprep(cfg, physical=None):
    """物理字段保持只读；统计和模型索引写独立准备目录。"""
    cfg = validate(cfg)
    session = run.TrainingRun()
    if session.dry_run:
        return None
    physical = resolve_input(
        physical, cfg["inputs"]["trainprep"]["dataset"], name="trainprep.dataset"
    )
    caches = None
    if cfg["model"].get("include_local_features", False):
        caches = lambda arrays: build_radius_cache_arrays(
            arrays["local_positions"],
            radii=cfg["model"]["radii"],
            neighbors=cfg["model"]["neighbors_in_radius"],
        )
    prepared = prepare_trajectory_inputs(
        physical,
        session.output_dir("trainprep"),
        extract=binding.extract,
        statistics=binding.statistics,
        transform=binding.transform,
        caches=caches,
        declaration={
            "case": "bumper_beam",
            "fields": binding.FIELDS,
            "times": binding.TIMES,
            "model": cfg["model"],
        },
    )
    record_bundle(session, "prepared", prepared, kind="preparation", stage="trainprep")
    session.report({"preparation": prepared}, stage="trainprep")
    return prepared


if __name__ == "__main__":
    from configuration import load_configuration

    raise SystemExit(
        run.launch(
            {"trainprep": trainprep},
            script=__file__,
            only=["trainprep"],
            config_loader=load_configuration,
        )
    )
