"""两个正式扩展的仓库外物化、真实训练、Task恢复及固定结果消费。"""

import copy
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
import torch

ROOT = Path(__file__).resolve().parents[2]


def _run(args, *, cwd, env=None, timeout=180):
    result = subprocess.run(
        args, cwd=cwd, env=env, text=True, capture_output=True, timeout=timeout, check=False
    )
    assert result.returncode == 0, result.stdout + result.stderr
    return result


def _equal(a, b):
    if isinstance(a, torch.Tensor):
        torch.testing.assert_close(a, b, atol=0, rtol=0)
    elif isinstance(a, np.ndarray):
        np.testing.assert_array_equal(a, b)
    elif isinstance(a, dict):
        assert a.keys() == b.keys()
        for key in a:
            _equal(a[key], b[key])
    elif isinstance(a, (tuple, list)):
        assert len(a) == len(b)
        for first, second in zip(a, b, strict=True):
            _equal(first, second)
    else:
        assert a == b


def _module(path):
    spec = importlib.util.spec_from_file_location("extension_local", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_validation_split_is_disjoint_and_preserves_source(monkeypatch):
    from tests.integration.test_epoch_stream import capability

    monkeypatch.setitem(
        sys.modules, "ai4e_core.abilities.training.selection", capability("selection")
    )
    component = _module(ROOT / "examples/recipe_extensions/research_state/local_components.py")
    original = [
        {"id": str(i), "split": "train" if i < 8 else "test", "index": i} for i in range(11)
    ]
    split = component.validation_samples(original, 3)
    assert [s["id"] for s in split if s["split"] == "validation"] == ["5", "6", "7"]
    assert all(s["source_split"] == "train" for s in split if s["split"] == "validation")
    assert split[8:] == original[8:] and all(s["split"] == "train" for s in original[:8])
    with pytest.raises(ValueError):
        component.validation_samples(original, 8)


@pytest.mark.parametrize("damage", ["missing_weights", "wrong_source", "wrong_shape"])
def test_research_selection_rejects_unpaired_state_without_mutation(monkeypatch, damage):
    from tests.integration.test_epoch_stream import capability

    monkeypatch.setitem(
        sys.modules, "ai4e_core.abilities.training.selection", capability("selection")
    )
    component = _module(ROOT / "examples/recipe_extensions/research_state/local_components.py")
    model = torch.nn.Linear(1, 1)
    policy = component.ResearchSelection(model, contract={"data": "fixed"})
    policy.selector.commit(0.5, step=2, source="ema")
    policy.selected = {
        "model": copy.deepcopy(model.state_dict()),
        "updates": 2,
        "source": "ema",
        "value": 0.5,
        "contract": {"data": "fixed"},
    }
    policy.evaluations = [{"updates": 2, "raw": 0.7, "ema": 0.5}]
    before = policy.state_dict()
    broken = copy.deepcopy(before)
    if damage == "missing_weights":
        broken["selected"] = None
    elif damage == "wrong_source":
        broken["selected"]["source"] = "raw"
    else:
        broken["selected"]["model"]["weight"] = torch.zeros(3, 3)
    with pytest.raises((ValueError, RuntimeError)):
        policy.load_state_dict(broken)
    _equal(policy.state_dict(), before)


@pytest.fixture(scope="module")
def runtime(tmp_path_factory):
    """可选择主会话当前源码运行时；最终验收使用配套真实wheel。"""
    supplied = os.environ.get("DOJO_RESEARCH_EXTENSION_RUNTIME")
    if supplied:
        return Path(supplied)
    folder = tmp_path_factory.mktemp("extension-wheel")
    wheels, installed = folder / "wheels", folder / "installed"
    for package in ("ai4e-spec", "ai4e-core", "ai4e-contrib", "ai4e-task"):
        _run(["uv", "build", "--package", package, "--wheel", "--out-dir", str(wheels)], cwd=ROOT)
    _run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        cwd=folder,
    )
    return installed


@pytest.mark.parametrize("name", ["tail_batch", "research_state"])
def test_external_copy_direct_task_resume_and_fixed_post(tmp_path, runtime, name):
    """每例真实改batch、换loss、加派生数组；direct与Task共用完整目录。"""
    env = {
        **os.environ,
        "PYTHONPATH": str(runtime),
        "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "1",
        "VECLIB_MAXIMUM_THREADS": "1",
    }
    probe = tmp_path / "exercise.py"
    probe.write_text(EXERCISE)
    result = _run(
        [sys.executable, str(probe), str(tmp_path), name, str(ROOT)],
        cwd=tmp_path,
        env=env,
        timeout=240,
    )
    (tmp_path / "console.txt").write_text(result.stdout + result.stderr)
    report = json.loads((tmp_path / "acceptance.json").read_text())
    assert report["passed"] and report["uninterrupted_equal"] and report["prediction_exact"]
    assert report["tail_size"] == 2 and report["derived_consumed"] and report["post_without_model"]
    assert report["task_status"] == "succeeded"
    assert Path(report["runtime"]["core"]).is_relative_to(runtime)
    if name == "research_state":
        assert report["validation_ids"] == ["train_0005", "train_0006", "train_0007"]
        assert report["selection_restored"] and report["selected_weight_matches"]


