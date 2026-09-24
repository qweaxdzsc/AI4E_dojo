"""NASA 工况表与双圆柱训练降维准备；来源、时间和字段语义在应用层绑定。"""

import hashlib
import json
from pathlib import Path

import h5py
import numpy as np

from ai4e_contrib.application.classic_networks.preparation import read_prepared as read_classic
from ai4e_contrib.application.datasets.nasa_crm.constants import (
    CONDITION_FIELDS,
    GLOBAL_TARGET_FIELDS,
)
from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays, save_arrays
from ai4e_core.abilities.data.save.arrays import save_json
from ai4e_core.abilities.data.save.surrogate import read_state, save_state
from ai4e_core.abilities.modeling.models.pod import POD
from ai4e_core.abilities.modeling.modules.polynomial import PolynomialBasis
from ai4e_core.abilities.training.reduced_basis import fit_pod


def _statistics(values):
    mean, scale = values.mean(axis=0), values.std(axis=0)
    scale = np.where(scale > 0, scale, 1.0)
    return {"mean": mean.tolist(), "scale": scale.tolist()}


def _normalize(values, statistics):
    return (values - np.asarray(statistics["mean"])) / np.asarray(statistics["scale"])


def _relative(root, path):
    target = (root / path).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError("准备引用越界")
    return target


def _read_nasa(path, split):
    path = Path(path).resolve()
    source_id = hashlib.sha256(str(path).encode()).hexdigest()[:16]
    inputs, targets, names = [], [], []
    with h5py.File(path, "r") as stream:
        for name in sorted(stream):
            group = stream[name]
            if not isinstance(group, h5py.Group):
                continue
            inputs.append([float(group.attrs[key]) for key in CONDITION_FIELDS])
            targets.append([float(group.attrs[key]) for key in GLOBAL_TARGET_FIELDS])
            names.append(name)
    x, y = np.asarray(inputs, dtype=np.float64), np.asarray(targets, dtype=np.float64)
    if not names or x.shape != (len(names), 6) or y.shape != (len(names), 3):
        raise ValueError("NASA 文件没有完整六工况/三响应表")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise ValueError("NASA 工况或响应非有限")
    attributes_digest = hashlib.sha256(
        x.tobytes() + y.tobytes() + json.dumps(names).encode()
    ).hexdigest()
    return (
        x,
        y,
        [f"{split}:{source_id}:{name}" for name in names],
        {
            "path": str(path),
            "file_size": path.stat().st_size,
            "source_id": source_id,
            "attribute_sha256": attributes_digest,
            "scope": "selected group attributes only",
        },
    )


def prepare_nasa(train_h5, test_h5, output):
    """读取全局属性表，训练独立拟合统计，保存自包含准备清单。

    不读取或复制百万点网格；本产物不是平台物理网格准备。不同来源文件中的
    同名 Sample 保留 source_id 与 split，不因为组名相同合并实体。
    """
    if Path(train_h5).resolve() == Path(test_h5).resolve():
        raise ValueError("NASA 训练与测试来源不能是同一文件")
    raw = {"train": _read_nasa(train_h5, "train"), "test": _read_nasa(test_h5, "test")}
    if raw["train"][3]["attribute_sha256"] == raw["test"][3]["attribute_sha256"]:
        raise ValueError("NASA 训练与测试属性表内容完全相同，不能以文件路径区分样本")
    conditions = {}
    complete_rows = {}
    for split, (inputs, targets, _, _) in raw.items():
        complete_rows[split] = {tuple(row) for row in np.column_stack((inputs, targets))}
        grouped = {}
        for inputs_row, target_row in zip(inputs, targets, strict=True):
            grouped.setdefault(tuple(inputs_row), set()).add(tuple(target_row))
        conditions[split] = grouped
    repeated_rows = complete_rows["train"] & complete_rows["test"]
    if repeated_rows:
        raise ValueError(
            f"NASA 跨训练/测试存在 {len(repeated_rows)} 条完全相同工况与响应，拒绝数据泄漏"
        )
    shared_conditions = conditions["train"].keys() & conditions["test"].keys()
    # 相同工况但不同响应可能来自重复实验，保留并显式登记，不误拒绝合法数据。
    distinct_response_pairs = sum(
        len(conditions["train"][key]) * len(conditions["test"][key]) for key in shared_conditions
    )
    statistics = {
        "input": _statistics(raw["train"][0]),
        "target": _statistics(raw["train"][1]),
        "fit_ids": raw["train"][2],
    }
    x_train = _normalize(raw["train"][0], statistics["input"])
    matrix = PolynomialBasis(6, 2)(x_train)
    rank = int(np.linalg.matrix_rank(matrix))
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    splits = {}
    for split, (x, y, ids, source) in raw.items():
        path = save_arrays(
            root / split,
            {
                "input": _normalize(x, statistics["input"]),
                "target": _normalize(y, statistics["target"]),
                "physical_input": x,
                "physical_target": y[:, None, :],
                "valid": np.ones((len(x), 1), dtype=bool),
                "entity_ids": np.arange(len(x), dtype=np.int64)[:, None],
            },
            kind="surrogate-inputs-v1",
            metadata={
                "case": "nasa_global",
                "split": split,
                "ids": ids,
                "source": source,
                "input_fields": list(CONDITION_FIELDS),
                "fields": list(GLOBAL_TARGET_FIELDS),
                "units": ["dimensionless"] * 3,
                "statistics": statistics,
                "scope": "global coefficient table; not a platform mesh preparation",
            },
        )
        splits[split] = str(Path(path).relative_to(root))
    save_json(
        root / "manifest.json",
        {
            "kind": "surrogate-preparation-v1",
            "case": "nasa_global",
            "splits": splits,
            "statistics": statistics,
            "diagnostics": {
                "quadratic_columns": matrix.shape[1],
                "quadratic_rank": rank,
                "shared_input_condition_count": len(shared_conditions),
                "shared_input_distinct_response_pair_count": distinct_response_pairs,
                "duplicate_definition": "exact finite six-input/three-response rows; distinct response pairs counted after within-split deduplication",
            },
        },
    )
    return str(root / "manifest.json")


