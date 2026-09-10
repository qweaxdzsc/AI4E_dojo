"""用锁定 Noether 的实际处理器和包装层方法生成输入参考；仅开发工具依赖 Noether。"""

import ast
import hashlib
import inspect
import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import torch
from noether.data.pipeline.sample_processors.moment_normalization import (
    MomentNormalizationSampleProcessor,
)
from noether.data.pipeline.sample_processors.position_normalization import (
    PositionNormalizationSampleProcessor,
)

reference = Path(sys.argv[1]).resolve()
output = Path(sys.argv[2]).resolve()
commit = subprocess.check_output(
    ["git", "-C", str(reference), "rev-parse", "HEAD"], text=True
).strip()
assert commit == "313e6c5c2ff31f283a3e5935b4d85888aac6b025"
files = [
    "src/noether/modeling/models/aerodynamics.py",
    "src/noether/modeling/models/ab_upt.py",
    "src/noether/data/pipeline/sample_processors/moment_normalization.py",
    "src/noether/data/pipeline/sample_processors/position_normalization.py",
    "LICENSE.txt",
]
for implementation, filename in (
    (MomentNormalizationSampleProcessor, files[2]),
    (PositionNormalizationSampleProcessor, files[3]),
):
    if Path(inspect.getfile(implementation)).read_bytes() != (reference / filename).read_bytes():
        raise ValueError("参考环境安装副本与锁定源码不一致")
for filename in files:
    committed = subprocess.check_output(
        ["git", "-C", str(reference), "show", f"{commit}:{filename}"]
    )
    if committed != (reference / filename).read_bytes():
        raise ValueError(f"参考文件有未提交变化: {filename}")
# 仅抽出原始包装层 forward，避开无关模型工厂依赖；方法体不改写。
source = (reference / files[0]).read_text()
cls = next(
    n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == "AeroABUPT"
)
method = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "forward")
namespace = {"torch": torch}
exec(  # noqa: S102 -- 执行已锁定本地参考方法，保留其原始方法体
    compile(ast.Module(body=[method], type_ignores=[]), str(reference / files[0]), "exec"),
    namespace,
)
physical = {
    "wall_pos": torch.arange(30, dtype=torch.float32).reshape(10, 3) / 30,
    "fluid_pos": torch.arange(36, dtype=torch.float32).reshape(12, 3) / 36,
    "pressure": torch.arange(10, dtype=torch.float32)[:, None],
    "velocity": torch.arange(36, dtype=torch.float32).reshape(12, 3),
    "sdf": torch.arange(12, dtype=torch.float32)[:, None],
    "normal": torch.ones(10, 3),
    "design": torch.tensor([[2.0, 4.0]]),
}
normalized = PositionNormalizationSampleProcessor(
    {"wall_pos", "fluid_pos"}, [0.0, 0.0, 0.0], [1.0, 1.0, 1.0]
)(physical)
parameters = {
    "pressure": ([2.0], [3.0]),
    "velocity": ([1.0, 2.0, 3.0], [2.0, 3.0, 4.0]),
    "sdf": ([1.0], [2.0]),
    "design": ([0.0, 0.0], [2.0, 2.0]),
}
for name, (mean, std) in parameters.items():
    normalized = MomentNormalizationSampleProcessor(name, mean, std)(normalized)
indices = {
    "geometry": [0, 1, 2, 3, 4, 5],
    "supernodes": [0, 2, 4],
    "surface_anchor": [1, 4, 7],
    "volume_anchor": [0, 3, 6, 9],
    "surface_query": [2, 5],
    "volume_query": [1, 8],
}
flat = {
    "geometry_position": normalized["wall_pos"][indices["geometry"]],
    "geometry_supernode_idx": torch.tensor(indices["supernodes"]),
    "geometry_batch_idx": torch.zeros(6, dtype=torch.long),
    "design": normalized["design"],
}
for d, pos, feat in [("surface", "wall_pos", "normal"), ("volume", "fluid_pos", "sdf")]:
    flat[d + "_anchor_position"] = normalized[pos][indices[d + "_anchor"]][None]
    flat["query_" + d + "_position"] = normalized[pos][indices[d + "_query"]][None]
    flat[d + "_anchor_features"] = normalized[feat][indices[d + "_anchor"]][None]
    flat[d + "_query_features"] = normalized[feat][indices[d + "_query"]][None]
captured = {}


def capture(**kwargs):
    captured.update({k: v for k, v in kwargs.items() if v is not None})
    return {}, None


namespace["forward"](
    SimpleNamespace(
        _domain_names=["surface", "volume"], _conditioning_keys=["design"], backbone=capture
    ),
    **flat,
)
output.mkdir(parents=True, exist_ok=True)
torch.save(
    {
        "physical": physical,
        "normalized": normalized,
        "parameters": parameters,
        "indices": indices,
        "inputs": captured,
    },
    output / "reference.pt",
)
(output / "source.json").write_text(
    json.dumps(
        {
            "commit": commit,
            "files": {f: hashlib.sha256((reference / f).read_bytes()).hexdigest() for f in files},
            "fixture_sha256": hashlib.sha256((output / "reference.pt").read_bytes()).hexdigest(),
            "command": "uv run --no-project --python <noether>/.venv/bin/python python tools/generate_abupt_inputs.py <noether> tests/fixtures/abupt_inputs",
            "boundary": "Real normalization processors; unchanged AeroABUPT.forward captured at backbone call. This validates input translation, not network outputs.",
        },
        indent=2,
    )
)
