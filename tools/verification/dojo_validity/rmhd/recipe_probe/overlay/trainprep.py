"""仅训练分片拟合统计，显式物化训练缓存并保留物理验证引用。"""

from configuration import component
from local_data import NormalizeSample, read_record, save_preparation

from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.run import TrainingRun


def trainprep(cfg, physical=None):
    """阶段正文表达拟合、变换、保存与下游交接。"""
    session = TrainingRun()
    source = resolve_input(
        physical, cfg["inputs"]["trainprep"]["physical"], name="trainprep.physical"
    )
    records = read_record(source)
    stats = component(cfg["components"]["statistics"])(records["train"])
    output = session.output_dir("trainprep")
    normalized = session.execute_samples(
        records["train"], NormalizeSample(stats, output), stage="trainprep"
    )
    preparation = save_preparation(output, records, stats, normalized)
    session.record_asset(
        "preparation", preparation, kind="dataset", stage="trainprep", dependencies=[source]
    )
    session.report({"preparation": preparation, "statistics": stats}, stage="trainprep")
    return preparation
