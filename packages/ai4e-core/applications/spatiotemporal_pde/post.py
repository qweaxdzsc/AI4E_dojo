"""固定时空结果的独立评价，不加载模型或重新采样。"""

from ai4e_core.abilities.data.save.array_manifest import read_arrays


def evaluate(results: dict, metrics) -> dict:
    """对每个完整分片计算声明的评价算术。"""
    summary = {}
    for split, path in results.items():
        record, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
        summary[split] = {
            **metrics(arrays),
            "samples": len(arrays["ids"]),
            "source": record["metadata"],
            "results": path,
        }
    return summary


def report_trajectories(*args, **kwargs):
    """按固定物理时间出具名轨迹报告，不构建网络或重跑预测。"""
    from ai4e_core.applications.parametric_pde.post import report_fields

    return report_fields(*args, **kwargs)
