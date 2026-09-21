"""只读核查发布数据身份、场语义、井标签和重复预测；不拟合统计量。"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import torch
from ai4e_core.abilities.data.save.array_manifest import digest
GRID = (80, 80, 5, 21)

def finite_tensor(value, shape, name):
    """拒绝维度、精度或有限性不符合发布格式的字段。"""
    if not isinstance(value, torch.Tensor) or tuple(value.shape) != tuple(shape):
        raise ValueError(f'{name}: expected tensor {tuple(shape)}')
    if value.dtype != torch.float32 or not torch.isfinite(value).all():
        raise ValueError(f'{name}: expected finite float32')

def inspect_chunk(chunk, name, *, count=3, grid=GRID, labels=True):
    """核对批次及井标签行数，返回稳定的输入身份。"""
    for field in ('pres', 'temp'):
        finite_tensor(chunk.get(field), (count, *grid), f'{name}.{field}')
    finite_tensor(chunk.get('spatial_params'), (count, *grid, 14), f'{name}.spatial_params')
    finite_tensor(chunk.get('global_params'), (count, 4), f'{name}.global_params')
    records = []
    for i in range(count):
        spatial = chunk['spatial_params'][i]
        global_ = chunk['global_params'][i]
        well_map = spatial[..., 2]
        if not torch.equal(well_map, well_map[..., :1].expand_as(well_map)):
            raise ValueError(f'{name}/{i}: well identity changes with time')
        if not torch.isin(well_map, torch.tensor([-1.0, 0.0, 1.0])).all():
            raise ValueError(f'{name}/{i}: unknown well marker')
        producers = int((well_map[..., 0] == -1).any(dim=2).sum())
        injectors = int((well_map[..., 0] == 1).any(dim=2).sum())
        if min(producers, injectors) == 0:
            raise ValueError(f'{name}/{i}: missing injection or production well')
        if labels:
            for key, nwell in [('Temp_wh', producers), ('Heat_wh', producers), ('P_inj', injectors)]:
                values = chunk.get(key)
                if not isinstance(values, (list, tuple)) or len(values) != count:
                    raise ValueError(f'{name}.{key}: expected {count} case labels')
                finite_tensor(values[i], (nwell, grid[-1] - 1), f'{name}/{i}.{key}')
        h = hashlib.sha256()
        for value in (spatial, global_):
            h.update(value.contiguous().numpy().tobytes())
        records.append({'id': f'{name}/{i}', 'input_sha256': h.hexdigest(), 'production_wells': producers, 'injection_wells': injectors})
    return records

def audit(root: Path):
    """核验全部发布文件，声明演示场不是独立真实值。"""
    root = root.resolve()
    chunks = sorted(root.glob('chunk_*.pt'))
    if [p.name for p in chunks] != [f'chunk_{i:02d}.pt' for i in range(8)]:
        raise ValueError('Expected exactly chunk_00.pt through chunk_07.pt')
    files = [*chunks, root / 'Prob_Data.pt', root / 'Prob_Pred.pt', root / 'stats.json']
    hashes = {p.name: digest(p) for p in files}
    stats = json.loads((root / 'stats.json').read_text())
    expected_stats = ['pres', 'temp', 'Pini', 'Tini', 'qinj', 'Tinj', 'ppro', 'perm', 'poro', 'global']
    for field in expected_stats:
        for suffix in ['mean', 'std']:
            key = f'{field}_{suffix}'
            value = torch.as_tensor(stats[key])
            expected = (4,) if field == 'global' else ()
            if tuple(value.shape) != expected or not torch.isfinite(value).all() or (suffix == 'std' and (not (value > 0).all())):
                raise ValueError(f'Invalid frozen statistics: {key}')
    training = []
    for path in chunks:
        values = torch.load(path, map_location='cpu', weights_only=False)
        training.extend(inspect_chunk(values, path.stem))
        del values
    demo = torch.load(root / 'Prob_Data.pt', map_location='cpu', weights_only=False)
    predictions = torch.load(root / 'Prob_Pred.pt', map_location='cpu', weights_only=False)
    demo_records = inspect_chunk(demo, 'Prob_Data', count=18, labels=False)
    duplicates = {}
    for raw, pred in [('pres', 'Pres'), ('temp', 'Temp')]:
        finite_tensor(predictions.get(pred), (18, *GRID), f'Prob_Pred.{pred}')
        duplicates[raw] = torch.equal(demo[raw], predictions[pred])
    for key, well_type in [('Twh', 'production_wells'), ('Hwh', 'production_wells'), ('Ewh', 'production_wells'), ('Pinj', 'injection_wells')]:
        values = predictions.get(key)
        if not isinstance(values, (list, tuple)) or len(values) != 18:
            raise ValueError(f'Prob_Pred.{key}: expected 18 case outputs')
        for i, record in enumerate(demo_records):
            finite_tensor(values[i], (record[well_type], 20), f'Prob_Pred/{i}.{key}')
    finite_tensor(predictions.get('Qout'), (18, 80, 80, 5, 20), 'Prob_Pred.Qout')
    training_ids = {r['input_sha256'] for r in training}
    demo_ids = {r['input_sha256'] for r in demo_records}
    for path in files:
        if digest(path) != hashes[path.name]:
            raise ValueError(f'Source changed during audit: {path}')
    return {'version': 1, 'source': str(root), 'sha256': hashes, 'statistics': stats, 'training': training, 'demonstration': demo_records, 'distinct_training_inputs': len(training_ids), 'distinct_demo_inputs': len(demo_ids), 'overlapping_inputs': sorted(training_ids & demo_ids), 'demo_fields_equal_author_prediction': duplicates, 'demo_independent_truth': False, 'training_fields': {'space': 'author_normalized', 'pressure_unit_after_decode': 'MPa', 'temperature_unit_after_decode': 'degC'}, 'demonstration_fields': {'space': 'physical', 'pressure_unit': 'MPa', 'temperature_unit': 'degC'}, 'axes': ['sample', 'x', 'y', 'z', 'year'], 'years': list(range(21)), 'evaluation_scope': '24-case rotating validation is not an independent test set'}
