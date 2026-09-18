"""训练结束后按设置写出预测或网格；不打开训练期评价。"""

import json
from copy import deepcopy
from pathlib import Path

from ai4e_core.applications.aero_cfd.infer import anchor as infer_stage


def _current_preparation(reference):
    """只接受现行 version=2 准备；样本名单从记录读取，消费交给独立推理。"""
    path = reference.get("preparation") if isinstance(reference, dict) else reference
    if not path:
        raise ValueError("训练结束写出需要准备记录")
    try:
        record = json.loads(Path(path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"train.preparation: 无法读取准备记录: {exc}") from exc
    if record.get("version") != 2:
        raise ValueError(
            "preparation_requires_regeneration: 数据准备已改用现行配置方式，这份旧准备不能再训，请按现行数据准备重新生成。"
        )
    return str(path), record


def export_training_fields(
    config,
    *,
    trained,
    session,
    dataset_component,
    model_component,
    predictions=False,
    meshes=False,
    split="test",
    preparation=None,
):
    """把本次训练权重按独立推理保存正文写进同一运行数据目录。

    现行准备只走 trainprep.preparation 与锚点推理，不调用旧物理准备接口。
    """
    if meshes and not predictions:
        raise ValueError("写出网格需要同时打开写出预测")
    if not predictions and not meshes:
        return None
    if getattr(session, "dry_run", False):
        return None
    if not isinstance(trained, dict) or "checkpoints" not in trained:
        raise ValueError("训练结束写出需要已提交的检查点")
    cfg = deepcopy(config)
    infer = cfg.setdefault("infer", {})
    infer["save_predictions"] = True
    infer["export_vtk"] = bool(meshes)
    infer["evaluate"] = False
    infer["query"] = bool(meshes)
    infer["split"] = split or "test"
    infer["device"] = (cfg.get("train") or {}).get("device") or infer.get("device") or "cpu"
    infer["checkpoint"] = None
    reference = preparation or (cfg.get("train") or {}).get("preparation")
    path, record = _current_preparation(reference)
    cfg.setdefault("train", {})["preparation"] = path
    infer["preparation"] = path
    samples = list((record.get("partitions") or {}).get(infer["split"]) or [])
    if not samples:
        raise ValueError(f"训练写出分片 {infer['split']} 没有样本")
    infer["samples"] = samples
    job = infer_stage.open_inference(
        cfg,
        dataset_component=dataset_component,
        model_component=model_component,
        session=session,
        trained=trained,
    )
    job = infer_stage.configure_restore(job, settings=cfg.get("model"))
    job = infer_stage.configure_prediction(job, settings=cfg.get("infer"))
    job = infer_stage.configure_physical_output(job)
    job = infer_stage.configure_selection(job, fields=(cfg.get("infer") or {}).get("fields"))
    job = infer_stage.configure_evaluation(job, settings=cfg.get("infer"))
    job = infer_stage.configure_save(
        job,
        output=session.output_dir("infer") / "predictions",
        settings=cfg.get("infer"),
    )
    job = infer_stage.configure_mesh_export(job, settings=cfg.get("infer"))
    return infer_stage.execute(job)
