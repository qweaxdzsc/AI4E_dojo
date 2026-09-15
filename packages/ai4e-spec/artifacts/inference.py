"""独立推理的轻量跨包交接；不包含模型、数组或服务器任意路径。"""

import re
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(frozen=True)
class InferenceCheckpointRef:
    """用户实际选中的训练检查点及内容修订。"""

    id: str
    revision: str


@dataclass(frozen=True)
class InferenceRequest:
    """固定批次选择；单检查点在子运行内顺序处理全部所选样本。"""

    expected_revision: str
    checkpoints: list[InferenceCheckpointRef]
    samples: list[str] = field(default_factory=list)
    split: str = "test"
    device: str = "auto"
    name: str = "批量推理"
    options: dict[str, Any] = field(default_factory=dict)
    idempotency_key: str | None = None
    sample_selection: list[dict[str, str]] | None = None
    fields: list[str] | None = None
    metrics: list[str] | None = None

    @classmethod
    def from_dict(cls, value: dict) -> "InferenceRequest":
        """在界面、脚本和管理入口执行同一选择校验。"""
        if not isinstance(value, dict):
            raise ValueError("inference_request_required")  # noqa: TRY004 - HTTP 业务校验统一错误
        known = set(cls.__dataclass_fields__)
        if set(value) - known:
            raise ValueError("unknown_inference_parameter")
        refs = value.get("checkpoints")
        samples = value.get("samples")
        selection = value.get("sample_selection")
        if selection is not None:
            if "samples" in value or "split" in value:
                raise ValueError("ambiguous_inference_samples")
            if not isinstance(selection, list) or not selection:
                raise ValueError("inference_samples_required")
            for ref in selection:
                if (
                    not isinstance(ref, dict)
                    or set(ref) != {"split", "sample"}
                    or not all(isinstance(v, str) and v.strip() for v in ref.values())
                ):
                    raise ValueError("invalid_inference_sample_reference")
            if len({(r["split"], r["sample"]) for r in selection}) != len(selection):
                raise ValueError("duplicate_inference_samples")
            samples = [r["sample"] for r in selection]
        for key in ("fields", "metrics"):
            if key in value:
                items = value[key]
                if (
                    not isinstance(items, list)
                    or not items
                    or any(not isinstance(v, str) or not v for v in items)
                    or len(set(items)) != len(items)
                ):
                    raise ValueError("invalid_inference_" + key)
        if not isinstance(refs, list) or not refs:
            raise ValueError("inference_checkpoints_required")
        if (
            not isinstance(samples, list)
            or not samples
            or any(not isinstance(s, str) or not s for s in samples)
        ):
            raise ValueError("inference_samples_required")
        if selection is None and len(samples) != len(set(samples)):
            raise ValueError("duplicate_inference_samples")
        parsed = []
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {"id", "revision"}:
                raise ValueError("fixed_checkpoint_reference_required")
            if not all(isinstance(v, str) and v for v in ref.values()):
                raise ValueError("fixed_checkpoint_reference_required")
            parsed.append(InferenceCheckpointRef(**ref))
        if len({r.id for r in parsed}) != len(parsed):
            raise ValueError("duplicate_inference_checkpoints")
        device = value.get("device", "auto")
        if not isinstance(device, str) or not re.fullmatch(r"auto|cpu|mps|cuda(?::\d+)?", device):
            raise ValueError("invalid_inference_device")
        if not isinstance(value.get("options", {}), dict):
            raise ValueError("invalid_inference_options")  # noqa: TRY004 - HTTP 业务校验统一错误
        options = dict(value.get("options", {}))
        if set(options) - {"evaluate", "save_predictions", "export_vtk", "query_chunk_size"}:
            raise ValueError("unsupported_inference_option")
        for key in ("evaluate", "save_predictions", "export_vtk"):
            options.setdefault(key, True)
            if not isinstance(options[key], bool):
                raise ValueError("invalid_inference_option: " + key)  # noqa: TRY004 - HTTP 业务校验统一错误
        size = options.setdefault("query_chunk_size", 16384)
        if not isinstance(size, int) or isinstance(size, bool) or size < 1:
            raise ValueError("invalid_query_chunk_size")
        if options["export_vtk"] and not options["save_predictions"]:
            raise ValueError("mesh_requires_saved_predictions")
        if not options["evaluate"] and not options["save_predictions"]:
            raise ValueError("inference_output_required")
        for key in ("expected_revision", "split", "name"):
            candidate = value.get(key, {"split": "test", "name": "批量推理"}.get(key))
            if not isinstance(candidate, str) or not candidate.strip():
                raise ValueError("invalid_inference_" + key)
        key = value.get("idempotency_key")
        if key is not None and (not isinstance(key, str) or not key):
            raise ValueError("invalid_idempotency_key")
        return cls(**{**value, "checkpoints": parsed, "samples": list(samples), "options": options})

    def to_dict(self) -> dict:
        """返回仅含可持久化声明的副本。"""
        result = asdict(self)
        for key in ("sample_selection", "fields", "metrics"):
            if result[key] is None:
                result.pop(key)
        if self.sample_selection is not None:
            result.pop("samples")
            result.pop("split")
        return result

    def selections(self) -> list[dict[str, str]]:
        """返回保留分片身份的有序选择，不把同名样本合并。"""
        return (
            self.sample_selection
            if self.sample_selection is not None
            else [{"split": self.split, "sample": s} for s in self.samples]
        )


@dataclass(frozen=True)
class InferenceResultRef:
    """固定推理结果身份；具体成员通过受控文件接口解析。"""

    task_id: str
    batch_id: str
    run_id: str
    checkpoint_revision: str
    sample: str
    split: str = "test"


from typing import NotRequired, TypedDict


class InferenceSampleSelection(TypedDict):
    """分片内样本身份，不用样本名独自充当跨分片键。"""

    split: str
    sample: str


class InferenceFieldDescription(TypedDict):
    """可选物理量的稳定描述。"""

    id: str
    domain: str
    field: str
    component: str
    label: str
    category: str
    unit: str | None
    available: bool
    evaluable: bool
    default: bool
    reason: NotRequired[str]


class InferenceMetricDescription(TypedDict):
    """指标公式与适用范围；数值算法由core实现。"""

    id: str
    label: str
    category: str
    formula: str
    unit_rule: str
    scope: str
    default: bool


class InferenceStatistic(TypedDict):
    """固定结果按样本等权统计，不混同历史全元素累计。"""

    checkpoint_id: str
    checkpoint: str
    split: str
    field_id: str
    field: str
    metric: str
    unit: str | None
    mean: float | None
    median: float | None
    p90: float | None
    max: float | None
    valid: int
    expected: int
    undefined: int
    complete: bool
    prediction_seconds: float | None
    throughput: float | None
    algorithm: NotRequired[str]
    checkpoint_revision: NotRequired[str | None]
    source_runs: NotRequired[list[str]]
    source_protocols: NotRequired[list[str]]
    undefined_reasons: NotRequired[list[str]]
