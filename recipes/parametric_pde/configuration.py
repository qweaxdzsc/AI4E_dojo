"""五段用户配置：案例默认展开、显式路径、公共组件选择与参数预检。"""

import math
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_core.applications.parametric_pde.contracts import load_component

CASES = {
    "convection_diffusion": ([25, 25], 3, 64, 5000, "epoch_sum", 3.0),
    "neumann_diffusion": ([40, 40], 5, 128, 5000, "epoch_sum", 5.0),
    "advection": ([150, 150], 5, 64, 2000, "instance", 10.0),
    "burgers": ([100, 100], 4, 64, 5000, "instance", 15.0),
    "diffusion_trapezoid": ([100, 20, 20], 3, 64, 3000, "instance", 1.0),
}


def _domain_defaults(case):
    """正式案例默认参数；研究用覆盖仍通过同一校验入口。"""
    if case not in CASES:
        raise ValueError(f"未知案例: {case}")
    cp, degree, hidden, epochs, group, data_weight = CASES[case]
    mse = {"loss": "mse", "reduction": "mean", "weight": 1.0}
    boundary, periodic = {}, {}
    if case == "neumann_diffusion":
        boundary = {n: {"u": {"type": "zero_gradient"}} for n in ("left", "right")}
    if case == "convection_diffusion":
        boundary = {"right": {"u": {"type": "fixed_value", "value": 1.0}}}
    if case == "diffusion_trapezoid":
        boundary = {
            n: {"u": {"type": "fixed_value", "value": 1.0}}
            for n in ("left", "right", "bottom", "top")
        }
    if case in {"advection", "burgers"}:
        periodic = {"x_periodic": {"boundaries": ["left", "right"], "fields": ["u"]}}
    hard_bc = case in {"convection_diffusion", "diffusion_trapezoid"}
    constraints = {
        "equations": dict(mse),
        "supervision": {**mse, "weight": data_weight},
        # 原 PI 分支仅 Neumann 将初值作为训练罚项；其余只记录违约指标。
        "initial_conditions": {**mse, "weight": 2.0 if case == "neumann_diffusion" else 0.0},
        "boundary_conditions": {
            **mse,
            "enforcement": "hard" if hard_bc else "soft",
            "weight": 2.0 if case == "neumann_diffusion" else 1.0,
            "overrides": {},
        },
        # 周期配对能力可供研究使用，参考训练没有额外周期罚项。
        "periodic_boundary_conditions": {**mse, "weight": 0.0},
    }
    if case == "burgers":
        constraints["equations"]["loss"] = constraints["supervision"]["loss"] = "l2"
    if case == "diffusion_trapezoid":
        # 用户要求以论文 Appendix D.3 为准；仓库实际调用 1e-5 另行披露。
        constraints["equations"]["weight"] = 1e-3
    return {
        "case": case,
        "components": {
            "dataset": "ai4e_contrib.application.datasets.parametric",
            "model": "ai4e_contrib.ability.model.pibsnet.component",
        },
        "dataset": {"manifest": "../datasets/manifest.json"},
        "run_root": "../runs",
        "snapshot_modules": ["ai4e_spec", "ai4e_contrib"],
        "pipeline": {"stages": ["rawprep", "trainprep", "train", "post"]},
        "rawprep": {},
        "trainprep": {"execute": True, "output": "../prepared"},
        "model": {
            "control_points": cp,
            "degree": degree,
            "hidden_dim": hidden,
            "hard_initial": case == "advection",
            "boundary_conditions": boundary,
            "initial_conditions": {
                "u": {
                    "value": "dataset_initial",
                    "corner_policy": "boundary_priority" if hard_bc else "initial_priority",
                }
            },
            "periodic_boundary_conditions": periodic,
            "constraints": constraints,
            "sampling": {
                "seed": 42,
                "supervised": {"method": "all"},
                "interior": {"method": "all", "include_boundary": True},
                "initial": {"method": "all"},
                "boundaries": {name: {"method": "all"} for name in boundary},
                "periodic_pairs": {
                    name: {"method": "uniform", "num_pairs": 100} for name in periodic
                },
            },
        },
        "train": {
            "execute": True,
            "device": "auto",
            "precision": "fp32",
            "seed": 42,
            "max_epochs": epochs,
            "learning_rate": 0.001,
            "betas": [0.9, 0.999],
            "weight_decay": 0.0,
            "gradient_clip": None,
            "update_group": group,
            "step": None,
            "resume": None,
            "log_every": 100,
            "save_on_interrupt": True,
            "restore_history": True,
            "snapshot": True,
            "evaluation": {"enabled": False, "interval": 50},
        },
        "post": {"checkpoint": None, "output": "../predictions"},
    }


def _unknown(value, allowed, path):
    extra = set(value) - set(allowed)
    if extra:
        raise ValueError(f"{path}: 未知配置 {sorted(extra)}")


