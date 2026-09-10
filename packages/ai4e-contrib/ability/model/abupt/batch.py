"""按固定域布局收批，支持不等几何点数和独立目标。"""

from ai4e_core.abilities.training.batch import concatenate_geometry, stack


def collate(samples):
    """递归堆叠同形张量，几何索引按实际点数偏移。"""
    if not samples:
        raise ValueError("批次不能为空")
    inputs = [s["inputs"] for s in samples]
    if any(set(v) != set(inputs[0]) for v in inputs):
        raise ValueError("同批输入域和可选字段必须一致")
    if len({len(v["geometry_supernode_idx"]) for v in inputs}) != 1:
        raise ValueError("同批超节点数量必须一致")
    geometry = concatenate_geometry(
        [v["geometry_position"] for v in inputs], [v["geometry_supernode_idx"] for v in inputs]
    )

    def merge(values):
        if isinstance(values[0], dict):
            if any(set(v) != set(values[0]) for v in values):
                raise ValueError("同批字段布局不一致")
            return {k: merge([v[k] for v in values]) for k in values[0]}
        return stack(values)

    result = {
        "geometry_position": geometry["position"],
        "geometry_supernode_idx": geometry["indices"],
        "geometry_batch_idx": geometry["batch"],
    }
    result.update(
        {k: merge([v[k] for v in inputs]) for k in inputs[0] if not k.startswith("geometry_")}
    )
    return {
        "inputs": result,
        "targets": merge([s["targets"] for s in samples]),
        "metadata": [s["metadata"] for s in samples],
    }
