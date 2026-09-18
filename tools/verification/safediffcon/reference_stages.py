"""冻结原定义的独立后训练与适配连接，仅共享数据容器和物理响应适配。

不调用 Dojo 的训练、校准、引导或采样编排。显式采用每轮开始校准、
完整阶段权重交接和真实更新数；这些修正不冒称原脚本未经修改的复现。
"""

import ast
import logging
import math
import random
from collections.abc import Callable
from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from typing import Optional

import numpy as np
import torch
from ema_pytorch import EMA

from ai4e_contrib.application.pde_control.safediffcon.stream import BatchStream
from ai4e_core.abilities.training.checkpoint import capture_iteration
from ai4e_core.applications.pde_control.contracts import digest, read_arrays


def definitions(path: Path, names: set[str], scope: dict) -> None:
    """仅执行已校验快照的指定原定义，避开无关 TensorFlow 顶层导入。"""
    nodes = [
        n
        for n in ast.parse(path.read_text()).body
        if isinstance(n, (ast.ClassDef, ast.FunctionDef)) and n.name in names
    ]
    if {n.name for n in nodes} != names:
        raise ValueError(f"原定义缺失: {path}")
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(path), "exec"), scope)  # noqa: S102


def seed_all(seed: int) -> None:
    """固定阶段随机量，与实验协议一致，不读取 Dojo 编排状态。"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.backends.mps.is_available():
        torch.mps.manual_seed(seed)
    torch.set_num_threads(4)


class Average:
    """原 EMA 对接共享记录容器，不改变其预热或更新计数。"""

    def __init__(self, model):
        self.raw = EMA(model, beta=0.995, update_every=10).to(next(model.parameters()).device)

    @property
    def state(self):
        """原库完整状态。"""
        return self.raw.state_dict()


class ReferenceStages:
    """调用原训练步和原校准类的独立控制阶段。"""

    def __init__(self, snapshot: Path, case: str):
        from reference import verify_source

        verify_source(snapshot)
        self.case = case
        self.source = snapshot / ("1D" if case == "burgers" else "tokamak")
        self.scale = (
            10
            if case == "burgers"
            else torch.tensor([2, 7, 2, 1, 2, 2, 2, 2, 1, 1, 2, 3], dtype=torch.float32).reshape(
                12, 1
            )
        )
        self.scope = {
            "torch": torch,
            "np": np,
            "logging": logging,
            "Dict": dict,
            "Optional": Optional,
            "Tuple": tuple,
            "List": list,
            "Callable": Callable,
            "InferenceConfig": object,
            "PostTrainConfig": object,
            "SCALER": self.scale,
        }
        if case == "burgers":
            definitions(
                self.source / "inference/guidance.py",
                {"calculate_guidance", "get_weight", "normalize_weights"},
                self.scope,
            )
            definitions(self.source / "posttrain/post_train.py", {"PostTrainPipeline"}, self.scope)
            definitions(self.source / "inference/inference_ft.py", {"InferenceFT"}, self.scope)
        else:
            definitions(self.source / "utils/metrics.py", {"calculate_safety_score"}, self.scope)
            definitions(
                self.source / "utils/guidance.py",
                {"calculate_weight", "normalize_weights", "GradientGuidance"},
                self.scope,
            )
            definitions(self.source / "inference/pipeline.py", {"InferencePipeline"}, self.scope)
        definitions(self.source / "inference/conformal.py", {"ConformalCalculator"}, self.scope)

    def config(self, settings: dict, device, *, previous_q=None, previous_weight=None):
        """把显式实验参数映射为原类使用的字段。"""
        return SimpleNamespace(
            device=device,
            num_cal_batch=math.ceil(settings.get("calibration_samples", 1) / 16),
            nt=11,
            nt_total=122,
            use_max_safety=True,
            u_bound=0.8,
            guidance_weights={"w_score": settings["weight"], "w_obj": 0.0, "w_safe": 1.0},
            guidance_scaler=settings["weight"],
            InfFT_Q=previous_q,
            safety_threshold=4.98,
            finetune_set="train" if previous_q is None else "test",
            use_guidance=False,
            wo_post_train=previous_q is None,
            finetune_quantile=previous_q,
            finetune_guidance_weights={"w_obj": 0.0, "w_safe": 1.0},
            finetune_guidance_scaler=previous_weight,
            loss_weights={"loss_train": 1.0, "loss_test": 0.0},
        )

    def weights(self, states, target, q, settings):
        """原权重函数及原归一化，保留全零回退。"""
        if self.case == "burgers":
            raw = self.scope["get_weight"](states, q, self.config(settings, states.device))
        else:
            raw = self.scope["calculate_weight"](
                states, target, 122, q, 4.98, 0.0, 1.0, settings["weight"]
            )
        return self.scope["normalize_weights"](raw)

    def calibration(
        self, model, states, target, q, settings, *, previous_q=None, previous_weight=None
    ):
        """直接执行原校准类，批次与统计量保持原定义。"""
        config = self.config(
            settings, states.device, previous_q=previous_q, previous_weight=previous_weight
        )
        config.num_cal_batch = math.ceil(len(states) / 16)
        instance = self.scope["ConformalCalculator"](model, config)
        model.eval()
        if self.case == "burgers":
            batches = iter([states[i : i + 16] for i in range(0, len(states), 16)])
            scores, weights, values = instance.get_conformal_scores(batches, q)
        else:
            batches = iter(
                [
                    (states[i : i + 16], torch.arange(i, min(i + 16, len(states))))
                    for i in range(0, len(states), 16)
                ]
            )
            scores, weights, values = instance.get_conformal_scores(batches, target, q)
        value = float(instance.calculate_quantile(scores, weights, values, settings["alpha"]))
        if not math.isfinite(value):
            raise FloatingPointError("原校准非有限")
        return value

    def sample(self, model, states, target, q, weight, *, backward=False):
        """原扩散模型直接采样，使用原安全代价产生输入梯度。"""
        if self.case == "burgers":
            config = self.config({"weight": weight}, states.device)

            def guide(x):
                with torch.enable_grad():
                    x = x.detach().requires_grad_()
                    return torch.autograd.grad(
                        self.scope["calculate_guidance"](x, q, config).sum(), x
                    )[0]

            conditions = {"u_init": states[:, 0, 0], "u_final": states[:, 0, 10]}
        else:
            kind = self.scope["GradientGuidance"]
            guide = kind.__new__(kind)
            guide.w_obj, guide.w_safe, guide.guidance_scaler = 0.0, 1.0, weight
            guide.Q, guide.safety_threshold, guide.nt, guide.state_target = q, 4.98, 122, target
            conditions = {"u_init": states[:, :3, 0], "u_final": states[:, [0, 2], :122]}
        return model.sample(
            batch_size=len(states),
            clip_denoised=True,
            device=states.device,
            guidance_u0=True,
            nablaJ=guide,
            J_scheduler=lambda t: 1.0,
            w_scheduler=lambda t: 1.0,
            enable_grad=backward,
            **conditions,
        )

    def physical(self, values):
        """原常数缩放恢复物理单位。"""
        return values * (
            self.scale.to(values.device) if isinstance(self.scale, torch.Tensor) else self.scale
        )

    def restore(self, checkpoint, cfg):
        """从明确完成权重构造原模型；共享容器不参与算法。"""
        from compare import source_model

        state = torch.load(checkpoint, map_location="cpu", weights_only=False)
        if (
            state["status"] != "complete"
            or state["contract"]["case"] != self.case
            or state["contract"]["model"] != cfg["model"]
        ):
            raise ValueError("独立参考权重不相容")
        model = source_model(case=self.case, device=cfg["train"]["device"], **cfg["model"])
        model.load_state_dict(state["model"])
        return model, state

    def arrays(self, prepared, split, n, device):
        """共享只读准备数组，控制执行不调用 Dojo 领域编排。"""
        _, values = read_arrays(prepared[split], kind="control_prepared_v1")
        return (
            torch.tensor(np.array(values["model"][:n]), device=device),
            torch.tensor(np.array(values["target"][:n]), device=device),
            values,
        )

    def worker(self, model, settings, *, adapting=False):
        """原训练步对象，替换的仅是单设备执行环境和输入注入。"""
        key = (
            ("InferenceFT" if adapting else "PostTrainPipeline")
            if self.case == "burgers"
            else "InferencePipeline"
        )
        kind = self.scope[key]
        obj = kind.__new__(kind)
        device = next(model.parameters()).device
        obj.model, obj.config, obj.step, obj.max_grad_norm = (
            model,
            self.config(settings, device),
            0,
            1.0,
        )
        obj.accelerator = SimpleNamespace(
            device=device,
            is_main_process=True,
            autocast=nullcontext,
            backward=lambda loss: loss.backward(),
            clip_grad_norm_=torch.nn.utils.clip_grad_norm_,
            wait_for_everyone=lambda: None,
        )
        if self.case == "tokamak":
            obj.device = device
        obj.optimizer = (
            torch.optim.AdamW(model.parameters(), lr=settings["lr"], weight_decay=1e-4)
            if self.case == "burgers"
            else torch.optim.Adam(model.parameters(), lr=settings["lr"], betas=(0.99, 0.999))
        )
        average = Average(model) if self.case == "burgers" else None
        scheduler = None
        if average:
            obj.ema = average.raw
            if adapting:
                scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
                    obj.optimizer, T_max=max(1, settings["adaptation_updates"]), eta_min=1e-6
                )
            else:
                warmup = max(1, int(0.05 * settings["updates_per_round"]))
                scheduler = torch.optim.lr_scheduler.SequentialLR(
                    obj.optimizer,
                    [
                        torch.optim.lr_scheduler.LambdaLR(
                            obj.optimizer, lambda step: min(1.0, step / warmup)
                        ),
                        torch.optim.lr_scheduler.CosineAnnealingLR(
                            obj.optimizer, T_max=settings["subset_size"] * 4, eta_min=1e-6
                        ),
                    ],
                    milestones=[warmup],
                )
            obj.scheduler = scheduler
        return obj, average, scheduler

    def save(
        self, session, obj, stream, history, contract, algorithm, namespace, average, scheduler
    ):
        """仅复用公开 writer 和状态容器，明确完成阶段。"""
        payload = capture_iteration(
            obj.model,
            obj.optimizer,
            updates=len(history),
            stream=stream,
            contract=contract,
            history=history,
            ema=average,
            scheduler=scheduler,
        )
        payload.update(algorithm_state=algorithm, status="complete")
        checkpoint = str(session.checkpoint("latest", payload, namespace=namespace))
        session.report(
            {
                "checkpoint": checkpoint,
                "q": algorithm["q"],
                "updates": len(history),
                "loss": history[-1],
            },
            stage=namespace,
        )
        return checkpoint

    def posttrain(self, cfg, prepared, checkpoint):
        """独立执行两轮开始校准与原加权训练步，显式保存轮次交接。"""
        from ai4e_core import run

        session = run.TrainingRun()
        settings, device = cfg["posttrain"], cfg["train"]["device"]
        q = 0.0
        for round_index in range(2):
            seed_all(cfg["seed"] + 100 + round_index)
            model, prior = self.restore(checkpoint, cfg)
            expected = "pretrain" if round_index == 0 else "posttrain"
            if prior["contract"]["phase"] != expected or prior["contract"]["prepared"] != digest(
                prepared["train"]
            ):
                raise ValueError("独立参考阶段输入不符")
            states, targets, _ = self.arrays(prepared, "train", settings["subset_size"], device)
            cal, cal_target, _ = self.arrays(
                prepared, "cal", settings["calibration_samples"], device
            )
            calibration_model = model
            if self.case == "burgers" and round_index:
                calibration_model, _ = self.restore(checkpoint, cfg)
                calibration_model.load_state_dict(
                    {
                        k.removeprefix("ema_model."): v
                        for k, v in prior["ema"].items()
                        if k.startswith("ema_model.")
                    }
                )
            q = self.calibration(calibration_model, cal, cal_target, q, settings)
            del calibration_model
            weights = self.weights(states, targets, q, settings)
            obj, average, scheduler = self.worker(model, settings)
            stream = BatchStream(
                len(states), settings["batch_size"], seed=cfg["seed"] + 100 + round_index
            )
            if round_index:
                obj.optimizer.load_state_dict(prior["optimizer"])
                stream.load_state_dict(prior["stream"])
                if scheduler:
                    scheduler.load_state_dict(prior["scheduler"])
                    average.raw.load_state_dict(prior["ema"])
            history = []
            for index in range(settings["updates_per_round"]):
                ids = stream.next()
                result = obj.finetune_step(
                    states[ids], torch.zeros_like(states[ids]), weights[ids], weights[ids]
                )
                history.append(result["loss"])
                if not math.isfinite(history[-1]):
                    raise FloatingPointError("原后训练损失非有限")
                if (index + 1) % 50 == 0:
                    logging.getLogger(__name__).info(
                        "reference posttrain_%s update=%s", round_index, index + 1
                    )
            contract = {
                "case": self.case,
                "model": cfg["model"],
                "prepared": digest(prepared["train"]),
                "phase": "posttrain",
                "round": round_index,
                "settings": settings,
            }
            checkpoint = self.save(
                session,
                obj,
                stream,
                history,
                contract,
                {"phase": "posttrain", "round": round_index, "q": q},
                f"posttrain_{round_index}",
                average,
                scheduler,
            )
        return checkpoint

    def infer(self, cfg, prepared, checkpoint):
        """独立校准、原适配训练步和原采样；响应与存储仍使用公共适配。"""
        from ai4e_contrib.ability.eval.safediffcon.control import metrics
        from ai4e_contrib.application.pde_control.safediffcon.solver import solve
        from ai4e_core import run
        from ai4e_core.applications.pde_control.infer import save_results

        session = run.TrainingRun()
        seed_all(cfg["seed"] + 200)
        settings, device = cfg["infer"], cfg["infer"]["device"]
        states, targets, arrays = self.arrays(prepared, "test", settings["test_samples"], device)
        model, prior = self.restore(checkpoint, cfg)
        if prior["contract"]["phase"] != "posttrain" or prior["algorithm_state"]["round"] != 1:
            raise ValueError("独立参考推理需要完整后训练")
        cal, cal_target, _ = self.arrays(
            prepared, "cal", cfg["posttrain"]["calibration_samples"], device
        )
        q = prior["algorithm_state"]["q"]
        q = self.calibration(
            model,
            cal,
            cal_target,
            q,
            {**settings, "alpha": cfg["posttrain"]["alpha"]},
            previous_q=q,
            previous_weight=settings["weight"]
            if self.case == "burgers"
            else cfg["posttrain"]["weight"],
        )
        effective = checkpoint
        if settings["adaptation_updates"]:
            obj, average, scheduler = self.worker(model, settings, adapting=True)
            obj.Q = q
            stream = BatchStream(len(states), len(states), seed=cfg["seed"] + 200)
            history = []
            model.train()
            for _ in range(settings["adaptation_updates"]):
                stream.next()
                prediction = self.physical(
                    self.sample(model, states, targets, q, settings["weight"], backward=True)
                )
                result = (
                    obj.finetune_step(prediction)
                    if self.case == "burgers"
                    else obj.backward_finetune_step(prediction, targets)
                )
                history.append(result["loss"])
            effective = self.save(
                session,
                obj,
                stream,
                history,
                {"case": self.case, "model": cfg["model"], "phase": "adapt", "parent": checkpoint},
                {"phase": "adapt", "q": q},
                "adapt",
                average,
                scheduler,
            )
            model = average.raw.ema_model if average else model
        model.eval()
        outputs = []
        with torch.no_grad():
            for start in range(0, len(states), settings["batch_size"]):
                stop = start + settings["batch_size"]
                outputs.append(
                    self.physical(
                        self.sample(
                            model, states[start:stop], targets[start:stop], q, settings["weight"]
                        )
                    )
                    .cpu()
                    .numpy()
                )
        output = np.concatenate(outputs)
        controls, prediction = (
            (output[:, 1, :10], output[:, 0, :11])
            if self.case == "burgers"
            else (output[:, 3:, :121].transpose(0, 2, 1), output[:, :3, :122])
        )
        target = targets.cpu().numpy()
        response = solve(target, controls, case=self.case, settings=cfg["solver"])
        paper_target = np.array(arrays["paper_target"][: len(states)])
        evaluated = metrics(response, target, case=self.case, paper_target=paper_target)
        destination = Path(cfg["data"]["output"]) / Path(session.run_dir).name / "results"
        value = save_results(
            destination,
            case=self.case,
            ids=np.arange(len(states)) + (49950 if self.case == "tokamak" else 0),
            target=target,
            paper_target=paper_target,
            controls=controls,
            prediction=prediction,
            response=response,
            checkpoint=effective,
            q=q,
            metrics=evaluated,
        )
        session.report(
            {"results": value, "metrics": evaluated, "effective_checkpoint": effective, "q": q},
            stage="infer",
        )
        return value