def _validate_domain(cfg):
    """脚本和程序共用严格输入检查；不修改用户配置或历史产物。"""
    reference = _domain_defaults(cfg["case"])
    _unknown(cfg, set(reference) | {"execution"}, "config")
    for section in ("dataset", "components", "rawprep", "trainprep", "model", "train", "post"):
        _unknown(cfg[section], reference[section], section)
    model = cfg["model"]
    cp = model["control_points"]
    if len(cp) != len(reference["model"]["control_points"]) or any(
        isinstance(n, bool) or not isinstance(n, int) or n <= model["degree"] for n in cp
    ):
        raise ValueError("model.control_points 必须与维度对应且大于 degree")
    if model["degree"] < 2 or model["hidden_dim"] < 1:
        raise ValueError("样条至少二次，hidden_dim 必须为正")
    if model["hard_initial"] and cfg["case"] != "advection":
        raise ValueError("hard_initial 仅支持 Advection 原初始控制行插值")
    sampling = model["sampling"]
    _unknown(sampling, reference["model"]["sampling"], "model.sampling")
    if set(sampling["boundaries"]) != set(model["boundary_conditions"]):
        raise ValueError("边界条件与采样边界名称不一致")
    if set(sampling["periodic_pairs"]) != set(model["periodic_boundary_conditions"]):
        raise ValueError("周期条件与采样配对名称不一致")
    valid_boundaries = {"left", "right"} | ({"top", "bottom"} if len(cp) == 3 else set())
    for name, fields in model["boundary_conditions"].items():
        if name not in valid_boundaries or set(fields) != {"u"}:
            raise ValueError(f"boundary_conditions.{name}: 未知边界或字段")
        condition = fields["u"]
        kind = condition["type"]
        allowed = {
            "fixed_value": {"type", "value"},
            "fixed_gradient": {"type", "gradient"},
            "zero_gradient": {"type"},
        }
        if kind not in allowed or set(condition) != allowed[kind]:
            raise ValueError(f"boundary_conditions.{name}: 条件参数不匹配")
        target = condition.get("value", condition.get("gradient", 0.0))
        if isinstance(target, dict):
            if set(target) != {"function"}:
                raise ValueError(f"boundary_conditions.{name}: 函数目标需要 function")
            load_component(target["function"])
        elif (
            isinstance(target, bool)
            or not isinstance(target, (int, float))
            or not math.isfinite(target)
        ):
            raise ValueError(f"boundary_conditions.{name}: 目标必须有限")
    initial = model["initial_conditions"]
    if set(initial) != {"u"} or set(initial["u"]) != {"value", "corner_policy"}:
        raise ValueError("initial_conditions 需要 u.value 和 corner_policy")
    if initial["u"]["corner_policy"] not in {"initial_priority", "boundary_priority"}:
        raise ValueError("未知初边界交角策略")
    if (
        model["constraints"]["boundary_conditions"]["enforcement"] == "hard"
        and model["boundary_conditions"]
        and initial["u"]["corner_policy"] != "boundary_priority"
    ):
        raise ValueError("硬边界需要显式 boundary_priority，避免不连续交角冲突")
    for name, condition in model["periodic_boundary_conditions"].items():
        if set(condition) != {"boundaries", "fields"} or condition["fields"] != ["u"]:
            raise ValueError(f"periodic.{name}: 需要 boundaries 和 fields=[u]")
        if set(condition["boundaries"]) != {"left", "right"} or len(condition["boundaries"]) != 2:
            raise ValueError("首期案例周期配对仅支持 left/right")
        if set(condition["boundaries"]) & set(model["boundary_conditions"]):
            raise ValueError("周期边界不能重复声明另一物理边界条件")
    constraints = model["constraints"]
    _unknown(constraints, reference["model"]["constraints"], "model.constraints")
    for name, settings in constraints.items():
        _unknown(settings, reference["model"]["constraints"][name], f"constraints.{name}")
        if settings["loss"] not in {"mse", "mae", "l2"} or settings["reduction"] not in {
            "sum",
            "mean",
        }:
            raise ValueError(f"constraints.{name}: 未知损失或归约")
        if not math.isfinite(settings["weight"]) or settings["weight"] < 0:
            raise ValueError(f"constraints.{name}: 非法权重")
    if constraints["boundary_conditions"]["enforcement"] not in {"hard", "soft"}:
        raise ValueError("未知边界施加方式")
    for boundary, fields in constraints["boundary_conditions"]["overrides"].items():
        if boundary not in model["boundary_conditions"] or set(fields) != {"u"}:
            raise ValueError("边界约束覆盖引用未知边界或字段")
        _unknown(fields["u"], {"weight", "loss", "reduction"}, "boundary.overrides")
        settings = {**constraints["boundary_conditions"], **fields["u"]}
        if settings["loss"] not in {"mse", "mae", "l2"} or settings["reduction"] not in {
            "mean",
            "sum",
        }:
            raise ValueError("边界覆盖损失无效")
        if not math.isfinite(settings["weight"]) or settings["weight"] < 0:
            raise ValueError("边界覆盖权重无效")
    train = cfg["train"]
    _unknown(train["evaluation"], {"enabled", "interval"}, "train.evaluation")
    if (
        not isinstance(train["evaluation"]["enabled"], bool)
        or not isinstance(train["evaluation"]["interval"], int)
        or train["evaluation"]["interval"] < 1
    ):
        raise ValueError("评价开关须为布尔值，评价间隔须为正整数")
    if train["precision"] not in {"fp32", "fp64"} or train["update_group"] not in {
        "epoch_sum",
        "instance",
    }:
        raise ValueError("未知精度或更新分组")
    if train["max_epochs"] < 1 or train["learning_rate"] <= 0:
        raise ValueError("训练预算和学习率必须为正")
    if train["gradient_clip"] is not None and (
        not math.isfinite(train["gradient_clip"]) or train["gradient_clip"] <= 0
    ):
        raise ValueError("gradient_clip 必须为 null 或有限正数")
    stages = cfg["pipeline"]["stages"]
    order = ["rawprep", "trainprep", "train", "infer", "post"]
    if not stages or len(set(stages)) != len(stages) or stages != [s for s in order if s in stages]:
        raise ValueError("阶段必须按 rawprep/trainprep/train/post 顺序选择")
    return cfg


