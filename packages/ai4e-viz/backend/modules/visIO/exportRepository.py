"""任务目录导出记录；成功文件与配置摘要分开保存。"""
from infrastructure.storage.atomic import contained, identity, write_json, read_json
from .assetRepository import asset_root, scope_root


def export_root(scope, asset_id, export_id):
    """解析资产内受控输出位置。"""
    return contained(asset_root(scope, asset_id), 'exports/' + identity(export_id))


def put_export(scope, asset_id, record):
    """原子发布导出状态，不修改 asset.json。"""
    scope_root(scope, write=True)
    write_json(contained(export_root(scope, asset_id, record['export_id']), 'manifest.json'), record)


def get_export(scope, asset_id, export_id):
    """按明确资产和导出身份读取状态。"""
    return read_json(contained(export_root(scope, asset_id, export_id), 'manifest.json'))
