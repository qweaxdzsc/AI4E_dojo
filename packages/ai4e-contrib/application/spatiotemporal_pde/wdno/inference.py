"""明确检查点来源后预测；原 Trainer 文件只作权重导入。"""

from pathlib import Path

import torch

from ai4e_core.abilities.data.save.array_manifest import digest
from ai4e_core.applications.spatiotemporal_pde.infer import predict_split

from .model import diffusion
from .provenance import identity
from .training import contract


def infer(
    cfg: dict,
    prepared: dict,
    checkpoint: str,
    *,
    construct,
    objective,
    predict,
    output: str,
    derived=None,
) -> dict:
    """评价普通权重，严格校验 Dojo 合约；source 模式不提供续训。"""
    torch.set_num_threads(8)
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    if cfg["infer"]["checkpoint_format"] == "dojo":
        # 固定权重预测不构造优化器；新增训练策略只约束完整续训。
        # 其余原有模型/数据/目标/数值身份仍逐项保留严格比较。
        prediction_contract = dict(state.get("contract") or {})
        prediction_contract.pop("strategies", None)
        if prediction_contract != contract(cfg, prepared["train"], construct, objective):
            raise ValueError("推理检查点模型、数据或算法身份不相容")
    else:
        if cfg["model"] != {"dim": 128, "dim_mults": [1, 2, 4, 8], "groups": 1, "ddim_steps": 50}:
            raise ValueError("原权重导入仅支持已审计基础网络配置")
        if "opt" not in state or "step" not in state:
            raise ValueError("不是原 Trainer 检查点")
    model = diffusion(cfg["model"], construct).to(cfg["infer"]["device"])
    model.load_state_dict(state["model"], strict=True)
    del state
    provenance = {
        "checkpoint_sha256": digest(checkpoint),
        "weights": "model",
        "format": cfg["infer"]["checkpoint_format"],
        "predict": identity(predict),
        "derived": identity(derived) if derived else None,
        "sampling": cfg["model"]["ddim_steps"],
        "torch": torch.__version__,
    }
    return {
        split: predict_split(
            model,
            prepared[split],
            Path(output) / split,
            predict,
            batch_size=cfg["infer"]["batch_size"],
            provenance=provenance,
            derived=derived,
        )
        for split in ("validation", "test")
    }
