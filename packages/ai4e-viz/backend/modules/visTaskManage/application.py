"""可视化任务应用用例门面。

本层统一承接参数校验与 ``VisualizationSpec`` 版本编排，供 ``visIO`` 等一级模块通过
公开门面调用。调用方不需要了解方法目录、JSON Schema 或 Repository 的内部布局。
"""

from __future__ import annotations

from typing import Any

from .repository import append_version, create_spec, get_version, list_specs, list_versions
from .catalog import FUNCTIONS
from .parameterRegistry import normalize_and_validate


def validate_visualization_parameters(
    function_id: str,
    profile: dict[str, Any],
    encoding: dict[str, Any],
    parameters: object,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """按已注册方法合并默认值并校验参数。

    返回规范参数和结构化错误列表；方法不存在时抛出 ``KeyError``，由调用模块转换为
    自己的协议错误。该用例不写数据库，也不承担 HTTP 错误转换。
    """

    function = next((item for item in FUNCTIONS if item["id"] == function_id), None)
    if function is None:
        raise KeyError(function_id)
    return normalize_and_validate(function, profile, encoding, parameters)


def save_visualization_spec(
    spec_payload: dict[str, Any],
    *,
    spec_id: str,
    created_by: str,
    base_spec_id: str | None = None,
    base_version: int | None = None,
) -> dict[str, Any]:
    """创建首版或在显式基线之上追加不可变 Spec 版本。

    Repository 的 ``KeyError``、``FileExistsError`` 与 ``RuntimeError`` 原样保留，调用方
    据此映射 404、409 等协议；事务边界始终留在本模块 Repository。
    """

    if base_spec_id:
        if not isinstance(base_version, int):
            raise ValueError("base_version is required")
        return append_version(base_spec_id, base_version, spec_payload, created_by)
    return create_spec(spec_id, spec_payload, created_by)

__all__ = [
    "append_version", "create_spec", "get_version", "list_specs", "list_versions",
    "save_visualization_spec", "validate_visualization_parameters",
]


def save_method_config(context: dict, payload: dict, identity=None, expected_revision=0):
    """原方法编辑器保存到目标任务，保留参数协议但不再写全局 SQLite。"""
    from pathlib import Path
    from modules.dataAssets import get_artifact, source_fingerprint
    from modules.visIO import save_asset
    try:
        source = get_artifact(payload['artifact_id'])
        path = Path(source['file_path'])
    except KeyError:
        from .examples import CASES
        if payload['artifact_id'] not in CASES:
            raise
        path = Path(__file__).with_name('examples.py')
    ref = {'asset_id': payload['artifact_id'], 'revision': source_fingerprint(path)}
    spec = {'schema_version': 1, 'kind': payload['kind'], 'sources': [{'id': 'catalog-source', 'ref': ref, 'catalog': True}], 'method': {'function_id': payload['function_id']}, 'parameters': payload['params']}
    record = save_asset(context['scope'], spec, name=payload['function_id'], visualization_id=identity, expected_revision=expected_revision)
    return {**payload, 'spec_id': record['visualization_id'], 'version': record['revision']}
