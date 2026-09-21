"""独立 wheel 的公开注意力入口、真实更新、保存恢复和许可交付。"""

import os
import subprocess
import sys
from pathlib import Path


def test_installed_flare_optional_component(tmp_path):
    root = Path(__file__).resolve().parents[2]
    wheels = tmp_path / "wheels"
    subprocess.run(
        ["uv", "build", "--package", "ai4e-core", "--wheel", "--out-dir", str(wheels)],
        cwd=root,
        check=True,
        capture_output=True,
    )
    installed = tmp_path / "installed"
    subprocess.run(
        [
            "uv",
            "pip",
            "install",
            "--no-deps",
            "--target",
            str(installed),
            *map(str, wheels.glob("*.whl")),
        ],
        check=True,
        capture_output=True,
    )
    relative = "abilities/modeling/modules/flare_attention.py"
    assert (installed / "ai4e_core" / relative).read_bytes() == (
        root / "packages/ai4e-core" / relative
    ).read_bytes()
    assert (installed / "ai4e_core/Notice/physicsnemo/flare_plus_plus.json").is_file()
    assert (installed / "ai4e_core/Notice/physicsnemo/LICENSE").is_file()
    # 仓库外用户脚本：普通 nn.Sequential 内可选组合，没有应用或模型注册。
    script = tmp_path / "user.py"
    script.write_text("""import sys
import torch
from pathlib import Path
from ai4e_core.abilities.modeling.modules.flare_attention import FLAREPlusPlus
import ai4e_core.abilities.modeling.modules.flare_attention as source
assert Path(source.__file__).is_relative_to(Path(sys.argv[1]))
torch.set_num_threads(2)
torch.manual_seed(9)
model = torch.nn.Sequential(torch.nn.LayerNorm(8), FLAREPlusPlus(8, heads=2, dim_head=4, n_global_queries=3), torch.nn.Linear(8, 1))
x, target = torch.randn(2, 11, 8), torch.randn(2, 11, 1)
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
before = model[1].q_seed.detach().clone()
for _ in range(2):
    optimizer.zero_grad()
    (model(x) - target).square().mean().backward()
    optimizer.step()
assert not torch.equal(before, model[1].q_seed)
torch.save(model.state_dict(), "weights.pt")
expected = model.eval()(x).detach()
model.load_state_dict(torch.load("weights.pt", weights_only=True))
torch.save(model(x).detach(), "prediction.pt")
torch.testing.assert_close(torch.load("prediction.pt", weights_only=True), expected, rtol=0, atol=0)
assert not any(n.startswith(("physicsnemo", "ai4e_contrib", "ai4e_task", "ai4e_server", "einops", "jaxtyping")) for n in sys.modules)
""")
    env = {**os.environ, "PYTHONPATH": str(installed), "PYTHONDONTWRITEBYTECODE": "1"}
    result = subprocess.run(
        [
            "uv",
            "run",
            "--no-project",
            "--python",
            sys.executable,
            "python",
            "-B",
            str(script),
            str(installed),
        ],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
        timeout=90,
    )
    assert result.returncode == 0, result.stdout + result.stderr
