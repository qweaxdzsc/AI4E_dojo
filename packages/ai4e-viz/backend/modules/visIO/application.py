"""可视化资产保存、引用和导出用例门面。"""

from .repository import create_visualization, get_visualization, list_visualizations

__all__ = ["create_visualization", "get_visualization", "list_visualizations"]


def save_scoped(context: dict, body: dict) -> dict:
    """校验固定数据绑定后提交轻量配置，Router 不编排持久化事务。"""
    from modules.dataAssets import resolve_external
    from .save import save_asset
    for source in body['spec']['sources']:
        resolve_external(source, context['bindings'])
    return save_asset(context['scope'], body['spec'], name=body['name'], visualization_id=body.get('visualization_id'), expected_revision=body.get('expected_revision', 0), request_id=body.get('request_id'))


def save_catalog(context: dict, artifact_id: str, body: dict) -> dict:
    """旧图表入口沿用渲染方法，新保存仅冻结来源与参数。"""
    from pathlib import Path
    from modules.dataAssets import get_artifact, source_fingerprint
    from modules.visDatasets import recommend_artifact
    from modules.visTaskManage import validate_visualization_parameters
    stored = get_artifact(artifact_id)
    recommendation = recommend_artifact(artifact_id)
    selected = next((item for item in recommendation.get('detected_candidates', recommendation.get('candidates', [])) if item['recommendation_id'] == body['recommendation_id']), None)
    if selected is None or recommendation.get('blocked'):
        raise ValueError('unknown_or_blocked_recommendation')
    normalized, errors = validate_visualization_parameters(selected['function_id'], stored.get('profile') or {}, selected.get('encoding') or {}, body.get('parameters', {}))
    if errors:
        raise ValueError('parameter_validation_failed: ' + str(errors))
    ref = {'asset_id': artifact_id, 'revision': source_fingerprint(Path(stored['file_path']))}
    source = {'id': 'catalog-source', 'ref': ref, 'catalog': True}
    context['bindings'] = [b for b in context['bindings'] if b['ref']['asset_id'] != artifact_id] + [{'ref': ref, 'path': stored['file_path']}]
    spec = {'schema_version': 1, 'kind': selected['kind'], 'sources': [source], 'method': {'function_id': selected['function_id'], 'recommendation_id': selected['recommendation_id'], 'renderer': selected['renderer']}, 'parameters': normalized}
    saved = save_scoped(context, {'spec': spec, 'name': body.get('name', stored['name']), 'visualization_id': body.get('base_spec_id'), 'expected_revision': body.get('base_version', 0), 'request_id': body.get('request_id')})
    return {**saved, 'spec_id': saved['visualization_id'], 'spec_version': saved['revision']}


def read_catalog(context: dict, identity: str, revision=None, base_url='') -> dict:
    """重新执行旧图表渲染，数组只存在响应中，不写入 spec。"""
    from pathlib import Path
    from modules.dataAssets import get_artifact, source_fingerprint
    from modules.visDatasets import build_example
    from .save import read_asset
    saved = read_asset(context['scope'], identity, revision)
    spec = saved['spec']
    if not spec.get('method'):
        return saved
    ref = spec['sources'][0]['ref']
    stored = get_artifact(ref['asset_id'])
    if source_fingerprint(Path(stored['file_path'])) != ref['revision']:
        raise ValueError('source_revision_mismatch')
    method = spec['method']
    recommendation_id = method.get('recommendation_id')
    if not recommendation_id:
        from modules.visDatasets import recommend_artifact
        recommendations = recommend_artifact(ref['asset_id'])
        selected = next((candidate for candidate in recommendations.get('detected_candidates', recommendations.get('candidates', [])) if candidate['function_id'] == method['function_id']), None)
        if selected is None:
            raise ValueError('configured_method_not_available_for_source')
        recommendation_id = selected['recommendation_id']
    return {**saved, 'artifact_id': ref['asset_id'], 'spec_id': identity, 'spec_version': saved['revision'], 'recommendation_id': recommendation_id, 'parameters': spec['parameters'], 'payload': build_example(ref['asset_id'], base_url, recommendation_id, spec['parameters'])}


def materialize_reference(context: dict, reference: dict, exports) -> dict:
    """报告显式导出时按固定修订请求物理场 PNG，复用唯一生产链。"""
    import time
    from .save import read_asset
    from .exportRepository import get_export, export_root
    if any(reference.get(key) != context['scope'][key] for key in ('project_id', 'task_id')):
        raise ValueError('report_visualization_scope_mismatch')
    saved = read_asset(context['scope'], reference['visualization_id'], reference['revision'])
    if saved['content_hash'] != reference['content_hash']:
        raise ValueError('report_visualization_revision_mismatch')
    output = exports.create(context, saved['visualization_id'], saved['revision'], {'format': 'png', 'view': reference.get('view', 0)})
    for _ in range(600):
        status = get_export(context['scope'], saved['visualization_id'], output['export_id'])
        if status['status'] != 'running':
            if status['status'] != 'succeeded':
                raise ValueError(status.get('error', 'report_visualization_export_failed'))
            return {'manifest': status, 'path': export_root(context['scope'], saved['visualization_id'], output['export_id'])/status['files'][0]['name']}
        time.sleep(.1)
    exports.cancel(context['scope'], saved['visualization_id'], output['export_id'])
    raise ValueError('report_visualization_export_timeout')


def read_fixed_reference(context: dict, reference: dict, base_url='') -> dict:
    """报告按固定任务、配置修订及内容摘要读取，动态运行字段不进入报告配置。"""
    if any(reference.get(key) != context['scope'][key] for key in ('project_id', 'task_id')):
        raise ValueError('report_visualization_scope_mismatch')
    saved = read_catalog(context, reference['visualization_id'], reference['revision'], base_url)
    if saved['content_hash'] != reference['content_hash']:
        raise ValueError('report_visualization_revision_mismatch')
    return saved
