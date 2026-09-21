"""主控真实隔离推理验收：复放已训 baseline，并验证候选无法读取真值或联网。"""

import shutil
import uuid
from pathlib import Path

from ..io import read_json, write_json
from .evaluate import evaluate_candidate

ADAPTER = """import json
import numpy as np
import torch
from model import UNet

def load(assets):
    model = UNet().to("mps")
    model.load_state_dict(torch.load(assets / "checkpoint.pt", map_location="mps", weights_only=True)["model"])
    model.eval()
    stats = json.loads((assets / "statistics.json").read_text())
    mean = np.asarray(stats["mean"], dtype="float32")[None,None,:,None,None]
    std = np.asarray(stats["std"], dtype="float32")[None,None,:,None,None]
    @torch.inference_mode()
    def predict(history):
        state = torch.from_numpy(((history-mean)/std).reshape(-1,60,100,100)).to("mps")
        values = []
        for _ in range(8):
            prediction = model(state)
            values.append(prediction)
            state = torch.cat([state[:,30:],prediction],1)
        return torch.cat(values,1).reshape(-1,40,6,100,100).cpu().numpy()*std+mean
    return predict
"""


def check_worker(comparison):
    """只用验证集，主控私有环境；产物不能进入实验组。"""
    root = Path(comparison)
    attempt = root / "worker-check" / str(uuid.uuid4())
    candidate = attempt / "candidate"
    candidate.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(Path(__file__).with_name("model.py"), candidate / "model.py")
    shutil.copyfile(root / "preflight/epoch-500.pt", candidate / "checkpoint.pt")
    shutil.copyfile(root / "preflight/statistics.json", candidate / "statistics.json")
    secret = root / "worker-check/hidden-sentinel.txt"
    secret.write_text("must-never-be-readable-by-candidate")
    prefix = f"""import socket
from pathlib import Path
try:
    Path({str(secret)!r}).read_text()
except PermissionError:
    pass
else:
    raise AssertionError("candidate read secret")
try:
    s=socket.socket(); s.settimeout(2); s.connect(("127.0.0.1",8000))
except PermissionError:
    pass
else:
    raise AssertionError("candidate connected to local service")
finally:
    s.close()
"""
    (candidate / "predict.py").write_text(prefix + ADAPTER)
    write_json(candidate / "submission.json", {"entrypoint": "predict.py"})
    samples = read_json(root / "private-split.json")["splits"]["validation"]
    config = read_json(root / "comparison-protocol.json")
    result = evaluate_candidate(
        candidate,
        root / "evaluation-runtime",
        config["runtime_readonly_roots"],
        samples,
        attempt / "output",
    )
    expected = read_json(root / "preflight/result.json")["validation"]["mean_field_relative_l2"]
    result["parity_passed"] = (
        result["status"] == "evaluated"
        and abs(result["accuracy"]["mean_field_relative_l2"] - expected) < 1e-6
    )
    result["passed"] = result["parity_passed"] and result["eligible"]
    write_json(root / "evidence/worker-check.json", result)
    return result
