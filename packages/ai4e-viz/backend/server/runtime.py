"""服务装配的上下文能力注册；存储路径只能由可信宿主或 CLI 注入。"""
import os
import secrets
from pathlib import Path
import hashlib
import json
from modules.dataAssets import dependency_snapshot, source_fingerprint
from modules.visPhysField import Sessions
from modules.visIO import Exports


class Runtime:
    """每实例独立上下文、会话与导出生命周期。"""
    def __init__(self):
        """默认四个工作区，断连十五分钟回收。"""
        self.contexts = {}
        self.sessions = Sessions(
            int(os.getenv('AI4E_VIS_MAX_SESSIONS', '4')),
            int(os.getenv('AI4E_VIS_SESSION_TTL', '900')),
            int(os.getenv('AI4E_VIS_SESSION_IDLE', '45')),
        )
        self.exports = Exports()
        self.control_token = os.getenv('AI4E_VIS_CONTROL_TOKEN', secrets.token_urlsafe(32))

    def register(self, body):
        """注册可信宿主提供的存储及数据绑定，公开只返回不透明身份。"""
        body = {**body, 'bindings': [dict(binding) for binding in body.get('bindings', [])], 'sources': [dict(source) for source in body.get('sources', [])]}
        for binding in body['bindings']:
            if 'data_revision' in binding:
                continue
            path = Path(binding['path'])
            dependencies = dependency_snapshot(path)
            binding['dependencies'] = dependencies
            binding['data_revision'] = hashlib.sha256(json.dumps([source_fingerprint(path), dependencies, binding.get('frames', [])], sort_keys=True).encode()).hexdigest()
            for source in body['sources']:
                if source['ref'] == binding['ref']:
                    if source.get('data_revision') and source['data_revision'] != binding['data_revision']:
                        raise ValueError('source_revision_conflict')
                    source['data_revision'] = binding['data_revision']
        identity = secrets.token_hex(32)
        context = {**body, 'context_id': identity}
        self.contexts[identity] = context
        return {'context_id': identity, 'sources': body.get('sources', []), 'writable': bool(body.get('scope', {}).get('writable')), 'project_id': body.get('scope', {}).get('project_id'), 'task_id': body.get('scope', {}).get('task_id')}

    def context(self, identity):
        """解析不透明上下文，未绑定时拒绝保存。"""
        if not identity or identity not in self.contexts:
            raise ValueError('storage_context_required_or_expired')
        return self.contexts[identity]

    def shutdown(self):
        """服务停止时回收全部专属工作。"""
        self.exports.shutdown()
        self.sessions.shutdown()
