"""控制流程的路径交接及公开资产登记，不依赖 Task。"""

import json
from pathlib import Path

from ai4e_core.base.config.conventions import resolve_input


def resolve_splits(explicit, configured, *, name):
    """两种来源都存在时逐分片核对，禁止静默覆盖。"""
    if explicit is None and configured is None:
        raise ValueError(f"缺少输入: {name}")
    if explicit is not None and configured is not None and set(explicit) != set(configured):
        raise ValueError(f"输入分片冲突: {name}")
    return {
        key: resolve_input(
            (explicit or {}).get(key), (configured or {}).get(key), name=f"{name}.{key}"
        )
        for key in (explicit if explicit is not None else configured)
    }


def register_splits(session, values, *, stage, kind):
    """登记领域清单和同目录数组，不将数组格式解释交给 Task。"""
    for split, path in values.items():
        session.record_asset(
            split,
            path,
            kind=kind,
            stage=stage,
            dependencies=[Path(path).parent],
            semantics={"type": "control.preparation" if kind == "preparation" else "control.trajectory", "split": split},
            bundle_root=Path(path).parent,
        )


def register_checkpoint(session, path, *, stage, phase):
    """登记完成阶段的权重身份，保留通用writer的原命名空间索引。"""
    session.record_asset(phase, path, kind="checkpoint", stage=stage,
                         semantics={"type": "control.checkpoint", "phase": phase})


def register_metrics(session, results, report, *, evaluate):
    """为参考评价登记口径和固定真值身份；自定义指标由其提供者声明语义。"""
    from ai4e_contrib.ability.eval.safediffcon.control import metrics as reference_metrics
    from ai4e_core.base.config import operation_record

    if evaluate is not reference_metrics:
        return
    record = json.loads(Path(results).read_text())
    case = record["metadata"]["case"]
    definitions = {
        "J": ("u", "source_u_squared", "sample_mean_final_frame_spatial_mse"),
        "J_source_outputs": (
            "channels_0_2",
            "source_objective_units",
            "sample_mean_sum_channel_time_mse_source_outputs",
        ),
        "J_dataset_targets": (
            "channels_0_2",
            "source_objective_units",
            "sample_mean_sum_channel_time_mse_dataset_targets",
        ),
        "R_sample": ("constraint", "1", "fraction_samples_with_any_violation"),
        "R_time": ("constraint", "1", "fraction_sample_times_with_any_violation"),
        "R_point": ("constraint", "1", "fraction_sample_time_points_with_violation"),
    }
    identity = {
        name: record["fields"][name]["sha256"] for name in ("ids", "target", "paper_target")
    }
    for name, (field, unit, statistic) in definitions.items():
        if name not in report:
            continue
        session.record_metric(
            name,
            report[name],
            stage="post",
            assets=[results, Path(results).parent],
            semantics={
                "field": field,
                "unit": unit,
                "split": "test",
                "statistic": statistic,
                "case": case,
                "data_identity": identity,
                "definition": operation_record(evaluate),
                "constraint": "abs(u)>0.8" if case == "burgers" else "channel_1<4.98",
                "paper_protocol_matched": False,
            },
        )
