"""冻结入口缺省时的现行官方连接；不改写磁盘 task-entry。"""

OFFICIAL_AERO_DATASETS = frozenset(
    {
        "ai4e_contrib.application.datasets.shapenet_car",
        "ai4e_contrib.application.datasets.nasa_crm",
    }
)
OFFICIAL_AERO_CONFIGURATION_ADAPTER = (
    "ai4e_contrib.application.aero_cfd.loader_adapter.load_user_configuration"
)


def resolve_configuration_adapter(entry: dict) -> str | None:
    """已声明则用声明；官方外流旧任务缺键时挂上现行适配器。"""
    target = entry.get("configuration_adapter")
    if isinstance(target, str) and target.strip():
        return target
    dataset = str((entry.get("components") or {}).get("dataset") or "")
    if dataset in OFFICIAL_AERO_DATASETS:
        return OFFICIAL_AERO_CONFIGURATION_ADAPTER
    return None


def with_resolved_configuration_adapter(entry: dict) -> dict:
    """只补本次请求入口，不回写用户 recipe。"""
    target = resolve_configuration_adapter(entry)
    if target and entry.get("configuration_adapter") != target:
        entry = {**entry, "configuration_adapter": target}
    dataset = (entry.get("components") or {}).get("dataset")
    if (
        dataset in OFFICIAL_AERO_DATASETS
        and "shared_outputs" not in entry
        and "train.manifest" in entry.get("inputs", {})
    ):
        entry = official_shared_entry(entry)
    return entry


def official_shared_entry(entry: dict) -> dict:
    """为官方入口声明共享物理输出；阶段依赖仅取该入口确实声明的键。"""
    from copy import deepcopy

    value = deepcopy(entry)
    value["shared_outputs"] = {
        "physical_dataset": {
            "kind": "dataset",
            "stage": "rawprep",
            "name_key": "dataset.processed_name",
            "manifest": "manifest.json",
            "consumer_binding": "train.manifest",
        }
    }
    for key in ("root", "train", "test", "eval"):
        binding = "paths.datasets." + key
        if binding in value["outputs"]:
            value["outputs"][binding] = "{shared_physical_dataset_dir}" + (
                "" if key == "root" else "/" + key
            )
    inputs = value.get("inputs", {})
    declarations = {
        "rawprep": [(key, None) for key in inputs if key.startswith("dataset.")],
        "trainprep": [
            ("train.manifest", "rawprep"),
            ("trainprep.normalization.statistics", None),
            ("dataset.partition", None),
        ],
        "model": [("train.manifest", "rawprep"), ("train.preparation", "trainprep")],
        "train": [
            ("train.preparation", "trainprep"),
            ("train.resume", None),
            ("model.initial_weights", None),
        ],
        "infer": [
            ("infer.preparation", "trainprep"),
            ("train.preparation", "trainprep"),
            ("infer.checkpoint", "train"),
        ],
        "post": [("post.results", "infer"), ("infer.results", "infer")],
    }
    if "stage_inputs" not in value:
        value["stage_inputs"] = {
            stage: [
                {"key": key, **({"provided_by": producer} if producer else {})}
                for key, producer in pairs
                if key in inputs
            ]
            for stage, pairs in declarations.items()
        }
    return value
