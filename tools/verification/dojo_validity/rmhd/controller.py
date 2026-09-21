"""主控状态机与冻结收据；隐藏评价入口只有双方最终选择锁定后可调用。"""

import shutil
from pathlib import Path

from ..io import digest, inside, inventory, read_json, write_json


def freeze_environment(source, destination, runtime):
    """复制前拒绝环境中越界链接；仅bin/python可引用白名单系统解释器。"""
    source, destination = Path(source).resolve(), Path(destination)
    allowed = [Path(p).resolve() for p in runtime]
    visited = set()

    def validate(path):
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(source):
            interpreter = path.parent == source / "bin" and path.name.startswith("python")
            if (
                not interpreter
                or not resolved.is_file()
                or not any(resolved.is_relative_to(p) for p in allowed)
            ):
                raise ValueError(f"环境链接越界: {path.relative_to(source)}")
        if path.is_dir():
            if resolved in visited:
                raise ValueError("环境目录存在循环或重复链接")
            visited.add(resolved)
            for child in path.iterdir():
                validate(child)
        elif not path.is_file():
            raise ValueError("环境含非普通文件")

    validate(source)
    shutil.copytree(source, destination, symlinks=False)
    files = inventory(destination)
    for path in destination.rglob("*"):
        if path.is_file():
            path.chmod(0o555 if path.stat().st_mode & 0o111 else 0o444)
    return files


def immutable_copy(source, destination):
    """拒绝链接，独立复制候选并只读化；不执行提交中的任何文件。"""
    source, destination = Path(source), Path(destination)
    files = inventory(source)
    if not files:
        raise ValueError("空提交")
    if any((source / name).stat().st_nlink != 1 for name in files):
        raise ValueError("候选不能包含硬链接")
    shutil.copytree(source, destination)
    if inventory(destination) != files:
        raise ValueError("复制期间提交发生变化")
    for path in destination.rglob("*"):
        path.chmod(0o555 if path.is_dir() else 0o444)
    destination.chmod(0o555)
    return files


def freeze_round(comparison, group, number, source):
    """保存完整提交到主控根；从源码与权重摘要确定身份而非目录名。"""
    if group not in {"plain", "dojo"} or type(number) is not int or number not in range(6):
        raise ValueError("组或轮次非法")
    root = Path(comparison)
    state = read_json(root / "state.json")
    if state["phase"] != "running":
        raise ValueError("当前阶段不可提交候选")
    source = Path(source)
    manifest = read_json(source / "submission.json")
    if manifest.get("round") != number or manifest.get("interface") != "rmhd-predict-v1":
        raise ValueError("提交轮次或接口不匹配")
    for key in ("entrypoint", "checkpoint", "statistics"):
        if not inside(source, manifest[key]).is_file():
            raise ValueError(f"提交缺少 {key}")
    if not manifest.get("method") or not isinstance(manifest.get("dojo_usage"), list):
        raise ValueError("提交缺少方法与实际组件使用记录")
    destination = root / "frozen" / group / f"round-{number:02d}"
    files = immutable_copy(source, destination)
    receipt = {"group": group, "round": number, "files": files, "source_manifest": manifest}
    write_json(root / "receipts" / group / f"round-{number:02d}.json", receipt)
    return receipt


def lock_final(comparison, group, selection):
    """只从已冻结候选选择，不允许最终阶段修改代码或新增第六轮。"""
    root = Path(comparison)
    if group not in {"plain", "dojo"}:
        raise ValueError("组非法")
    if read_json(root / "state.json")["phase"] != "running":
        raise ValueError("最终选择阶段已关闭")
    for number in range(6):
        verify_frozen(root, group, number)
    number = selection["round"]
    if type(number) is not int or number not in range(6):
        raise ValueError("最终选择必须来自 round-00..05")
    target = root / "final-selections" / f"{group}.json"
    if target.exists():
        raise FileExistsError("最终选择不可覆盖")
    write_json(
        target,
        selection
        | {"receipt_sha256": digest(root / "receipts" / group / f"round-{number:02d}.json")},
    )
    if all((root / "final-selections" / f"{g}.json").exists() for g in ("plain", "dojo")):
        write_json(
            root / "state.json", {"phase": "both_finals_locked", "formal_sessions_started": True}
        )


def verify_frozen(comparison, group, number):
    """每次消费重核冻结内容；只读权限之外仍必须核字节身份。"""
    root = Path(comparison)
    receipt = read_json(root / "receipts" / group / f"round-{number:02d}.json")
    source = root / "frozen" / group / f"round-{number:02d}"
    if inventory(source) != receipt["files"]:
        raise ValueError("冻结候选内容变化")
    return source


def evaluate_hidden(comparison, evaluator):
    """双最终锁定门禁不可由组协议开关覆盖；评价结果只写主控目录。"""
    root = Path(comparison)
    if read_json(root / "state.json")["phase"] not in {"both_finals_locked", "hidden_evaluating"}:
        raise ValueError("双方最终选择冻结前禁止隐藏评价")
    for group in ("plain", "dojo"):
        final = read_json(root / "final-selections" / f"{group}.json")
        if (
            digest(root / "receipts" / group / f"round-{final['round']:02d}.json")
            != final["receipt_sha256"]
        ):
            raise ValueError("最终选择收据变化")
        for number in range(6):
            verify_frozen(root, group, number)
    write_json(root / "state.json", {"phase": "hidden_evaluating", "formal_sessions_started": True})
    for group in ("plain", "dojo"):
        for number in range(6):
            output = root / "hidden-results" / group / f"round-{number:02d}"
            if (output / "result.json").exists():
                continue
            output.mkdir(parents=True, exist_ok=True)
            result = evaluator(group, number, verify_frozen(root, group, number), output)
            write_json(output / "result.json", result)
    write_json(
        root / "state.json",
        {"phase": "hidden_evaluated_accounting_pending", "formal_sessions_started": True},
    )


def run_pair(comparison, driver):
    """唯一正式调度顺序：round00和五轮均在组内，失败保留原会话等待续接。"""
    root = Path(comparison)
    state = read_json(root / "state.json")
    if state["phase"] not in {"ready", "running"}:
        raise ValueError("科学/隔离/资料/证据门槛未通过")
    config = read_json(root / "comparison-protocol.json")
    if state["phase"] == "ready":
        driver.verify_startup(config)
    write_json(root / "state.json", {"phase": "running", "formal_sessions_started": True})
    for number in range(6):
        order = ("plain", "dojo") if number % 2 == 0 else ("dojo", "plain")
        for group in order:
            if (root / "receipts" / group / f"round-{number:02d}.json").exists():
                verify_frozen(root, group, number)
                continue
            # driver 可做开发验证，但此接口根本不接收隐藏 evaluator。
            source = driver.round(group, number, config["experiments"][group])
            freeze_round(root, group, number, source)
    for group in ("plain", "dojo"):
        if not (root / "final-selections" / f"{group}.json").exists():
            selection = driver.select_final(group, config["experiments"][group])
            lock_final(root, group, selection)
