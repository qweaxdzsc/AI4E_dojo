"""本地普通组件：改变网络初始读出并发布带单位的温降数组。"""
import json
import shutil
from pathlib import Path

import numpy as np
import torch

from ai4e_contrib.ability.model.pcno import build_model as original
from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.applications.geothermal.post import read_results


def build_model(**kwargs):
    """兼容原签名；改变最后一个参数的初值以验证替换实际生效。"""
    model = original(**kwargs)
    with torch.no_grad():
        list(model.parameters())[-1].add_(0.01)
    return model


def temperature_drop(source, output):
    """计算每例第1至20年平均场温降，单位K；复制固定结果且不改原结果。"""
    record, arrays = read_results(source)
    root = Path(source).parent
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    for sample in record['samples']:
        shutil.copyfile(root / sample['file'], output / sample['file'])
    values = np.asarray([float((a['Temp'][..., 1] - a['Temp'][..., -1]).mean()) for a in arrays])
    target = output / 'temperature_drop.npy'
    np.save(target, values, allow_pickle=False)
    record.pop('derived_values', None)
    record['derived'] = {'temperature_drop': {'file': target.name, 'sha256': digest(target),
        'sample_ids': [s['id'] for s in record['samples']], 'unit': 'K', 'axes': ['sample']}}
    result = output / 'results.json'
    save_json(result, record)
    return str(result)
