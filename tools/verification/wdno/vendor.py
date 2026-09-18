"""从冻结的作者代码抽取数值定义；只改导入和职责归属。"""

import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(
    "/Users/zonghui/work/project_simulation/dojo_train/wdno/burgers-local-v1-20260917/frozen/source/burgers"
)
BASE = ROOT / "packages/ai4e-contrib/ability"


def main():
    record = {"revision": "2d5c0ffbe11797e669efe0a34bd22f087eae51d7", "files": {}}

    def emit(dest, source, header, names=None, methods=None):
        original = (SOURCE / source).read_text()
        tree = ast.parse(original)
        pieces = []
        for node in tree.body:
            if not isinstance(node, (ast.FunctionDef, ast.ClassDef)) or (
                names and node.name not in names
            ):
                continue
            if methods and isinstance(node, ast.ClassDef):
                selected = [
                    n
                    for n in node.body
                    if isinstance(n, ast.FunctionDef)
                    and ((n.name in {"p_losses", "forward"}) == (methods == "loss"))
                ]
                declaration = (
                    "class DenoisingObjective:"
                    if methods == "loss"
                    else "class GaussianDiffusion(DenoisingObjective, nn.Module):"
                )
                pieces.append(
                    declaration
                    + "\n"
                    + "\n\n".join(
                        "\n".join(
                            original.splitlines()[
                                min([d.lineno for d in n.decorator_list] or [n.lineno])
                                - 1 : n.end_lineno
                            ]
                        )
                        for n in selected
                    )
                )
            else:
                pieces.append(ast.get_source_segment(original, node))
        target = BASE / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        (target.parent / "__init__.py").touch()
        target.write_text(
            '"""WDNO 作者数值定义；来源和抽取记录见 model/wdno/source.json。"""\n'
            + header
            + "\n\n"
            + "\n\n".join(pieces)
            + "\n"
        )
        record["files"][dest] = {
            "source": source,
            "original_sha256": hashlib.sha256((SOURCE / source).read_bytes()).hexdigest(),
            "sha256": hashlib.sha256(target.read_bytes()).hexdigest(),
        }

    emit(
        "model/wdno/unet.py",
        "ddpm_burgers/unet.py",
        "import torch\nfrom torch import nn, einsum\nimport torch.nn.functional as F\nfrom einops import rearrange\nfrom einops.layers.torch import Rearrange\nimport math\nfrom functools import partial\nfrom .schedules import default, exists",
        names={
            n.name
            for n in ast.parse((SOURCE / "ddpm_burgers/unet.py").read_text()).body
            if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name != "Unet1D"
        },
    )
    emit(
        "model/wdno/schedules.py",
        "ddpm_burgers/model_utils.py",
        "import math\nimport torch",
        names={
            "default",
            "exists",
            "identity",
            "normalize_to_neg_one_to_one",
            "unnormalize_to_zero_to_one",
            "extract",
            "linear_beta_schedule",
            "cosine_beta_schedule",
        },
    )
    emit(
        "transform/wdno/layout.py",
        "wave_trans.py",
        "import torch\nfrom torch import nn",
        names={"coef_to_tensor", "tensor_to_coef"},
    )
    emit(
        "transform/wdno/multiscale.py",
        "ddpm_burgers/wavelet_utils.py",
        "import torch\nimport torch.nn.functional as F",
    )
    emit(
        "transform/wdno/preparation.py",
        "ddpm_burgers/data_burgers_1d.py",
        "import math\nimport torch\nfrom torch import nn\nfrom pytorch_wavelets import DWTInverse, DWT1DForward\nfrom .layout import tensor_to_coef\nfrom .multiscale import upsample_coef",
        names={"get_wavelet_super_preprocess"},
    )
    emit(
        "constraint/wdno/objective.py",
        "ddpm_burgers/diffusion_1d.py",
        "import math\nimport torch\nimport torch.nn.functional as F\nfrom random import random\nfrom einops import reduce\nfrom ai4e_contrib.ability.model.wdno.schedules import default, extract",
        names={"GaussianDiffusion"},
        methods="loss",
    )
    emit(
        "inference/wdno/diffusion.py",
        "ddpm_burgers/diffusion_1d.py",
        'import torch\nfrom torch import nn\nimport torch.nn.functional as F\nfrom torch.cuda.amp import autocast\nfrom functools import partial\nfrom collections import namedtuple\nfrom tqdm.auto import tqdm\nfrom ai4e_contrib.ability.model.wdno.schedules import linear_beta_schedule, cosine_beta_schedule, default, identity, normalize_to_neg_one_to_one, unnormalize_to_zero_to_one, extract\nfrom ai4e_contrib.ability.transform.wdno.multiscale import get_wt_T\nfrom ai4e_contrib.ability.constraint.wdno.objective import DenoisingObjective\nModelPrediction = namedtuple("ModelPrediction", ["pred_noise", "pred_x_start"])',
        names={"GaussianDiffusion"},
        methods="sampler",
    )
    emit(
        "eval/wdno/metrics.py", "ddpm_burgers/test_util.py", "import torch", names={"mse_deviation"}
    )
    (BASE / "model/wdno/source.json").write_text(json.dumps(record, indent=2) + "\n")


if __name__ == "__main__":
    main()
