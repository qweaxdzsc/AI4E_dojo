"""独立后处理只消费固定预测，通过普通用户函数形成诊断。"""

from configuration import component

from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.run import TrainingRun


def post(cfg, results=None):
    """明确固定结果输入，不导入模型或重做推理。"""
    session = TrainingRun()
    results = resolve_input(results, cfg["inputs"]["post"]["predictions"], name="post.predictions")
    report = component(cfg["components"]["post"])(results, session.output_dir("post"))
    session.record_asset(
        "diagnostics", report["arrays"], kind="other", stage="post", dependencies=[results]
    )
    session.report(report, stage="post")
    return report
