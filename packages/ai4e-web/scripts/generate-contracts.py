"""根据 FastAPI OpenAPI 与稳定检查契约生成请求类型，避免另写一份接口字段。"""
from pathlib import Path
from tempfile import TemporaryDirectory
from ai4e_server.bootstrap.app import create_app
from ai4e_server.bootstrap.settings import Settings


def typename(schema):
    """将本期 JSON schema 子集映射成 TypeScript 类型。"""
    if not isinstance(schema, dict):return 'unknown'
    if '$ref' in schema:return schema['$ref'].split('/')[-1]
    if 'anyOf' in schema:return ' | '.join(typename(v) for v in schema['anyOf'])
    if 'enum' in schema:return ' | '.join(__import__('json').dumps(v) for v in schema['enum'])
    t=schema.get('type')
    if t=='array':return '('+typename(schema.get('items',{}))+')[]'
    if t=='object':
        if schema.get('properties'):
            return '{ ' + '; '.join(k + ('' if k in schema.get('required',[]) else '?') + ': ' + typename(v) for k,v in schema['properties'].items()) + ' }'
        return 'Record<string, '+typename(schema.get('additionalProperties',{}))+'>'
    return {'string':'string','number':'number','integer':'number','boolean':'boolean','null':'null'}.get(t,'unknown')


if __name__=='__main__':
    with TemporaryDirectory() as directory:
        api=create_app(Settings(Path(directory),Path('.'))).openapi()
    result=['/** 自动生成：uv run packages/ai4e-web/scripts/generate-contracts.py。 */']
    for name,schema in sorted(api['components']['schemas'].items()):
        result.append('export interface '+name+' {')
        for key,value in schema.get('properties',{}).items():
            optional='' if key in schema.get('required',[]) else '?'
            result.append('  '+key+optional+': '+typename(value)+';')
        result.append('}')
    target=Path(__file__).resolve().parents[1]/'src/infrastructure/contracts/api.generated.ts'
    target.parent.mkdir(parents=True,exist_ok=True);target.write_text('\n'.join(result)+'\n')
