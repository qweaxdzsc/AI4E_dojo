"""PCNO 分支构造公开入口，数值能力由 core 提供。"""
from .model import EnhancedP_T_Net


def build_model(*, branch: str, modes=(1,1,1,1), width: int = 8):
    """构造压力或温度分支；输入为 BXYZT14 和 B4，输出 BXYZT。"""
    if branch not in ('pres','temp') or len(modes)!=4 or any(type(m) is not int or m<1 for m in modes):
        raise ValueError('PCNO 分支或谱模式非法')
    if type(width) is not int or width<8 or width%8:
        raise ValueError('PCNO 宽度须为正的8倍数')
    return EnhancedP_T_Net(*modes,width,width,train_mode=branch)


def import_weights(model, path):
    """从可信原版检查点或纯状态字典严格导入权重，不恢复优化器或游标。"""
    import torch
    from ai4e_core.abilities.data.save.array_manifest import digest

    state = torch.load(path, map_location='cpu', weights_only=False)
    weights = state['model'] if 'model' in state else state
    model.load_state_dict(weights, strict=True)
    return {'source_sha256': digest(path), 'mode': 'weights_only', 'exact_resume': False}