def defaults(case):
    """公共阶段输入和数据输出根，科学参数保留原默认值。"""
    cfg = _domain_defaults(case)
    manifest = cfg["dataset"].pop("manifest")
    cfg["data_root"] = "../data"
    cfg["dataset"]["name"] = case
    cfg["inputs"] = {
        "rawprep": {"manifest": manifest},
        "trainprep": {"dataset": manifest},
        "train": {"dataset": manifest, "preparation": None, "resume": None},
        "infer": {"dataset": manifest, "preparation": None, "checkpoint": None},
        "post": {"results": None},
    }
    cfg["trainprep"].pop("output")
    cfg["train"].pop("resume")
    cfg["post"] = {}
    cfg["infer"] = {}
    cfg["pipeline"]["stages"] = ["rawprep", "trainprep", "train", "infer", "post"]
    return cfg


def application_parameters(config, *, stage="trainprep", session=None, dataset=None,
                           prepared=None, trained=None, results=None):
    """领域所需参数由公共输入显式绑定；冻结模型语义不包含目录外壳。"""
    from copy import deepcopy
    from ai4e_core.base.config.conventions import input_bindings, require_current_keys

    cfg = deepcopy(config)
    require_current_keys(cfg, {"dataset.manifest": "inputs.<stage>.dataset",
        "trainprep.output": "data_root", "train.resume": "inputs.train.resume",
        "post.checkpoint": "inputs.infer.checkpoint", "post.output": "data_root"})
    input_bindings(cfg)
    inputs = cfg.pop("inputs")
    root = Path(cfg.pop("data_root"))
    cfg.pop("infer", None)
    cfg["dataset"] = {"manifest": inputs["rawprep"].get("manifest")}
    if stage in ("trainprep", "train", "infer"):
        cfg["dataset"]["manifest"] = inputs[stage].get("dataset")
    if dataset is not None:
        cfg["dataset"]["manifest"] = dataset["manifest"] if isinstance(dataset, dict) else dataset
    reference = prepared
    if reference is None and stage in ("train", "infer"):
        reference = inputs[stage].get("preparation")
    if isinstance(reference, dict):
        reference = reference["path"]
    cfg["trainprep"]["output"] = str(Path(reference).parent) if reference else str(root / "trainprep")
    if stage == "trainprep" and session is not None:
        cfg["trainprep"]["output"] = str(session.output_dir("trainprep"))
    if stage in ("train", "infer") and not reference:
        raise ValueError(f"{stage} 缺少明确 preparation 输入")
    cfg["train"]["resume"] = inputs["train"].get("resume")
    cfg["post"] = {"checkpoint": inputs["infer"].get("checkpoint"),
                   "output": str(session.output_dir("infer") / "results") if session else str(root / "infer")}
    if trained is not None:
        cfg["post"]["checkpoint"] = str(session.run_dir / "checkpoints/last.pt")
    if stage == "post":
        cfg["post"]["results"] = results["results"] if isinstance(results, dict) else results or inputs["post"].get("results")
        if not cfg["post"]["results"]:
            raise ValueError("post 缺少固定结果")
    return cfg


def validate(cfg):
    """校验公开参数，数据是否存在由实际消费阶段判断。"""
    from ai4e_core.base.config.conventions import input_bindings, require_current_keys
    input_bindings(cfg)
    internal = application_parameters(cfg)
    _validate_domain(internal)
    return cfg


def load_configuration(path, overrides=None):
    """以配置文件为基准解析公共输入，旧公共键明确拒绝。"""
    from ai4e_core.base.config.conventions import normalize_recipe_config
    path = Path(path).resolve()
    user = OmegaConf.merge(OmegaConf.load(path), OmegaConf.from_dotlist(overrides or []))
    cfg = OmegaConf.to_container(OmegaConf.merge(defaults(user["case"]), user), resolve=True)
    cfg = normalize_recipe_config(cfg, base=path.parent)
    validate(cfg)
    return cfg


def components(cfg):
    """只在模板边界选择贡献组件，core 不反向导入 contrib。"""
    return {
        "dataset_component": load_component(cfg["components"]["dataset"]),
        "model_component": load_component(cfg["components"]["model"]),
    }