def _window_identity(record, arrays):
    ids = record["metadata"]["ids"]
    history, future = arrays["physical_input"], arrays["physical_target"]
    if history.ndim != 5 or history.shape[1] != 3 or history.shape[2:] != future.shape[1:]:
        raise ValueError("双圆柱须为 [N,3,H,W,C] 历史及同空间下一帧")
    if future.shape[0] != len(ids) or arrays["times"].shape != (len(ids), 4):
        raise ValueError("时间/窗口身份数量不一致")
    if len(set(ids)) != len(ids):
        raise ValueError("窗口身份重复")
    entities = np.asarray(arrays["entity_ids"])
    if (
        entities.shape != future.shape[:-1]
        or not np.all(entities == entities[0])
        or len(np.unique(entities[0])) != entities[0].size
    ):
        raise ValueError("POD 需要相同原实体行序")
    if arrays["valid"].shape != future.shape[:-1] or not np.all(arrays["valid"]):
        raise ValueError("本批 POD 需要共同完整有效网格，不以填零冒充共同空间")
    parsed = []
    for identity, times in zip(ids, arrays["times"], strict=True):
        trajectory, start = identity.rsplit("_", 1)
        if not trajectory or float(start) != times[0] or not np.all(np.diff(times) > 0):
            raise ValueError("窗口起点/时间身份不一致")
        parsed.append((trajectory, tuple(float(t) for t in times)))
    return parsed


