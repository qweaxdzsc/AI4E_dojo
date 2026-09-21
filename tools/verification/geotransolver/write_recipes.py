"""初次显式模板脚手架；已有目录拒绝覆盖，后续直接维护公开文件。"""

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]

COMMON = {
    "configuration.py": '''"""本地配置及可替换组件入口。"""
from ai4e_contrib.application.geotransolver import load_configuration,validate,component
__all__=['load_configuration','validate','component']
''',
    "pipeline.py": '''"""Python 决定原始准备、模型准备、训练、预测与固定结果报告顺序。"""
from configuration import load_configuration,validate
from rawprep import rawprep
from trainprep import trainprep
from train import train
from infer import infer
from post import post
from ai4e_core import run


def pipeline(cfg):
    """同一正文由 direct-core 与 Task 执行。"""
    cfg=validate(cfg)
    selected=cfg['pipeline']['stages']
    physical=prepared=trained=results=last=None
    if 'rawprep' in selected:
        last=physical=run.stage('rawprep',rawprep,cfg)
    if 'trainprep' in selected:
        last=prepared=run.stage('trainprep',trainprep,cfg,physical)
    if 'train' in selected:
        last=trained=run.stage('train',train,cfg,prepared)
    if 'infer' in selected:
        last=results=run.stage('infer',infer,cfg,prepared,trained)
    if 'post' in selected:
        last=run.stage('post',post,cfg,results)
    return last

if __name__=='__main__':
    raise SystemExit(run.launch(pipeline,script=__file__,config_loader=load_configuration))
''',
    "rawprep.py": '''"""来源名单、物理读取及逐场 PT/VTKHDF 交付。"""
from configuration import validate
from ai4e_core import run
from ai4e_core.applications.DOMAIN.rawprep import PREPARE
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_contrib.application.DOMAIN.geotransolver import binding


def rawprep(cfg):
    """原始字段和拓扑保存，采样及转点留到模型准备。"""
    cfg=validate(cfg); session=run.TrainingRun()
    if session.dry_run: return None
    source=binding.source(cfg['inputs']['rawprep']['source'])
    result=PREPARE(source.samples(),source.read,session.output_dir('rawprep'),session=session,metadata={'dataset':'CASE'})
    record_bundle(session,'physical',result,kind='dataset',stage='rawprep')
    session.report({'dataset':result},stage='rawprep')
    return result
''',
    "trainprep.py": '''"""显式连接字段抽取、训练统计、编码和几何缓存。"""
from configuration import validate
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.applications.DOMAIN.trainprep import PREPARE
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.abilities.geometry.radius_query import build_radius_cache_arrays
from ai4e_contrib.application.DOMAIN.geotransolver import binding


def trainprep(cfg,physical=None):
    """物理字段保持只读；统计和模型索引写独立准备目录。"""
    cfg=validate(cfg); session=run.TrainingRun()
    if session.dry_run: return None
    physical=resolve_input(physical,cfg['inputs']['trainprep']['dataset'],name='trainprep.dataset')
    caches=None
    if cfg['model'].get('include_local_features',False):
        caches=lambda arrays:build_radius_cache_arrays(arrays['local_positions'],radii=cfg['model']['radii'],neighbors=cfg['model']['neighbors_in_radius'],cache_spec=dict(radii=record['metadata']['declaration']['model']['radii'],neighbors=record['metadata']['declaration']['model']['neighbors_in_radius']))
    prepared=PREPARE(physical,session.output_dir('trainprep'),extract=binding.extract,statistics=binding.statistics,transform=binding.transform,caches=caches,declaration={'case':'CASE','fields':binding.FIELDS,'times':binding.TIMES,'model':cfg['model']})
    record_bundle(session,'prepared',prepared,kind='preparation',stage='trainprep')
    session.report({'preparation':prepared},stage='trainprep')
    return prepared
''',
    "train.py": '''"""显式选择网络、取批、解码目标和优化策略；core 执行训练及恢复。"""
from functools import partial
import time
import torch
from configuration import validate,component
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs
from ai4e_core.applications.DOMAIN.train import FIT
from ai4e_core.abilities.inference.prediction import named_array_batch
from ai4e_core.abilities.constraint.relative_norm import supervised_objective
from ai4e_core.abilities.training.iteration_stream import IterationStream
from ai4e_core.abilities.training.cancellation import cancellation
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
from ai4e_contrib.application.geotransolver import build_model,build_optimizer,build_scheduler
from ai4e_contrib.application.DOMAIN.geotransolver import binding


def train(cfg,prepared=None):
    """更新数为恢复后的累计目标，不静默重置随机游标或学习率日程。"""
    cfg=validate(cfg); session=run.TrainingRun()
    if session.dry_run: return None
    prepared=resolve_input(prepared,cfg['inputs']['train']['preparation'],name='train.preparation')
    record,arrays=read_field_inputs(prepared,'train')
    device=resolve_device(cfg['train']['device']);torch.manual_seed(cfg['seed'])
    model=build_model(cfg['model']).to(device)
    if cfg['model'].get('include_local_features',False):
        install_prepared_queries(model,arrays,radii=cfg['model']['radii'],neighbors=cfg['model']['neighbors_in_radius'],cache_spec=dict(radii=record['metadata']['declaration']['model']['radii'],neighbors=record['metadata']['declaration']['model']['neighbors_in_radius']))
    batch=partial(named_array_batch,arrays,device=device,names=(*binding.INPUT_NAMES,'target','physical_target'))
    decode,target=binding.objective_binding(record['metadata']['statistics'])
    objective=partial(supervised_objective,input_names=binding.INPUT_NAMES,decode=decode,target_name=target,loss=component(cfg['components']['loss']))
    optimizer=build_optimizer(model,lr=cfg['train']['lr'],weight_decay=cfg['train']['weight_decay'])
    stream=IterationStream(len(arrays['target']),cfg['train']['batch_size'],seed=cfg['seed'])
    scheduler=build_scheduler(optimizer,policy=cfg['train']['schedule'],updates_per_epoch=len(arrays['target'])//cfg['train']['batch_size'],epochs=cfg['train']['schedule_epochs'],end_lr=cfg['train']['end_lr'])
    # 数组清单的内容摘要加入恢复合同，跨准备目录复制不会改变身份。
    contract={'model':cfg['model'],'prepared_fields':record['fields'],'metadata':record['metadata'],'loss':cfg['components']['loss'],'lr':cfg['train']['lr'],'schedule':cfg['train']['schedule'],'schedule_epochs':cfg['train']['schedule_epochs'],'end_lr':cfg['train']['end_lr'],'weight_decay':cfg['train']['weight_decay']}
    with cancellation() as stopped:
        result=FIT(model=model,batch=batch,objective=objective,optimizer=optimizer,stream=stream,session=session,updates=cfg['train']['updates'],contract=contract,scheduler=scheduler,resume=cfg['inputs']['train']['resume'],deadline=time.monotonic()+cfg['train']['seconds'],cancelled=stopped,checkpoint_every=cfg['train']['checkpoint_every'])
    session.report(result,stage='train')
    return result
''',
    "infer.py": '''"""固定权重批量预测、物理反变换、拓扑及派生结果交付。"""
from functools import partial
import torch
from configuration import validate,component
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.applications.parametric_pde.trainprep import read_field_inputs
from ai4e_core.applications.DOMAIN.infer import PREDICT
from ai4e_core.applications.base.array_assets import record_bundle
from ai4e_core.abilities.inference.prediction import named_array_batch
from ai4e_core.abilities.modeling.weights import load_mapped_weights
from ai4e_core.abilities.training.optimization import resolve_device
from ai4e_core.abilities.geometry.radius_query import install_prepared_queries
from ai4e_contrib.application.geotransolver import build_model
from ai4e_contrib.application.DOMAIN.geotransolver import binding


def infer(cfg,prepared=None,trained=None):
    """末批不丢弃，保存固定预测供独立 post 消费。"""
    cfg=validate(cfg); session=run.TrainingRun()
    if session.dry_run: return None
    prepared=resolve_input(prepared,cfg['inputs']['infer']['preparation'],name='infer.preparation')
    checkpoint=resolve_input(trained['checkpoint'] if trained else None,cfg['inputs']['infer']['checkpoint'],name='infer.checkpoint')
    record,arrays=read_field_inputs(prepared,binding.EVALUATION)
    model=build_model(cfg['model']).to(resolve_device(cfg['infer']['device']))
    state=torch.load(checkpoint,map_location='cpu',weights_only=False)
    if state['contract']['model']!=cfg['model'] or state['contract']['metadata']['statistics']!=record['metadata']['statistics']:
        raise ValueError('固定权重结构或归一化身份不匹配')
    load_mapped_weights(model,state['model'])
    if cfg['model'].get('include_local_features',False):
        install_prepared_queries(model,arrays,radii=cfg['model']['radii'],neighbors=cfg['model']['neighbors_in_radius'],cache_spec=dict(radii=record['metadata']['declaration']['model']['radii'],neighbors=record['metadata']['declaration']['model']['neighbors_in_radius']))
    batch=partial(named_array_batch,arrays,device=resolve_device(cfg['infer']['device']),names=binding.INPUT_NAMES)
    result=PREDICT(model,prepared,session.output_dir('infer')/'fixed',split=binding.EVALUATION,batch=batch,input_names=binding.INPUT_NAMES,decode=binding.decoder(record['metadata']['statistics'],physical=True),batch_size=cfg['infer']['batch_size'],fields=binding.FIELDS,units=binding.UNITS,times=binding.TIMES,provenance={'updates':state['updates'],'model':cfg['model']},derived=component(cfg['components']['derived']))
    record_bundle(session,'prediction',result,kind='other',stage='infer')
    session.report({'results':result},stage='infer')
    return result
''',
    "post.py": '''"""只消费固定结果和可替换派生数组，不导入网络。"""
from configuration import validate,component
from ai4e_core import run
from ai4e_core.base.config.conventions import resolve_input
from ai4e_core.applications.DOMAIN.post import REPORT
from ai4e_core.applications.base.array_assets import record_bundle


def post(cfg,results=None):
    """CPU float64 评价、表格、误差曲线与场图，记录来源资产。"""
    cfg=validate(cfg);session=run.TrainingRun()
    if session.dry_run:return None
    results=resolve_input(results,cfg['inputs']['post']['results'],name='post.results')
    summary=REPORT(results,session.output_dir('post'),time_unit='TIMEUNIT',consume=component(cfg['components']['consume']))
    asset=record_bundle(session,'fixed-results',results,kind='other',stage='post')
    record_bundle(session,'evaluation',summary['metrics'],kind='other',stage='post')
    session.record_metric('physical_mse',summary['mse'],stage='post',semantics={'space':'physical','reduction':'all_elements','case':'CASE'},assets=[results])
    session.report(summary,stage='post')
    return summary
''',
}


