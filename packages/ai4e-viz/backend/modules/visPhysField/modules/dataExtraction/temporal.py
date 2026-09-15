"""时序提取范围和步长业务规则。"""


def temporal_indices(start: int, stop: int, step: int = 1) -> tuple[int, ...]:
    """生成包含起点、不包含终点的帧索引，规则与Python range一致。"""

    if start < 0 or stop < start or step <= 0:
        raise ValueError("时序提取范围或步长无效")
    return tuple(range(start, stop, step))


def sample_history(source: dict, bindings: list, positions: list) -> list[dict]:
    """按真实时间逐帧采样，不跨缺帧插值，不修改交互工作区。"""
    from modules.dataAssets import resolve_external
    from modules.visDatasets import load_physical, source_times
    from modules.visEngine import probe
    binding = resolve_external(source, bindings)
    times = source_times(binding)
    if not times:
        raise ValueError('temporal_source_required')
    rows = []
    for value in times:
        mesh, _ = load_physical(source, bindings, value)
        for row in probe(mesh, positions):
            rows.append({'time': value, **row})
    return rows
