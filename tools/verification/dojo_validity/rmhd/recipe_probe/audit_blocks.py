"""对照旧293行自写代码与当前能力；把源码来源复用和调用行占比分开。"""

import argparse
import ast
import importlib.util
import json
from pathlib import Path


def main(study, proof):
    """复用上次计数规则，生成不改变历史分母的块级清单。"""
    study, proof = Path(study), Path(proof)
    old = json.loads((study / "reviews/code-volume/counts.json").read_text())
    spec = importlib.util.spec_from_file_location(
        "prior_count", study / "reviews/code-volume/audit.py"
    )
    audit = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(audit)
    rows = []
    mapping = {
        "round-00/source/prepare.py": [
            (1, 12, "配置与来源设置", "公开配置加载/路径解析；字段清单仍为领域声明"),
            (13, 20, "tar成员与轨迹身份", "file_fingerprint已有；tar分片名单适配为用户组件"),
            (21, 24, "HDF5读取及形状校验", "read_array/validate_layout已有；六字段组合需适配"),
            (25, 29, "逐轨迹总体矩合并", "accumulate_moments/fit_statistics已有"),
            (30, 33, "数组保存与处理回执", "save_arrays/read_arrays与execute_samples已有"),
            (34, 36, "统计冻结与保存", "save_json/统计能力已有；std floor按科学协议声明"),
            (38, 40, "正反归一化物化", "Standardization已有；分片和轴连接需适配"),
            (41, 50, "500epoch抽样审计", "独立协议校验，不应由被测采样器自证"),
        ],
        "round-05/source/train.py": [
            (1, 25, "运行配置与路径/输出设置", "load_recipe_config/TrainingRun已有；参数改入YAML"),
            (
                26,
                40,
                "可恢复混合窗口流",
                "公开stream承接；现成IterationStream不覆盖尾批和此抽样顺序",
            ),
            (
                42,
                60,
                "模型/优化器/数据装配",
                "initialize_weights/read_arrays/construct已有；学习率与设备声明保留",
            ),
            (61, 65, "窗口批次适配", "window_slices已有；批量堆叠和设备连接为用户组件"),
            (66, 71, "逐样本逐场相对RMSE", "现有compare整体范数不等价；本地objective可承接"),
            (
                72,
                77,
                "每轮损失/内存/时间日志",
                "训练history/writer已有；协议专属时间账本与样本权重仍需定义",
            ),
            (78, 78, "返回科学损失", "普通objective接口连接"),
            (
                79,
                107,
                "验证窗口/选优/时间记录",
                "trajectory_metrics和checkpoint已有；raw/EMA验证选优政策需局部装配",
            ),
            (108, 112, "raw与EMA评价连接", "MovingAverage已有；候选比较策略为用户组件"),
            (
                113,
                122,
                "合同/完成性/检查点复核",
                "train_model/state保存已有；独立复核不能只由框架自证",
            ),
            (124, 127, "配置加载与启动连接", "load_recipe_config/launch已有"),
        ],
        "round-05/source/evaluate.py": [
            (1, 12, "导入/路径与候选动态加载", "公开配置与构造可复用；冻结候选装载属于提交合同"),
            (14, 20, "独立进程预测服务", "实验IPC探测；不应伪计为科学模型或由被测框架自证"),
            (
                22,
                32,
                "验证数据/窗口/预测合同",
                "read_arrays/window_slices/measure已有；分片与完整输出门禁为连接",
            ),
            (
                33,
                42,
                "独立FP64复算/身份/指标记录",
                "trajectory_metrics已调用；NumPy独立复核必须保留独立性",
            ),
            (44, 48, "本地完整预测延迟", "measure已调用；预热和输入遍历协议仍需装配"),
            (49, 60, "跨进程传输时延/退出核验", "实验专属进程与IPC协议，不是Dojo算法缺失"),
            (
                61,
                65,
                "汇总/摘要/写结果与入口",
                "save_json/file_fingerprint已有；指标口径声明留在实验侧",
            ),
        ],
        "round-05/source/initialize.py": [
            (1, 13, "构造/加载/路径设置", "construct/initialize_weights/load_mapped_weights已有"),
            (
                14,
                33,
                "Net2Wider与扰动/等价检查",
                "结构特有算法需用户组件；通用映射不能执行通道复制变换",
            ),
            (34, 47, "宽网预测/延迟复核", "measure/推理执行已有；等价与延迟准入为独立核验"),
        ],
        "round-05/source/prepare.py": [
            (
                1,
                18,
                "缓存身份/有限值/布局复核",
                "read_arrays/validate_layout已有；轨迹名单与无污染要求属协议",
            )
        ],
        "round-05/submission/model.py": [
            (1, 24, "残差U-Net算法", "既有其他U-Net权重结构不等价；本地网络可直接接入")
        ],
        "round-05/submission/predictor.py": [
            (
                1,
                23,
                "模型恢复/接口/设备/预测转换",
                "initialize_weights/inference_execution/Standardization已有；数组合同仍需显式连接",
            )
        ],
    }
    source = Path(old["experiment"])
    for f in old["files"]:
        if f["path"] not in mapping:
            continue
        remaining = set(f["code_lines"]) - set(f["dojo_use_lines"]) - set(f["dojo_import_lines"])
        allocated = set()
        for start, end, title, assessment in mapping[f["path"]]:
            selected = sorted(remaining & set(range(start, end + 1)))
            assert not allocated.intersection(selected)
            allocated.update(selected)
            rows.append(
                {
                    "file": f["path"],
                    "start": start,
                    "end": end,
                    "title": title,
                    "local_lines": len(selected),
                    "line_numbers": selected,
                    "assessment": assessment,
                }
            )
        assert allocated == remaining, (f["path"], remaining - allocated)
    assert sum(x["local_lines"] for x in rows) == 293

    def count(paths):
        files = []
        for p in paths:
            physical = audit.analyze(p.read_text())
            canonical = audit.analyze(ast.unparse(ast.parse(p.read_text())) + "\n")
            files.append(
                {
                    "file": str(p),
                    "physical": {k: physical[k] for k in audit.KEYS},
                    "canonical": {k: canonical[k] for k in audit.KEYS},
                }
            )

        def total(key):
            items = [f[key] for f in files]
            t = audit.totals(items)
            t["with_import_lexical_ratio"] = (
                t["dojo_expression_tokens"] + t["dojo_import_tokens"]
            ) / t["lexical_tokens"]
            return t

        return {"files": files, "physical": total("physical"), "canonical": total("canonical")}

    reference_files = [
        source / p
        for p in old["rounds"][5]["files"]
        if next(f for f in old["files"] if f["path"] == p)["role"] == "scientific"
    ]
    new_files = sorted((proof / "case").glob("*.py"))
    full_example = sorted((proof / "base-example").glob("*.py"))
    report = {
        "old_total_scientific_sloc": 342,
        "old_dojo_import_or_use_sloc": 49,
        "old_local_sloc": 293,
        "blocks": rows,
        "old_final": count(reference_files),
        "current_prototype": count(new_files),
        "fully_copied_existing_example": count(full_example),
        "metric_limit": "D/I counts integration expressions, not borrowed implementation. A wholly copied example is 100% source reuse but generally has much lower D/I ratio. Canonical formatting and lexical metrics expose original semicolon/multiline sensitivity.",
        "comparison_limit": "New prototype includes complete recipe and standalone post, optional baseline and residual models. It is not the same functional denominator as old final script. Newly written local components are not pre-existing Dojo code.",
    }
    (proof / "code-gap-analysis.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
    print(
        json.dumps(
            {
                key: report[key]["physical"]
                for key in ["old_final", "current_prototype", "fully_copied_existing_example"]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--study", required=True)
    parser.add_argument("--proof", required=True)
    args = parser.parse_args()
    main(args.study, args.proof)