def main():
    """仅生成已维护的显式模板，不安装环境。"""
    for case, domain in [("darcy", "parametric_pde"), ("bumper_beam", "spatiotemporal_pde")]:
        root = ROOT / "recipes/geotransolver" / case
        root.mkdir(parents=True, exist_ok=False)
        for name, body in COMMON.items():
            prep = "prepare_named_fields" if case == "darcy" else "prepare_named_trajectories"
            if name == "trainprep.py":
                prep = "prepare_field_inputs" if case == "darcy" else "prepare_trajectory_inputs"
            body = (
                body.replace("DOMAIN", domain)
                .replace("CASE", case)
                .replace("PREPARE", prep)
                .replace("FIT", "fit_fields" if case == "darcy" else "fit_trajectories")
                .replace(
                    "PREDICT", "predict_fields" if case == "darcy" else "predict_named_trajectories"
                )
                .replace("REPORT", "report_fields" if case == "darcy" else "report_trajectories")
                .replace("TIMEUNIT", "benchmark" if case == "darcy" else "ms")
            )
            if name in {"rawprep.py", "trainprep.py", "train.py", "infer.py", "post.py"}:
                stage = name[:-3]
                body += f'\n\nif __name__ == "__main__":\n    from configuration import load_configuration\n    raise SystemExit(run.launch({{{stage!r}: {stage}}},script=__file__,only=[{stage!r}],config_loader=load_configuration))\n'
            (root / name).write_text(body)
        darcy = case == "darcy"
        model = {
            "functional_dim": 3,
            "out_dim": 1 if darcy else 50,
            "geometry_dim": 3,
            "n_layers": 4 if darcy else 6,
            "n_hidden": 128 if darcy else 256,
            "n_head": 4 if darcy else 8,
            "slice_num": 64 if darcy else 128,
            "use_te": False,
        }
        model.update(
            {"structured_shape": [85, 85]}
            if darcy
            else {
                "global_dim": 3,
                "include_local_features": True,
                "radii": [0.05, 0.25],
                "neighbors_in_radius": [8, 32],
                "n_hidden_local": 32,
            }
        )
        cfg = {
            "seed": 42,
            "run_root": "./runs",
            "data_root": "./data",
            "pipeline": {"stages": ["rawprep", "trainprep", "train", "infer", "post"]},
            "inputs": {
                "rawprep": {"source": None},
                "trainprep": {"dataset": None},
                "train": {"preparation": None, "resume": None},
                "infer": {"preparation": None, "checkpoint": None},
                "post": {"results": None},
            },
            "model": model,
            "train": {
                "updates": 20,
                "batch_size": 4 if darcy else 1,
                "lr": 0.001 if darcy else 0.0001,
                "weight_decay": 0.00001 if darcy else 0.0001,
                "schedule": "warmup_cosine" if darcy else "epoch_cosine",
                "schedule_epochs": 1000 if darcy else 10000,
                "end_lr": 0.0001 if darcy else 0.0000003,
                "device": "cpu",
                "seconds": 120,
                "checkpoint_every": 10,
            },
            "infer": {"batch_size": 4 if darcy else 1, "device": "cpu"},
            "components": {
                "loss": "ai4e_core.abilities.constraint.relative_norm.relative_norm"
                if darcy
                else "torch.nn.functional.mse_loss",
                "derived": None,
                "consume": None,
            },
        }
        (root / "config.yaml").write_text(yaml.safe_dump(cfg, sort_keys=False))
        (root / "README.md").write_text(
            f"# GeoTransolver {case}\n\n可复制的五阶段 Python 研究案例。设置 `inputs.rawprep.source`、`run_root` 和 `data_root` 后，以 `uv run --no-sync python pipeline.py --config config.yaml` 执行。原始数据只读，所有输出使用独立数据根。\n\n"
            + (
                "Darcy 训练1000/评价200；421网格物理保存，85网格模型准备；4层128宽。"
                if darcy
                else "保险杠124训练/7验证；共同11帧，预测10帧全部节点；6层基础256宽，多尺度后320宽。"
            )
            + "\n\n默认20更新及120秒用于短检查，超过阶段预算会保存检查点并失败；恢复设置 `inputs.train.resume` 和累计目标 `train.updates`。调度沿原实验总轮次，短训不压缩日程。论文精度未复现。\n\n独立 post 仅设置 `inputs.post.results` 并选择 `[post]`，无需原数据或网络；可在 `components.loss/derived/consume` 替换普通函数。安装依赖选择 `ai4e-contrib[geotransolver]`，运行不依赖 PhysicsNeMo。\n"
        )
        example = ROOT / "examples/geotransolver" / case
        shutil.copytree(root, example, dirs_exist_ok=True)


if __name__ == "__main__":
    main()
