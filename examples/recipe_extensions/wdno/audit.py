import numpy as np

from ai4e_core import run
from ai4e_core.applications.spatiotemporal_pde.post import evaluate


def check_energy(arrays):
    """检查已保存的能量与固定预测逐样本、逐时刻相符。"""
    expected = np.mean(arrays["prediction"] ** 2, axis=-1)
    saved = arrays["energy"]
    if saved.shape != expected.shape or not np.isfinite(saved).all():
        raise ValueError("能量形状不符或含非有限值")
    if not np.allclose(saved, expected, rtol=1e-6, atol=1e-7):
        raise ValueError("已保存能量与固定预测不一致")
    return {"energy_readback_passed": True}


def audit(results):
    """通过已有领域评价步骤读取分片，报告交给运行记录写入器。"""
    session = run.TrainingRun()
    if session.dry_run:
        return None
    summary = evaluate(results, check_energy)
    session.report(summary, stage="audit")
    session.artifact("wdno-energy-readback.json", summary)
    return summary
