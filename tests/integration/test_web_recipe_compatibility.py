"""页面配置只改变任务副本，原模板及未涉及阶段保持不变。"""
import hashlib
from tests.integration.test_web_project_task import platform, RECIPE


def digest_tree(root):
    """跳过解释器缓存，仅核对案例交付文件。"""
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc'}


def test_template_unchanged_and_custom_script_refused(platform):
    c,p,t,_,_=platform
    before=digest_tree(RECIPE)
    url=f'/api/v1/projects/{p}/tasks/{t["id"]}/rawprep'
    cfg=c.get(url).json();cfg['rawprep']['vtkhdf']=True
    saved=c.put(url,json=cfg);assert saved.status_code==200
    assert digest_tree(RECIPE)==before
    base=c.app.state.services.project(p)
    script=base/'tasks'/t['id']/'recipe/rawprep.py';script.write_text(script.read_text()+'\n# user customization\n')
    rejected=c.put(url,json=saved.json());assert rejected.status_code==400 and 'recipe_profile_changed' in rejected.text
    assert digest_tree(RECIPE)==before
