"""独立推理参数边界；旧 post 配置只在兼容入口解释。"""

from copy import deepcopy

from ai4e_core.base.config import plain

try:
    from ai4e_spec.artifacts.inference import apply_export_aliases
except ImportError:  # 契约包尚未重装时，脚本入口仍须能导入

    def apply_export_aliases(settings: dict, incoming: dict | None = None) -> dict:
        """与契约包同一规则：未拆新键时旧键同时开关二者。"""
        incoming = incoming if isinstance(incoming, dict) else settings

        def present(key: str) -> bool:
            return key in incoming and incoming[key] is not None

        split = present("export_pointcloud") or present("export_mesh")
        if not split:
            vtk = settings.get("export_vtk")
            value = True if vtk is None else bool(vtk)
            settings["export_pointcloud"] = value
            settings["export_mesh"] = value
        else:
            if present("export_pointcloud"):
                settings["export_pointcloud"] = bool(incoming["export_pointcloud"])
            else:
                settings["export_pointcloud"] = True
            if present("export_mesh"):
                settings["export_mesh"] = bool(incoming["export_mesh"])
            else:
                vtk = incoming.get("export_vtk", settings.get("export_vtk"))
                settings["export_mesh"] = True if vtk is None else bool(vtk)
        settings["export_vtk"] = bool(settings["export_mesh"])
        return settings


DEFAULTS = {
    "checkpoint": None,
    "preparation": None,
    "split": "test",
    "samples": [],
    "device": "cpu",
    "query_chunk_size": 16384,
    "evaluate": True,
    "save_predictions": True,
    "export_vtk": True,
    "export_pointcloud": True,
    "export_mesh": True,
}
OPTIONAL = {
    "seed",
    "prediction",
    "metric",
    "sample_metric",
    "derived_fields",
    "overwrite",
    "random_stream",
    "query",
    "sample_indices",
    "results",
    "fields",
    "metrics",
}


def resolve_infer(config: dict) -> dict:
    """校验独立推理参数并补缺；不修改训练或冻结准备声明。"""
    cfg = plain(config)
    settings = cfg.get("infer")
    if not isinstance(settings, dict):
        raise TypeError("独立 infer 需要 infer 参数映射")
    unknown = set(settings) - set(DEFAULTS) - OPTIONAL
    if unknown:
        raise ValueError(f"未知 infer 参数: {sorted(unknown)}")
    incoming = dict(settings)
    if "seed" in incoming and (type(incoming["seed"]) is not int or incoming["seed"] < 0):
        raise ValueError("infer.seed 必须为非负整数")
    settings = {**deepcopy(DEFAULTS), **incoming}
    apply_export_aliases(settings, incoming)
    for key in ("fields", "metrics"):
        if key in settings and settings[key] is not None:
            values = settings[key]
            if (
                not isinstance(values, list)
                or not values
                or any(not isinstance(v, str) or not v for v in values)
                or len(values) != len(set(values))
            ):
                raise ValueError("infer." + key + " 必须是非空、不重复的名称列表")
    samples = settings["samples"]
    if not isinstance(samples, list) or any(not isinstance(s, str) or not s for s in samples):
        raise ValueError("infer.samples 必须为有序样本名称列表")
    if len(samples) != len(set(samples)):
        raise ValueError("infer.samples 包含重复样本")
    if not isinstance(settings["split"], str) or not settings["split"]:
        raise ValueError("infer.split 不能为空")
    size = settings["query_chunk_size"]
    if isinstance(size, bool) or not isinstance(size, int) or size < 1:
        raise ValueError("infer.query_chunk_size 必须为正整数")
    for key in ("evaluate", "save_predictions", "export_vtk", "export_pointcloud", "export_mesh"):
        if not isinstance(settings[key], bool):
            raise TypeError(f"infer.{key} 必须为布尔值")
    if (settings["export_pointcloud"] or settings["export_mesh"]) and not settings[
        "save_predictions"
    ]:
        raise ValueError("导出点云或 VTK 网格化数据需要保存预测")
    if not settings["evaluate"] and not settings["save_predictions"]:
        raise ValueError("推理至少需要评价或保存预测")
    if not isinstance(settings["device"], str) or not settings["device"]:
        raise ValueError("infer.device 必须为设备名称")
    cfg["infer"] = settings
    return cfg


