"""验证选优的本地连接：已有工具负责比较、模式保护和完整状态交接。"""

import math
from copy import deepcopy

from ai4e_core.abilities.inference.execution import inference_execution
from ai4e_core.abilities.training.selection import BestMetric


def epoch_records(rng, epoch, *, count):
    """抽样规则可替换；轮次与 PCG64 状态交给 EpochBatchStream。"""
    return rng.permutation(count).tolist()


def validation_samples(samples, count):
    """按来源训练名单末尾留出验证，不触碰测试分片；来源行号保持。"""
    records = [dict(sample) for sample in samples]
    training = [sample for sample in records if sample["split"] == "train"]
    if type(count) is not int or not 0 < count < len(training):
        raise ValueError("验证人数须为正且小于来源训练人数")
    for sample in training[-count:]:
        sample["source_split"] = sample["split"]
        sample["split"] = "validation"
    return records


class ResearchSelection:
    """聚合选择状态与真正受评权重，只有本例承担它们的交接约定。"""

    def __init__(self, model, *, contract):
        self.selector = BestMetric(mode="min", tie="first")
        self.selected = None
        self.evaluations = []
        self.contract = deepcopy(contract)
        self.template = deepcopy(model)

    def evaluate(self, index, model, ema, batch, count, objective, session):
        """普通/EMA同口径验证；写入成功后提交，保持训练随机流与模式。"""
        shadow = deepcopy(model)
        shadow.load_state_dict(ema.state)
        values = batch(list(range(count)))
        metrics = {}
        for source, candidate in (("raw", model), ("ema", shadow)):
            with inference_execution(candidate):
                value = float(objective(candidate, values))
            metrics[source] = value
            if self.selector.improves(value):
                selected = {
                    "model": deepcopy(candidate.state_dict()),
                    "updates": index,
                    "source": source,
                    "value": value,
                    "contract": deepcopy(self.contract),
                }
                session.checkpoint("best", selected, namespace="train")
                self.selector.commit(value, step=index, source=source)
                self.selected = selected
        self.evaluations.append({"updates": index, **metrics})

    def state_dict(self):
        """保存最优快照本身，不依赖可能被覆盖或移动的best文件路径。"""
        return deepcopy(
            {
                "selector": self.selector.state_dict(),
                "selected": self.selected,
                "evaluations": self.evaluations,
            }
        )

    def validate_state_dict(self, state):
        """恢复前校验指标/位置/来源/模型结构，失败不触碰现有选择。"""
        if set(state) != {"selector", "selected", "evaluations"}:
            raise ValueError("研究选优状态字段不完整")
        self.selector.validate_state_dict(state["selector"])
        selected, policy = state["selected"], state["selector"]
        if selected is None:
            if policy["best"] is not None:
                raise ValueError("最佳指标缺少权重快照")
        else:
            if (
                selected["updates"] != policy["step"]
                or selected["source"] != policy["source"]
                or selected["value"] != policy["best"]
                or selected["contract"] != self.contract
            ):
                raise ValueError("最佳指标、权重来源或恢复契约不相容")
            deepcopy(self.template).load_state_dict(selected["model"], strict=True)
        if not isinstance(state["evaluations"], list) or any(
            type(row["updates"]) is not int
            or row["updates"] < 1
            or not all(math.isfinite(row[key]) for key in ("raw", "ema"))
            for row in state["evaluations"]
        ):
            raise ValueError("验证历史非法")

    def load_state_dict(self, state):
        """预检全部成功后更新本地内存，不访问外部文件。"""
        self.validate_state_dict(state)
        self.selector.load_state_dict(state["selector"])
        self.selected = deepcopy(state["selected"])
        self.evaluations = deepcopy(state["evaluations"])
