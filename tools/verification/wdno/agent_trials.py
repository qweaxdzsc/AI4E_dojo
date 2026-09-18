"""独立Agent现场实验的固定产物核验；不执行其代码或替它组装研究流程。"""

import argparse
import json
from pathlib import Path

import numpy as np
import torch

from ai4e_core.abilities.data.save.array_manifest import digest, read_arrays


def verify_trial(directory: Path) -> dict:
    """核对真实运行、更新状态、新增物理量和独立post；身份独立性另由会话记录证实。"""
    directory = Path(directory)
    claim = json.loads((directory / "acceptance.json").read_text())
    if claim.get("status") != "passed":
        raise ValueError("独立研究未报告完整成功")
    if not (directory / "initial-draft").is_dir() or not (directory / "commands.log").is_file():
        raise ValueError("缺少初稿或实际命令记录")
    summaries = {}
    for label in ("fresh", "resumed", "post_only"):
        reference = claim["runs"][label]
        actual = json.loads(Path(reference["summary_path"]).read_text())
        if actual != reference["summary"] or actual["research_status"] != "completed":
            raise ValueError("运行报告缺失、被替换或未完成")
        summaries[label] = actual
    states = [
        torch.load(
            summaries[label]["reports"]["train"]["checkpoint"],
            map_location="cpu",
            weights_only=False,
        )
        for label in ("fresh", "resumed")
    ]
    if [x["updates"] for x in states] != [2, 3]:
        raise ValueError("未完成从零2次更新并续至3次")
    if states[1]["history"][:2] != states[0]["history"]:
        raise ValueError("恢复损失前缀变化")
    if not any(
        not torch.equal(states[0]["model"][k], states[1]["model"][k]) for k in states[0]["model"]
    ):
        raise ValueError("续训没有实际更新权重")
    files, metrics = {}, {}
    for label in ("fresh", "resumed"):
        report = summaries[label]["reports"]
        if "mass_audit" not in report:
            raise ValueError("新增步骤未执行")
        for split, path in report["infer"].items():
            record, arrays = read_arrays(path, kind="spatiotemporal-result-v1")
            expected_ids = claim["indices"][split]
            if arrays["ids"].tolist() != expected_ids:
                raise ValueError("预测样本身份与预定名单不一致")
            # 独立按已声明的均匀点权定义复算，不导入Agent的能力函数。
            predicted = arrays["prediction"].astype(np.float64).sum(axis=-1) / 120
            target = arrays["target"].astype(np.float64).sum(axis=-1) / 120
            expected = {
                "mass_density_prediction": predicted,
                "mass_density_target": target,
                "mass_density_error": predicted - target,
            }
            for name, values in expected.items():
                if record["metadata"]["derived_fields"][name] != {
                    "units": "source_u",
                    "axes": ["sample", "time"],
                }:
                    raise ValueError("派生量单位或轴不符")
                np.testing.assert_array_equal(arrays[name], values)
            mae = float(np.abs((predicted - target)[:, 1:]).mean())
            np.testing.assert_allclose(
                report["post"][split]["mass_density_mae_exclude_initial"], mae, rtol=0, atol=0
            )
            metrics[f"{label}_{split}_mass_mae"] = mae
            files[str(path)] = digest(path)
    if summaries["post_only"]["reports"]["post"] != summaries["resumed"]["reports"]["post"]:
        raise ValueError("独立post改变固定结果评价")
    if [x["stage"] for x in summaries["post_only"]["stage_events"]] != ["post"]:
        raise ValueError("独立post执行了其他阶段")
    return {
        "passed": True,
        "updates": [2, 3],
        "fixed_results": files,
        "metrics": metrics,
        "paper_reproduced": False,
        "independence_evidence": "separate agent session; artifact checks do not prove identity",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trial", type=Path, required=True)
    args = parser.parse_args()
    result = verify_trial(args.trial)
    path = args.trial / "independent-verification.json"
    with path.open("x") as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
    print(path)


if __name__ == "__main__":
    main()