# 此程序位于仓库外，通过安装公开API运行；测试数据仅证明连接，不代表科学精度。
EXERCISE = r"""
import copy,json,sys,subprocess,shutil
from pathlib import Path
import numpy as np
import torch,yaml
from scipy.io import savemat
import ai4e_task as task
import ai4e_core
from ai4e_core.abilities.data.save.array_manifest import read_arrays
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs

root,name,repo=Path(sys.argv[1]),sys.argv[2],Path(sys.argv[3])
code=root/'case'
info=task.copy_example('recipe_extensions.'+name,code)
assert (code/info['documentation']['entry']).is_file()
raw=root/'raw';raw.mkdir()
rng=np.random.default_rng(123)
for suffix,count in [('smooth1',8),('smooth2',3)]:
    coeff=rng.uniform(1,3,(count,11,11)).astype('float32')
    sol=(coeff*.3+rng.uniform(.1,.2,coeff.shape)).astype('float32')
    savemat(raw/f'piececonst_r421_N1024_{suffix}.mat',{'coeff':coeff,'sol':sol})
# 缩小来源数量是本测试明确的用户组件适配；库不改造或下载科学数据。
p=code/'rawprep.py';s=p.read_text();s=s.replace('from configuration import validate',
'from configuration import validate\nfrom ai4e_contrib.application.datasets.darcy_flow import DarcySource')
s=s.replace('source = binding.source(cfg["inputs"]["rawprep"]["source"])',
'source = DarcySource(cfg["inputs"]["rawprep"]["source"], train_count=8, evaluation_count=3)')
p.write_text(s)
# 替换已定义公开loss，同时新增实际保存并由post消费的量。
(code/'user_variants.py').write_text('# 用户损失与派生误差。\nimport numpy as np\nfrom ai4e_core.abilities.constraint.relative_norm import relative_norm\n\ndef loss(prediction,target):\n    return relative_norm(prediction,target,reduction="none").square().mean()\n\ndef derived(arrays):\n    return {"signed_error": arrays["prediction"]-arrays["target"]}, {"signed_error": {"units":"benchmark","axes":["sample","time","entity","channel"]}}\n\ndef consume(arrays,descriptions):\n    np.testing.assert_array_equal(arrays["signed_error"],arrays["prediction"]-arrays["target"])\n    return {"max_abs_error":float(np.abs(arrays["signed_error"]).max())}\n')
cfg=yaml.safe_load((code/'config.yaml').read_text())
cfg['inputs']['rawprep']['source']=str(raw)
cfg['model'].update(n_layers=1,n_hidden=16,n_head=2,slice_num=4,structured_shape=[3,3])
cfg['train'].update(batch_size=3,updates=4,device='cpu',checkpoint_every=3,seconds=120)
cfg['infer'].update(batch_size=2,device='cpu')
cfg['components'].update(loss='user_variants.loss',derived='user_variants.derived',consume='user_variants.consume')
if name=='research_state': cfg['train'].update(validation_count=3,evaluate_every=2)
cfg['run_root']=str(root/'records');cfg['data_root']=str(root/'data')

def direct(config,entry='pipeline'):
    (code/'config.yaml').write_text(yaml.safe_dump(config,sort_keys=False))
    p=subprocess.run([sys.executable,str(code/(entry+'.py'))],cwd=root,text=True,capture_output=True,timeout=120)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
    path=max(Path(config['run_root']).glob('*/summary.json'),key=lambda p:p.stat().st_mtime_ns)
    return json.loads(path.read_text())

prep=copy.deepcopy(cfg);prep['pipeline']['stages']=['rawprep','trainprep']
prepared=direct(prep)['reports']['trainprep']['preparation']
cfg['pipeline']['stages']=['train','infer','post']
cfg['inputs']['train']['preparation']=prepared;cfg['inputs']['infer']['preparation']=prepared
# 原始训练统计不看留出的validation，更不看test。
if name=='research_state':
    record,train=read_field_inputs(prepared,'train')
    vr,validation=read_field_inputs(prepared,'validation')
    assert len(train['target'])==5 and len(validation['target'])==3
    assert not set(record['metadata']['ids']) & set(vr['metadata']['ids'])
    assert record['metadata']['statistics']==vr['metadata']['statistics']
    expected=__import__('scipy').io.loadmat(raw/'piececonst_r421_N1024_smooth1.mat')['coeff'][:5,::5,::5]
    assert abs(record['metadata']['statistics']['coeff']['mean'][0]-float(expected.mean()))<1e-6
project=root/'project';task.create_project(project)
current=task.new_task(project,name,source=code,configuration=cfg)

def managed(config):
    task.replace_configuration(project,current['id'],config,revision=task.read_configuration(project,current['id'])['revision'])
    item=task.submit_run(project,current['id'])
    finished=task.wait_run(project,item['id'],timeout=120,interval=.1)
    if finished['status']!='succeeded':
        logs='\n'.join(p.read_text(errors='replace')[-5000:] for p in (project/finished['run_path']).rglob('*.log'))
        raise RuntimeError(str(finished)+logs)
    return json.loads((project/finished['run_path']/'summary.json').read_text()),finished

def checkpoint(report):
    r=report['reports']['train']
    return torch.load(r.get('resume_checkpoint',r['checkpoint']),map_location='cpu',weights_only=False)

def equal(a,b):
    if isinstance(a,torch.Tensor):torch.testing.assert_close(a,b,rtol=0,atol=0)
    elif isinstance(a,np.ndarray):np.testing.assert_array_equal(a,b)
    elif isinstance(a,dict):
        assert a.keys()==b.keys()
        for k in a:equal(a[k],b[k])
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b)
        for x,y in zip(a,b):equal(x,y)
    else:assert a==b,(a,b)

def compare(a,b):
    first,second=checkpoint(a),checkpoint(b)
    for key in ['model','optimizer','scheduler','stream','history','updates','user_state','ema']:
        if key in first:equal(first[key],second[key])
    _,x=read_arrays(a['reports']['infer']['results'],kind='named-field-result-v1')
    _,y=read_arrays(b['reports']['infer']['results'],kind='named-field-result-v1')
    equal(x,y)

first=direct(cfg);other,done=managed(cfg);compare(first,other)
if name=='research_state':
    for summary in (first,other):
        previous=Path(summary['reports']['train']['checkpoint'])
        previous.rename(previous.with_suffix('.withheld'))
a,b=copy.deepcopy(cfg),copy.deepcopy(cfg)
for config,summary in [(a,first),(b,other)]:
    config['train']['updates']=6
    record=summary['reports']['train'];config['inputs']['train']['resume']=record.get('resume_checkpoint',record['checkpoint'])
resumed=direct(a);managed_resume,done=managed(b);compare(resumed,managed_resume)
full=copy.deepcopy(cfg);full['train']['updates']=6
uninterrupted=direct(full);compare(resumed,uninterrupted)
# 独立infer直接消费选定权重，不能隐式读latest。
inf=copy.deepcopy(cfg);inf['pipeline']['stages']=['infer']
inf['inputs']['infer']['checkpoint']=resumed['reports']['train']['checkpoint']
independent=direct(inf,entry='infer')
_,a_pred=read_arrays(resumed['reports']['infer']['results'],kind='named-field-result-v1')
_,b_pred=read_arrays(independent['reports']['infer']['results'],kind='named-field-result-v1')
equal(a_pred,b_pred)
# 复制固定预测后隐藏模型入口、准备和训练/推理权重路径；post仍须读回派生量。
fixed=root/'fixed';shutil.copytree(Path(resumed['reports']['infer']['results']).parent,fixed)
for script in ('train.py','infer.py'):(code/script).write_text('raise RuntimeError("must not import model stage")\n')
post=copy.deepcopy(cfg);post['pipeline']['stages']=['post'];post['inputs']['post']['results']=str(fixed/'manifest.json')
post['inputs']['train']['preparation']=None;post['inputs']['infer']['preparation']=None
post_report=direct(post,entry='post')
metrics=json.loads(Path(post_report['reports']['post']['metrics']).read_text())
assert 'max_abs_error' in metrics['derived']
report={'passed':True,'uninterrupted_equal':True,'prediction_exact':True,'post_without_model':True,
        'derived_consumed':True,'tail_size':resumed['reports']['train']['tail_size'],
        'task_status':done['status'],'runtime':{'core':ai4e_core.__file__,'task':task.__file__},
        'direct':resumed,'managed':managed_resume}
if name=='research_state':
    state=checkpoint(resumed);policy=state['user_state']['values']['selection']
    selected=torch.load(resumed['reports']['train']['checkpoint'],weights_only=False)
    assert 'effective_config' in selected  # writer追加来源信息，科学载荷逐项核对
    equal({key:selected[key] for key in policy['selected']},policy['selected'])
    report.update(selection_restored=True,selected_weight_matches=True,validation_ids=vr['metadata']['ids'])
(root/'acceptance.json').write_text(json.dumps(report,indent=2))
"""
