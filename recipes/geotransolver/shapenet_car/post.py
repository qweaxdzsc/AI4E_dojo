"""显式后处理：固定结果 → 指标 → 物理分析 → 图片与数据保存。"""

import sys

sys.dont_write_bytecode = True
from functools import partial

from configuration import load_configuration

from ai4e_core import run
from ai4e_core.applications.aero_cfd import post as post_ops
from ai4e_core.run import TrainingRun
from ai4e_core.run.execute import BatchExecutionError


def analyze_sample(reference, *, cfg, output):
    """一次只处理一个样本，研究者可在正文插入或替换公开步骤。"""
    fields = post_ops.read_fields(reference)
    settings = cfg.post
    selections = settings.get("fields")
    metrics = post_ops.evaluate_fields(
        fields, selections=selections, metrics=settings.get("metrics")
    )
    meshes, images, profiles, statistics = {}, {}, {}, {}
    figures = settings.get("figures", [])
    view = {
        "camera": settings.get("camera", "isometric"),
        "cmap": settings.get("cmap", "viridis"),
        "size": settings.get("image_size", [1600, 1000]),
    }
    pressure = settings.get("pressure", "surface:pressure:prediction")
    velocity = settings.get("velocity", "volume:velocity:prediction")
    # 纯指标调用不会进入网格绑定，更不会初始化渲染窗口。
    if "surface" in figures:
        surface = post_ops.bind_mesh(fields, domain="surface")
        meshes["surface"] = surface
        images["pressure"] = post_ops.render_field(surface, field=pressure, **view)
    if set(figures) & {"slice", "clip", "vectors", "streamlines", "contour", "profile"}:
        volume = post_ops.bind_mesh(fields, domain="volume")
        meshes["volume"] = volume
    if "slice" in figures:
        section = post_ops.slice_field(
            volume,
            origin=settings.get("slice_origin", [0, 0, 0]),
            normal=settings.get("slice_normal", [0, 1, 0]),
        )
        meshes["slice"] = section
        statistics["slice"] = post_ops.region_statistics(
            section, field=velocity, component="magnitude"
        )
        images["velocity_slice"] = post_ops.render_field(
            section, field=velocity, component="magnitude", **{**view, "camera": "normal"}
        )
    if "clip" in figures:
        clipped = post_ops.clip_field(
            volume,
            origin=settings.get("slice_origin", [0, 0, 0]),
            normal=settings.get("slice_normal", [0, 1, 0]),
        )
        meshes["clip"] = clipped
        images["velocity_clip"] = post_ops.render_field(
            clipped, field=velocity, component="magnitude", **view
        )
    if "vectors" in figures:
        vectors = post_ops.vector_field(
            volume,
            field=velocity,
            stride=settings.get("vector_stride", 20),
            scale=settings.get("vector_scale", 0.01),
        )
        meshes["vectors"] = vectors
        images["velocity_vectors"] = post_ops.render_field(
            vectors, field=velocity, component="magnitude", **view
        )
    if "streamlines" in figures:
        lines = post_ops.streamlines(
            volume,
            field=velocity,
            seeds=settings["streamline_seeds"],
            length=settings.get("streamline_length", 1.0),
            step=settings.get("streamline_step", 0.01),
        )
        meshes["streamlines"] = lines
        images["velocity_streamlines"] = post_ops.render_field(
            lines, field=velocity, component="magnitude", **view
        )
    if "contour" in figures:
        contours = post_ops.contour_field(
            volume, field=velocity, component="magnitude", values=settings["contour_values"]
        )
        meshes["contour"] = contours
        images["velocity_contour"] = post_ops.render_field(
            contours, field=velocity, component="magnitude", **view
        )
    if "profile" in figures:
        profile = post_ops.profile_field(
            volume,
            fields=[velocity],
            start=settings["profile_start"],
            end=settings["profile_end"],
            count=settings.get("profile_count", 101),
        )
        profiles["velocity"] = profile
        images["velocity_profile"] = post_ops.render_profile(
            profile, field="volume.velocity.prediction", component="magnitude", size=view["size"]
        )
    return post_ops.save_sample(
        fields,
        meshes=meshes,
        images=images,
        profiles=profiles,
        metrics=metrics,
        statistics=statistics,
        output=output,
        overwrite=settings.get("overwrite_analysis", False),
    )


def post(cfg, trained=None):
    """连续或独立运行都消费固定结果；没有启用分析时保留原接口。"""
    from ai4e_core.applications.aero_cfd.infer import open_results

    session = TrainingRun()
    reference = cfg.inputs.post.get("results")
    if isinstance(trained, dict) and "protocol" in trained and "results" in trained:
        reference = trained
    if reference is None:
        raise ValueError("后处理需要固定推理结果，不能重新运行模型")
    if not cfg.post.get("analysis_enabled", False):
        return open_results(reference, session=session)
    source = post_ops.open_analysis(reference, samples=cfg.post.get("samples"))
    if session.dry_run:
        result = post_ops.check_analysis(source, settings=cfg.post)
        session.report(result, stage="post")
        return result
    try:
        rows = session.execute_samples(
            source.samples,
            partial(analyze_sample, cfg=cfg, output=session.output_dir("post") / "analysis"),
            stage="post",
        )
    except BatchExecutionError as error:
        report = post_ops.publish_analysis(
            error.summary["results"],
            source=source,
            output=session.output_dir("post") / "analysis",
            failures=error.summary["failures"],
        )
        session.report(report, stage="post")
        raise
    report = post_ops.publish_analysis(
        rows, source=source, output=session.output_dir("post") / "analysis"
    )
    session.report(report, stage="post")
    return report


if __name__ == "__main__":
    raise SystemExit(
        run.launch({"post": post}, script=__file__, only=["post"], config_loader=load_configuration)
    )