def prepare_pod_data(classic_manifest, output, rank=2):
    """一次拟合训练快照 POD 并物化系数；真实调用由主控串行调度。

    历史和未来都使用训练 target 通道统计，绝不使用 classic 的 input 统计。
    每个 trajectory/time 只进入 POD 一次；重复引用若数值不同则拒绝。
    输出包含独立基状态及物理目标/身份，无需旧准备目录即可恢复推理和后处理。
    """
    if type(rank) is not int or rank not in (2, 3):
        raise ValueError("本批 POD 秩显式选择 2 或 3")
    groups = {split: read_classic(classic_manifest, split) for split in ("train", "test")}
    identities = {split: _window_identity(*pair) for split, pair in groups.items()}
    if {t for t, _ in identities["train"]} & {t for t, _ in identities["test"]}:
        raise ValueError("训练与验证轨迹重叠")
    train_record, train_arrays = groups["train"]
    meta = train_record["metadata"]
    if meta["case"] != "double_cylinder":
        raise ValueError("POD 时间准备只接受双圆柱案例")
    statistics = meta["statistics"]
    if statistics["fit_ids"] != meta["ids"]:
        raise ValueError("冻结 target 统计并非由当前训练名单拟合")
    target_stats = statistics["target"]
    mean, scale = np.asarray(target_stats["mean"]), np.asarray(target_stats["scale"])
    channels = train_arrays["physical_target"].shape[-1]
    if (
        mean.shape != (channels,)
        or scale.shape != (channels,)
        or not np.isfinite(mean).all()
        or not np.isfinite(scale).all()
        or (scale <= 0).any()
    ):
        raise ValueError("训练 target 统计与字段不符")
    for record, arrays in groups.values():
        other = record["metadata"]
        if (
            other["fields"] != meta["fields"]
            or other["units"] != meta["units"]
            or other["statistics"] != statistics
            or arrays["physical_target"].shape[1:] != train_arrays["physical_target"].shape[1:]
            or not np.array_equal(arrays["entity_ids"][0], train_arrays["entity_ids"][0])
        ):
            raise ValueError("训练/验证字段、统计或共同空间不同")
    snapshots = {}
    for row, (trajectory, times) in enumerate(identities["train"]):
        frames = [*train_arrays["physical_input"][row], train_arrays["physical_target"][row]]
        for time, frame in zip(times, frames, strict=True):
            key = (trajectory, time)
            flat = np.asarray(frame, dtype=np.float64).reshape(-1)
            if key in snapshots and not np.array_equal(snapshots[key], flat):
                raise ValueError("相同训练轨迹/时间快照内容不同")
            snapshots[key] = flat
    shape = train_arrays["physical_target"].shape[1:]
    unique = np.stack(list(snapshots.values())).reshape(-1, *shape)
    normalized = _normalize(unique, target_stats).reshape(len(unique), -1)
    state = fit_pod(normalized, rank)
    pod = POD(state)
    encoded = {}
    for split, (_, arrays) in groups.items():
        history = _normalize(np.asarray(arrays["physical_input"], dtype=np.float64), target_stats)
        future = _normalize(np.asarray(arrays["physical_target"], dtype=np.float64), target_stats)
        encoded[split] = (
            pod.encode(history.reshape(len(history), 3, -1)).reshape(len(history), -1),
            pod.encode(future.reshape(len(future), -1)),
        )
    feature_stats = _statistics(encoded["train"][0])
    tail = PolynomialBasis(3 * rank, 1)(_normalize(encoded["train"][0], feature_stats))
    tail_rank = int(np.linalg.matrix_rank(tail))
    if tail.shape[1] >= tail.shape[0] or tail_rank != tail.shape[1]:
        raise ValueError(f"历史系数一次尾项不可识别: rank={tail_rank}, shape={tail.shape}")
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    pod_path = save_state(
        root / "pod",
        state,
        context={
            "fields": meta["fields"],
            "units": meta["units"],
            "field_shape": list(shape),
            "statistics": target_stats,
            "fit_snapshot_ids": [[trajectory, time] for trajectory, time in snapshots],
        },
    )
    splits = {}
    for split, (record, arrays) in groups.items():
        features, target = encoded[split]
        path = save_arrays(
            root / split,
            {
                "input": _normalize(features, feature_stats),
                "target": target,
                "physical_input": arrays["physical_input"],
                "physical_target": arrays["physical_target"],
                "valid": arrays["valid"],
                "entity_ids": arrays["entity_ids"],
                "times": arrays["times"],
            },
            kind="surrogate-inputs-v1",
            metadata={
                "case": "double_cylinder_pod",
                "split": split,
                "ids": record["metadata"]["ids"],
                "fields": meta["fields"],
                "units": meta["units"],
                "field_shape": list(shape),
                "statistics": {
                    "target": target_stats,
                    "input": feature_stats,
                    "fit_ids": meta["ids"],
                },
                "rank": rank,
                "history_length": 3,
            },
        )
        splits[split] = str(Path(path).relative_to(root))
    save_json(
        root / "manifest.json",
        {
            "kind": "surrogate-preparation-v1",
            "case": "double_cylinder_pod",
            "splits": splits,
            "pod": str(Path(pod_path).relative_to(root)),
            "source_manifest_sha256": digest(classic_manifest),
            "diagnostics": {
                "unique_training_snapshots": len(snapshots),
                "history_tail_rank": tail_rank,
                "history_tail_columns": tail.shape[1],
            },
        },
    )
    return str(root / "manifest.json")


def read_prepared(path, split):
    """读取自包含拟合输入，不返回旧来源的可执行引用。"""
    path = Path(path).resolve()
    index = json.loads(path.read_text())
    if index["kind"] != "surrogate-preparation-v1" or split not in {"train", "test"}:
        raise ValueError("代理准备类型或分片不支持")
    record, arrays = read_arrays(
        _relative(path.parent, index["splits"][split]), kind="surrogate-inputs-v1"
    )
    if record["metadata"]["case"] != index["case"] or record["metadata"]["split"] != split:
        raise ValueError("准备分片标签不一致")
    return record, arrays


def read_pod(path):
    """从准备目录内部读取同一次冻结 POD 状态及其语义。"""
    path = Path(path).resolve()
    index = json.loads(path.read_text())
    if index["kind"] != "surrogate-preparation-v1" or index["case"] != "double_cylinder_pod":
        raise ValueError("此准备没有 POD 表示")
    state, context = read_state(_relative(path.parent, index["pod"]))
    return POD(state), context


def preparation_identity(path):
    """绑定准备及其子清单内容，移动整个目录不改变身份。

    子清单自身记录数组摘要，实际读入仍由 read_arrays 校验数组内容。
    这里不只摘要顶层索引，避免同名分片或 POD 被替换后仍误认为原准备。
    """
    path = Path(path).resolve()
    index = json.loads(path.read_text())
    if index["kind"] != "surrogate-preparation-v1":
        raise ValueError("不是代理准备")
    entries = {"index": digest(path)}
    for split in ("train", "test"):
        entries[split] = digest(_relative(path.parent, index["splits"][split]))
    if "pod" in index:
        entries["pod"] = digest(_relative(path.parent, index["pod"]))
    return hashlib.sha256(json.dumps(entries, sort_keys=True).encode()).hexdigest()
