"""外部来源是只读绑定，实际位置只存在运行上下文，不进入保存配置。"""
from pathlib import Path
import hashlib
from infrastructure.storage.atomic import contained


def fingerprint(path: Path) -> str:
    """流式计算文件或目录成员身份，不复制原数据。"""
    digest = hashlib.sha256()
    paths = sorted(p for p in path.rglob('*') if p.is_file()) if path.is_dir() else [path]
    for entry in paths:
        if path.is_dir():
            if not entry.resolve().is_relative_to(path.resolve()):
                raise ValueError('source_member_outside_root')
            digest.update(str(entry.relative_to(path)).encode())
            digest.update(fingerprint(entry).encode())
            continue
        with entry.open('rb') as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b''):
                digest.update(block)
    return digest.hexdigest()


def resolve_external(source: dict, bindings: list[dict]) -> dict:
    """按固定引用解析宿主授权绑定，缺失和内容变化分别报错。"""
    ref = source['ref']
    binding = next((b for b in bindings if all(b['ref'].get(k) == ref.get(k) for k in ('project_id', 'asset_id', 'revision', 'member'))), None)
    if binding is None:
        raise ValueError('source_binding_missing: ' + ref['asset_id'])
    path = Path(binding['path']).resolve()
    if not path.exists():
        raise FileNotFoundError('source_missing: ' + ref['asset_id'])
    if fingerprint(path) != binding.get('fingerprint', ref['revision']):
        raise ValueError('source_revision_mismatch: ' + ref['asset_id'])
    if source.get('data_revision') and source['data_revision'] != binding.get('data_revision'):
        raise ValueError('source_revision_mismatch')
    for dependency in binding.get('dependencies', []):
        child = contained(path.parent, dependency['member'])
        if not child.is_file() or fingerprint(child) != dependency['revision']:
            raise ValueError('source_revision_mismatch')
    return {**binding, 'path': path}


def dependency_snapshot(path: Path) -> list[dict]:
    """固定复合 VTK 的递归成员；阻止 XML 越界、循环与遗漏深层数据修订。"""
    import xml.etree.ElementTree as ET
    path = path.resolve()
    entries, visited = [], {path}

    def collect(current):
        """递归收集去重后的授权成员。"""
        if current.suffix.lower() not in ('.pvd', '.vtm', '.pvtu', '.pvti', '.pvtp', '.pvtr', '.pvts'):
            return
        for node in ET.parse(current).iter():
            member = node.attrib.get('file') or node.attrib.get('Source')
            if not member:
                continue
            child = (current.parent / member).resolve()
            if not child.is_relative_to(path.parent) or not child.is_file():
                raise ValueError('source_member_outside_root_or_missing')
            if child in visited:
                continue
            visited.add(child)
            entries.append({'member': child.relative_to(path.parent).as_posix(), 'revision': fingerprint(child)})
            collect(child)
    collect(path)
    return entries
