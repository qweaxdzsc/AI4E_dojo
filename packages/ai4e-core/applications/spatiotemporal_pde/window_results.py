"""时空窗口推理与固定结果消费的可组合业务步骤；字段解释由连接提供。"""

import json
from pathlib import Path

from ai4e_core.abilities.data.save.array_manifest import read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json


def predict_windows(records, read, predict, directory):
    """逐窗口读取、预测并保存；清单只发布完整成功结果。"""
    root = Path(directory)
    root.mkdir(parents=True, exist_ok=True)
    output = []
    for index, record in enumerate(records):
        sample = read(record)
        arrays, metadata = predict(sample)
        result = save_arrays(
            root / f"window_{index:04d}", arrays, kind="field-window-result-v1", metadata=metadata
        )
        output.append(result)
    if not output:
        raise ValueError("没有预测窗口")
    path = root / "results.json"
    save_json(path, {"kind": "field-window-list-v1", "windows": output})
    return str(path.resolve())


def analyze_windows(results, analyze, directory):
    """仅读取固定结果并调用普通分析函数，不构建模型。"""
    manifest = json.loads(Path(results).read_text())
    if manifest.get("kind") != "field-window-list-v1":
        raise ValueError("结果清单类型错误")
    reports = []
    for path in manifest["windows"]:
        record, arrays = read_arrays(path, kind="field-window-result-v1")
        reports.append({"metadata": record["metadata"], "metrics": analyze(arrays), "source": path})
    output = Path(directory) / "metrics.json"
    save_json(output, {"kind": "field-window-metrics-v1", "results": reports})
    return str(output.resolve())


def extend_windows(results, derive, directory):
    """通过用户普通函数派生字段，保存新结果；原结果保持不变。"""
    manifest = json.loads(Path(results).read_text())
    output = []
    for index, path in enumerate(manifest["windows"]):
        record, arrays = read_arrays(path, kind="field-window-result-v1")
        additions = derive(arrays)
        if set(additions) & set(arrays):
            raise ValueError("新增字段不能覆盖原预测")
        result = save_arrays(
            Path(directory) / f"window_{index:04d}",
            {**arrays, **additions},
            kind="field-window-result-v1",
            metadata=record["metadata"],
        )
        output.append(result)
    path = Path(directory) / "results.json"
    save_json(path, {"kind": "field-window-list-v1", "windows": output})
    return str(path.resolve())
