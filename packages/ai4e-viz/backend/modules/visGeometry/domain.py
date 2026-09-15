"""几何可视化领域对象和纯业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GeometryViewState:
    """描述几何视口可持久化的视角状态，不包含O3DV运行时对象。"""

    projection: str = "perspective"
    fit_to_window: bool = True
    selected_node_ids: tuple[str, ...] = ()
    hidden_node_ids: tuple[str, ...] = ()


def normalize_geometry_view(state: GeometryViewState) -> GeometryViewState:
    """校验并规范几何视角，避免UI状态直接污染领域对象。"""

    if state.projection not in {"perspective", "orthographic"}:
        raise ValueError("projection仅支持perspective或orthographic")
    return GeometryViewState(
        projection=state.projection,
        fit_to_window=bool(state.fit_to_window),
        selected_node_ids=tuple(dict.fromkeys(state.selected_node_ids)),
        hidden_node_ids=tuple(dict.fromkeys(state.hidden_node_ids)),
    )
