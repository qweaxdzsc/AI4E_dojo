"""报告查询、版本冻结、复制和导出任务的应用门面。"""

from .repository import create_export, create_report, duplicate_report, freeze_report, get_export, get_report_version, list_reports

__all__ = ["create_export", "create_report", "duplicate_report", "freeze_report", "get_export", "get_report_version", "list_reports"]


def resolve_visualization_reference(context: dict, reference: dict, exports) -> dict:
    """报告引用固定配置修订，输出由 visIO 管理，不读取其内部存储。"""
    from modules.visIO import materialize_reference
    if not all(reference.get(key) for key in ('visualization_id', 'revision', 'content_hash')):
        raise ValueError('fixed_visualization_reference_required')
    return materialize_reference(context, reference, exports)
