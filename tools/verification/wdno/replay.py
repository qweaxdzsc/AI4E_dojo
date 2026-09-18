"""独立进程用原构造函数读回主检查点，重放第一批固定测试样本。"""

import argparse
import json
import sys
from pathlib import Path

from protocol import digest, verify, write_json


def main():
    """验证落盘权重是真实推理输入；不共享训练进程模型对象。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    cfg = verify(root / "frozen")
    output = root / "main"
    checkpoint = output / "checkpoints" / "latest.pt"
    metadata = json.loads((output / "checkpoint.json").read_text())
    sys.path.insert(0, str(root / "frozen" / "source" / "burgers"))
    sys.path.insert(0, str(root / "frozen" / "source" / "burgers" / "ddpm_burgers"))
    import numpy as np
    import torch
    from ddpm_burgers import test_util
    from pytorch_wavelets import DWTInverse
    from train_ddpm_burgers import get_2d_ddpm
    from train_ddpm_burgers import parser as source_parser
    from wave_trans import tensor_to_coef

    torch.set_num_threads(8)
    options = source_parser.parse_args([])
    options.is_wavelet = True
    options.is_condition_u0 = True
    options.is_condition_uT = False
    options.is_condition_f = True
    options.is_condition_pad = True
    options.using_ddim = True
    options.ddim_sampling_steps = 50
    options.ddim_eta = 1.0
    scale = torch.tensor([10, 3, 3, 1, 21, 5, 5, 1, 10]).view(1, 9, 1, 1)
    model = get_2d_ddpm([41, 60], [81, 120], options, scale, False).to("mps")
    state = torch.load(checkpoint, map_location="cpu", weights_only=False)
    model.load_state_dict(state["model"], strict=True)
    if int(state["ema"]["step"]) != metadata["completed_updates"]:
        raise ValueError("落盘 EMA 计数与真实更新数不符")
    model.eval()
    raw = torch.load(
        cfg["sources"]["test"]["file"], map_location="cpu", mmap=True, weights_only=True
    )

    class Targets:
        def __init__(self, *_, **__):
            self.ori_shape = [81, 120]

        def get(self, indices):
            return torch.stack(
                (raw["u"][indices], torch.nn.functional.pad(raw["f"][indices], (0, 0, 0, 1))), dim=1
            )

    test_util.DiffusionDataset = Targets
    ids = json.loads((root / "frozen" / "indices.json").read_text())["test"][:16]
    torch.manual_seed(0)
    torch.mps.manual_seed(0)
    u0 = test_util.get_target(options, True, ids, device="cpu")[:, :32] / 10
    force = test_util.get_target(options, True, ids, f=True, device="cpu") / scale[:, 4:8]
    inverse = DWTInverse(mode="periodization", wave="bior2.4").to("mps")
    with torch.no_grad():
        coefficients = model.sample(batch_size=16, u_init=u0.to("mps"), f=force.to("mps"))
        physical = inverse(tensor_to_coef(coefficients * scale.to("mps"), [41, 60]))[
            :, :, :81, :120
        ]
    with np.load(output / "test-results.npz", allow_pickle=False) as arrays:
        predicted = physical[:, 0].cpu().numpy()
        expected = arrays["prediction"][:16]
        error = float(np.max(np.abs(predicted - expected)))
        if not np.allclose(predicted, expected, rtol=1e-6, atol=1e-6):
            raise ValueError("独立检查点重放与主进程预测不同: " + str(error))
    write_json(
        output / "checkpoint-replay.json",
        {
            "status": "passed",
            "samples": 16,
            "ids": ids,
            "max_abs_difference": error,
            "bitwise_equal": bool(np.array_equal(predicted, expected)),
            "weights": "model",
            "ema_step": int(state["ema"]["step"]),
            "completed_updates": metadata["completed_updates"],
            "checkpoint_sha256": digest(checkpoint),
            "original_factory": "train_ddpm_burgers.get_2d_ddpm",
            "rtol": 1e-6,
            "atol": 1e-6,
        },
    )


if __name__ == "__main__":
    main()
