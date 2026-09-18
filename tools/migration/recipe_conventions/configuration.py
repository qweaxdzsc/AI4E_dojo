"""离线转换旧公共配置；不被新运行时导入，不触碰冻结科学产物。"""

from copy import deepcopy


def convert_gencp(config: dict) -> dict:
    """迁移耦合案例的公开路径；非空旧恢复字典需先生成可核验权重组。"""
    value = deepcopy(config)
    if isinstance(value.get("dataset"), dict) and "inputs" in value:
        return value
    resume = value["train"].pop("resume", {})
    if resume:
        raise ValueError("非空分场恢复字典须先转换为固定权重组，不能丢失恢复设置")
    root = value["data"].pop("root")
    physical = value["data"].pop("processed_root")
    value["dataset"] = {"name": value["dataset"]}
    value["data_root"] = value.pop("paths")["output"]
    prepared = value["train"].pop("preparation")
    checkpoint = value["infer"].pop("checkpoints")
    value["inputs"] = {
        "rawprep": {"source": root},
        "trainprep": {"dataset": physical},
        "train": {"preparation": prepared, "resume": None},
        "infer": {"preparation": prepared, "checkpoint": checkpoint},
        "single": {"preparation": prepared, "checkpoint": checkpoint},
        "post": {"results": value["post"].pop("results")},
    }
    if value.get("pipeline", {}).get("stages") == ["pipeline"]:
        value["pipeline"]["stages"] = ["rawprep", "trainprep", "train", "single", "infer", "post"]
    for name in ("rawprep", "trainprep", "model"):
        value.setdefault(name, {})
    return value


def convert_array_recipe(config: dict, *, control: bool, base=".") -> dict:
    """迁移控制和时空预测模板；多个分片保留为多个显式输入。"""
    value = deepcopy(config)
    if "inputs" in value and not control:
        return value
    if not control:
        from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy

        return migrate_legacy(value, base=base)
    from ai4e_contrib.application.pde_control.safediffcon.migration import migrate_legacy

    return migrate_legacy(value, base=base)


def convert_aero(config: dict) -> dict:
    """离线移动外流公共路径；先展开旧插值，再删除旧输出树。"""
    from omegaconf import OmegaConf

    from ai4e_contrib.application.aero_cfd.inputs import REFERENCES

    cfg = OmegaConf.create(OmegaConf.to_container(OmegaConf.create(config), resolve=True))
    if "data_root" not in cfg:
        root = OmegaConf.select(cfg, "paths.datasets.root")
        if not root:
            raise ValueError("迁移需要明确 data_root 或旧 paths.datasets.root")
        cfg.data_root = root
    legacy_post = "inputs" not in cfg and "infer" not in cfg
    if legacy_post:
        cfg.infer = deepcopy(cfg.get("post", {}))
        selected = list(OmegaConf.select(cfg, "pipeline.stages") or [])
        if "post" in selected:
            selected.insert(selected.index("post"), "infer")
            cfg.pipeline.stages = selected
    if "inputs" not in cfg:
        cfg.inputs = {}
    # 已拆分推理的旧配置里 post.checkpoint 是未消费的兼容默认，不盖过 infer。
    if not legacy_post:
        cfg.get("post", {}).pop("checkpoint", None)
    for section in ("post", "infer"):
        value = OmegaConf.select(cfg, f"{section}.checkpoint")
        if value in ("best", "last", "latest"):
            if value in ("last", "latest") and "train" in list(OmegaConf.select(cfg, "pipeline.stages") or []):
                cfg[section]["checkpoint"] = None  # 同次训练的末次权重由 Python 返回值交接。
            else:
                raise ValueError(f"迁移须先将 {section}.checkpoint 的标签 {value} 固定为实际文件路径")
    for old, public in {"post.checkpoint": "inputs.infer.checkpoint", "infer.results": "inputs.post.results"}.items():
        value = OmegaConf.select(cfg, old)
        if value is not None:
            if value in ("best", "last", "latest"):
                raise ValueError(f"迁移须先将 {old} 的标签 {value} 固定为实际文件路径")
            existing = OmegaConf.select(cfg, public)
            if existing is not None and existing != value:
                raise ValueError(f"迁移输入冲突: {old} / {public}")
            OmegaConf.update(cfg, public, value, force_add=True)
    for old, public in REFERENCES.items():
        value = OmegaConf.select(cfg, old)
        existing = OmegaConf.select(cfg, public)
        if existing is not None and value is not None and existing != value:
            raise ValueError(f"迁移输入冲突: {old} / {public}")
        if old == "dataset.partition" and (OmegaConf.is_dict(value) or value == "official"):
            cfg.dataset.partitions = value
            value = None
        if value is not None or existing is None:
            OmegaConf.update(cfg, public, value, force_add=True)
        node = cfg
        parts = old.split(".")
        for part in parts[:-1]:
            node = node.get(part, {})
        node.pop(parts[-1], None)
    cfg.pop("paths", None)
    cfg.get("post", {}).pop("checkpoint", None)
    cfg.get("infer", {}).pop("results", None)
    cfg.components.application = "ai4e_contrib.application.aero_cfd.operations"
    return OmegaConf.to_container(cfg, resolve=False)


def convert_parametric(config: dict) -> dict:
    """参数化 PDE 把预测从 post 拆出；旧准备位置转为显式消费引用。"""
    value = deepcopy(config)
    if "inputs" in value:
        return value
    manifest = value.setdefault("dataset", {}).pop("manifest", None)
    value["dataset"]["name"] = value["case"]
    prepared = value.setdefault("trainprep", {}).pop("output", None)
    checkpoint = value.setdefault("post", {}).pop("checkpoint", None)
    value["post"].pop("output", None)
    value["data_root"] = "../data"
    selected = value.setdefault("pipeline", {}).get("stages", ["rawprep", "trainprep", "train", "post"])
    if "post" in selected and "infer" not in selected:
        selected.insert(selected.index("post"), "infer")
    value["pipeline"]["stages"] = selected
    reference = str(prepared).rstrip("/") + "/preparation.json" if prepared and "trainprep" not in selected else None
    value["inputs"] = {
        "rawprep": {"manifest": manifest}, "trainprep": {"dataset": manifest},
        "train": {"dataset": manifest, "preparation": reference,
                  "resume": value.setdefault("train", {}).pop("resume", None)},
        "infer": {"dataset": manifest, "preparation": reference, "checkpoint": checkpoint},
        "post": {"results": None},
    }
    return value