def inference_parameters(config: dict) -> dict:
    """给既有模型交付等价内部参数；训练配置副本不会写回用户配置。"""
    cfg = resolve_infer(config)
    cfg["post"] = deepcopy(cfg["infer"])
    cfg.setdefault("train", {})["device"] = cfg["infer"]["device"]
    if cfg["infer"]["preparation"]:
        cfg["train"]["preparation"] = cfg["infer"]["preparation"]
        # 独立推理的数据身份由选定准备固定，不消费别的阶段遗留的清单路径。
        cfg["train"]["manifest"] = None
    return cfg


def public_to_business(config: dict) -> dict:
    """将已展开的 checkpoint 用户配置还原为业务声明，供只读检查使用。"""
    cfg = plain(config)
    # 运行记录保存的是公共配置树；检查进程不能依赖 contrib 的配置装配器，
    # 但仍须把稳定的 inputs 引用还原成 core 预检所需的最小业务视图。
    inputs = cfg.get("inputs") or {}
    if inputs and ("dataset" not in cfg or "root" not in cfg.get("dataset", {})):
        raw = inputs.get("rawprep") or {}
        trainprep = inputs.get("trainprep") or {}
        train = inputs.get("train") or {}
        infer = inputs.get("infer") or {}
        post = inputs.get("post") or {}
        dataset = cfg.setdefault("dataset", {})
        for source, target in (
            ("source", "root"),
            ("manifest", "manifest"),
            ("train_h5", "train_h5"),
            ("test_h5", "test_h5"),
            ("connectivity_h5", "connectivity_h5"),
        ):
            if raw.get(source) is not None:
                dataset[target] = raw[source]
        if trainprep.get("partition") is not None:
            dataset["partition"] = trainprep["partition"]
        if trainprep.get("dataset") is not None:
            cfg.setdefault("train", {})["manifest"] = trainprep["dataset"]
        if trainprep.get("statistics") is not None:
            cfg.setdefault("normalization", {})["statistics"] = trainprep["statistics"]
        for section, values in (("train", train), ("infer", infer), ("post", post)):
            for key in ("preparation", "resume", "initial_weights", "checkpoint", "results"):
                if values.get(key) is not None:
                    cfg.setdefault(section, {})[key] = values[key]
        cfg.pop("inputs", None)
        # Paths are generated by the public adapter and are not user inputs.
        # Recreate only the directories needed by inspection/VTK capability.
        from pathlib import Path

        data_root = cfg.get("data_root")
        if data_root:
            root = Path(data_root)
            cfg["paths"] = {
                "datasets": {
                    "root": str(root / "rawprep"),
                    **{
                        name: str(root / "rawprep" / name)
                        for name in ("train", "test", "eval", "validation")
                    },
                    "normalize": {
                        "root": str(root / "trainprep" / "normalize"),
                        **{
                            name: str(root / "trainprep" / "normalize" / name)
                            for name in ("train", "test", "eval", "validation")
                        },
                    },
                    "predictions": str(root / "infer" / "predictions"),
                    "post": str(root / "post" / "analysis"),
                }
            }
    if "rawprep" in cfg:
        # 公共树把加载路径移入 inputs；未选初始权重仍是领域缺省 None。
        cfg.setdefault("model", {}).setdefault(
            "initial_weights", cfg.get("inputs", {}).get("train", {}).get("initial_weights")
        )
        cfg.update(cfg.pop("rawprep"))
        prep = cfg.setdefault("trainprep", {})
        if "normalization" in prep:
            cfg["normalization"] = prep.pop("normalization")
        if "sampling" in cfg.get("model", {}):
            cfg["sampling"] = cfg["model"].pop("sampling")
        elif "sampling" in prep:
            cfg["sampling"] = prep.pop("sampling")
    return cfg
