"""按科学定义提取 PCNO，保存来源摘要；计算优先进入 core，源码原件只读。"""

import argparse
import ast
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CORE = ROOT / "packages/ai4e-core"
CONTRIB = ROOT / "packages/ai4e-contrib"


def emit(target, names, tree, imports, description, records, source):
    """只拆模块、补说明，不改定义内科学表达式。"""
    definitions = {n.name: n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))}
    nodes = []
    for name in names:
        node = definitions[name]
        if not ast.get_docstring(node):
            node.body.insert(
                0, ast.Expr(ast.Constant(f"{description}：{name}；保留来源算法、参数与权重布局。"))
            )
        nodes.append(node)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        f'"""{description}。\n\n源自 Code Ocean capsule 8000337 v1.0，GPL-3.0；来源及许可证见 PCNO source.json。\n"""\n\n'
        + imports
        + "\n\n"
        + "\n\n".join(ast.unparse(n) for n in nodes)
        + "\n"
    )
    records.append(
        {"file": str(target.relative_to(ROOT)), "definitions": names, "source": source.name}
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    model = args.source / "PCNO_Model_4D.py"
    tree = ast.parse(model.read_text())
    from tools.verification.pcno.numerical_repair import repair_vis

    repair_vis(next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "PDE_F"))
    records = []
    emit(
        CORE / "abilities/modeling/modules/fourier4d.py",
        ["SpectralConv4d"],
        tree,
        "import torch\nfrom torch import nn",
        "四维实数 FFT 谱卷积，八个频域角块",
        records,
        model,
    )
    emit(
        CORE / "abilities/modeling/modules/unet_volume.py",
        ["UNet3D_Lite"],
        tree,
        "import torch\nfrom torch import nn",
        "三维 U-Net，仅在前两个空间轴池化",
        records,
        model,
    )
    emit(
        CORE / "abilities/modeling/modules/global_features.py",
        ["GlobalFeatureFusion"],
        tree,
        "from torch import nn",
        "将全局参数映射并广播为空间时间特征",
        records,
        model,
    )
    emit(
        CORE / "abilities/modeling/models/fourier_unet4d.py",
        ["Block4dWithUNet", "FNO4dUNet", "FNO4dUNet_WithGlobalFusion"],
        tree,
        "import torch\nfrom torch import nn\nfrom torch.nn import functional as F\nfrom ai4e_core.abilities.modeling.modules.fourier4d import SpectralConv4d\nfrom ai4e_core.abilities.modeling.modules.unet_volume import UNet3D_Lite\nfrom ai4e_core.abilities.modeling.modules.global_features import GlobalFeatureFusion",
        "四维谱算子和共享三维 U-Net 特征组合；一次 U-Net 结果供四层重复使用",
        records,
        model,
    )
    emit(
        CORE / "abilities/constraint/spatiotemporal_field.py",
        ["compute_enhanced_gradient_loss", "create_smooth_weight_map", "weighted_mse"],
        tree,
        "import torch\nfrom torch.nn import functional as F",
        "五轴时空场的相对梯度及井距加权监督；压力和温度为当前权重策略",
        records,
        model,
    )
    emit(
        CORE / "abilities/postproc/wellbore.py",
        ["WellboreModel", "wellbore_model_run", "extract_wellData", "process_wellResult"],
        tree,
        "import math\nimport numpy as np\nimport torch\nfrom iapws import IAPWS97",
        "井筒水汽物性与数值积分；井口结果经标量求解而不保留自动微分图",
        records,
        model,
    )
    emit(
        CORE / "abilities/constraint/geothermal.py",
        ["PDE_F", "physical_loss", "compute_loss"],
        tree,
        "import math\nimport torch\nfrom torch import nn\nfrom torch.nn import functional as F\nfrom ai4e_core.abilities.postproc.wellbore import extract_wellData, process_wellResult",
        "五层地热网格的水物性、上风通量、质量与能量残差；压力输入 MPa、温度摄氏度",
        records,
        model,
    )
    emit(
        CONTRIB / "ability/model/pcno/model.py",
        ["EnhancedP_T_Net"],
        tree,
        "from torch import nn\nfrom ai4e_core.abilities.modeling.models.fourier_unet4d import FNO4dUNet_WithGlobalFusion",
        "PCNO 单分支组合；两个独立网络保留作者 state_dict 布局",
        records,
        model,
    )
    trainer = args.source / "PCNO_Train_4D.py"
    t = ast.parse(trainer.read_text())
    tc = next(n for n in t.body if isinstance(n, ast.ClassDef) and n.name == "TrainConfig")
    tc.body = [
        n for n in tc.body if not isinstance(n, ast.FunctionDef) or n.name != "async_prefetch"
    ]
    emit(
        CONTRIB / "application/geothermal/pcno/protocol.py",
        ["TrainConfig", "ModelConfig"],
        t,
        'import math\nimport random\nimport numpy as np\nimport torch\n\ndef denormalize(tensor, mean, std):\n    """使用作者冻结统计量还原。"""\n    return tensor * std + mean',
        "PCNO 统计量、种子、原始250轮调度与分阶段损失权重",
        records,
        trainer,
    )
    econ = args.source / "PCNO_Heat_Ele_Eco_model.py"
    e = ast.parse(econ.read_text())
    emit(
        CORE / "abilities/postproc/geothermal_economics.py",
        ["utilization_eff", "cap_cost", "ope_cost", "level_cost", "score_tech_econ"],
        e,
        "import numpy as np\nimport torch",
        "地热二十年技术经济计算；保留原成本、折现与评分公式",
        records,
        econ,
    )
    tech = next(
        n for n in e.body if isinstance(n, ast.FunctionDef) and n.name == "technical_results"
    )
    tech.args.args.append(ast.arg(arg="stats"))
    emit(
        CONTRIB / "application/geothermal/pcno/economy.py",
        ["technical_results", "ensure_column"],
        e,
        "import numpy as np\nimport torch\nimport pandas as pd\nfrom ai4e_core.abilities.postproc.geothermal_economics import level_cost, score_tech_econ",
        "发布字段到地热经济输入的连接；井级取均值和求和按原源码",
        records,
        econ,
    )
    lines = econ.read_text().splitlines()
    assignments = "\n".join(lines[14:22])
    start = next(i for i, s in enumerate(lines) if s.startswith("T_y, T_a,"))
    end = next(i for i, s in enumerate(lines) if s.startswith("df = df.round"))
    body = "\n".join(lines[start : end + 1]).replace(
        "Twh_a, Hwh_a, Ewh_a, Pinj_a)", "Twh_a, Hwh_a, Ewh_a, Pinj_a, stats)"
    )
    target = CONTRIB / "application/geothermal/pcno/economy.py"
    with target.open("a") as stream:
        stream.write(
            '\n\ndef evaluate_economy(pred, raw, stats, T_threshold=75, CF=0.85):\n    """只消费固定预测；Temp_drop 保留作者首例平均温度基准，不解释为物理初温降幅。"""\n'
        )
        stream.write(
            "\n".join("    " + s for s in (assignments + "\n" + body + "\nreturn df").splitlines())
            + "\n"
        )
    license_ = (args.source / "LICENSE").read_bytes()
    (CONTRIB / "ability/model/pcno/LICENSE").write_bytes(license_)
    (CORE / "abilities/PCNO_LICENSE").write_bytes(license_)
    manifest = {
        "capsule": "https://codeocean.com/capsule/8000337/tree/v1",
        "commit": "dc4cd4417ed7f97715ffb47496690ce60f7665a3",
        "license": "GPL-3.0",
        "sha256": {
            p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [model, trainer, econ]
        },
        "modules": records,
        "adaptations": [
            "split modules and remove import-time seed changes",
            "explicit stats argument for technical_results",
            "ordinary function for fixed-result economic table",
            "shared Dojo training replaces original loop",
            "Explicit PDE_F.vis inactive-branch masking; active formulas unchanged",
        ],
    }
    (CONTRIB / "ability/model/pcno/source.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
