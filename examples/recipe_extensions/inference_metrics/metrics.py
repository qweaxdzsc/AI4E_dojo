"""普通用户评价函数：复用标准公式并显式标记本次算法来源。"""

from ai4e_core.applications.aero_cfd.infer.evaluation import evaluate_sample


def physical_metrics(item, selections, metrics):
    """消费物理数组和选中分量，返回可保存、导出、统计的逐场记录。"""
    rows = evaluate_sample(item, selections, metrics)
    for row in rows:
        row["algorithm"] = "user-physical-metrics-v1"
    return rows
