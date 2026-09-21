"""安装资源与可复制案例门面。

本模块只读取清单、文本和文件树，不导入案例、模型或训练栈。案例运行仍由
``ai4e_core.run.launch`` 或 ``ai4e_task`` 的公开 Python API 负责。
"""

from __future__ import annotations

import importlib.util
import json
import re
import shutil
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

_REQUIRED_COMMON = ("README.md", "config.yaml", "configuration.py", "pipeline.py")


class HelpIndexError(ValueError):
    """帮助中心清单或索引损坏。"""


class HelpTopicNotFoundError(KeyError):
    """请求的帮助主题不存在。"""


class HelpSymbolNotFoundError(KeyError):
    """请求的 API 符号不存在。"""


def _source_root() -> Path:
    """返回开发树根；安装 wheel 时不会走该路径。"""
    return Path(__file__).resolve().parents[3]


def resource_root() -> Path:
    """定位 wheel 内资源或源码树中的 examples。"""
    installed = Path(__file__).resolve().parents[1] / "resources"
    if (installed / "examples/case-manifest.json").is_file():
        return installed
    root = _source_root()
    if (root / "examples/case-manifest.json").is_file():
        return root
    raise FileNotFoundError("ai4e-task 安装资源缺少 case-manifest.json")


def manifest_path() -> Path:
    """返回机器可读案例清单路径。"""
    return resource_root() / "examples" / "case-manifest.json"


def help_root() -> Path:
    """返回当前安装或源码树中的 Agent 帮助中心根目录。"""
    path = resource_root() / "docs" / "agent-help"
    if not (path / "manifest.json").is_file():
        raise FileNotFoundError("ai4e-task 安装资源缺少 docs/agent-help/manifest.json")
    return path


def _help_manifest() -> dict[str, Any]:
    """读取并校验帮助中心顶层合同。"""
    try:
        value = json.loads((help_root() / "manifest.json").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HelpIndexError("帮助中心 manifest.json 不是有效 JSON") from exc
    required = {"schema_version", "help_contract_version", "default_entry", "indexes", "coverage"}
    if set(value) != required:
        raise HelpIndexError("帮助中心 manifest.json 顶层字段不完整")
    if value["schema_version"] != 1 or value["help_contract_version"] != 1:
        raise HelpIndexError("不支持的帮助中心合同版本")
    indexes = value.get("indexes")
    if not isinstance(indexes, dict) or set(indexes) != {
        "topics",
        "symbols",
        "cases",
        "source_map",
    }:
        raise HelpIndexError("帮助中心索引声明不完整")
    return value


def _help_index_path(name: str) -> Path:
    manifest = _help_manifest()
    relative = Path(manifest["indexes"][name])
    path = (help_root() / relative).resolve()
    if not path.is_relative_to(help_root().resolve()) or not path.is_file():
        raise HelpIndexError(f"帮助索引缺失或越出资源根: {name}")
    return path


def _help_topics() -> list[dict[str, Any]]:
    try:
        value = json.loads(_help_index_path("topics").read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise HelpIndexError("topics.json 不是有效 JSON") from exc
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise HelpIndexError("topics.json 必须是主题对象列表")
    return value


def help_info() -> dict[str, Any]:
    """返回帮助中心版本、入口、索引和覆盖数量。"""
    manifest = _help_manifest()
    root = help_root()
    return {
        "root": str(root.resolve()),
        "manifest": str((root / "manifest.json").resolve()),
        "entry": str((root / manifest["default_entry"]).resolve()),
        "indexes": {
            name: str((root / relative).resolve()) for name, relative in manifest["indexes"].items()
        },
        "schema_version": manifest["schema_version"],
        "help_contract_version": manifest["help_contract_version"],
        "coverage": dict(manifest["coverage"]),
    }


def list_help_topics(
    *,
    kind: str | None = None,
    layer: str | None = None,
    domain: str | None = None,
    case_id: str | None = None,
) -> list[dict[str, Any]]:
    """按类型、层级、领域或案例列出 Agent 帮助主题。"""
    topics = _help_topics()
    for field, selected in (("kind", kind), ("layer", layer), ("domain", domain)):
        if selected is None:
            continue
        allowed = {str(topic.get(field, "")) for topic in topics}
        if selected not in allowed:
            raise ValueError(f"未知帮助过滤值 {field}={selected!r}")
    if case_id is not None:
        known_cases = {item.get("id") for item in read_case_manifest()["cases"]}
        if case_id not in known_cases:
            raise ValueError(f"未知案例过滤值: {case_id}")
    result = []
    for topic in topics:
        if kind is not None and topic.get("kind") != kind:
            continue
        if layer is not None and topic.get("layer") != layer:
            continue
        if domain is not None and topic.get("domain") != domain:
            continue
        if case_id is not None and case_id not in topic.get("case_ids", []):
            continue
        result.append(dict(topic))
    return result


def _search_terms(value: str) -> list[str]:
    """产生不依赖分词库的中英文搜索词。"""
    normalized = value.casefold().strip()
    return [item for item in re.split(r"[^\w.<>-]+", normalized) if item]


def _topic_search_text(topic: dict[str, Any]) -> str:
    fields = [
        topic.get("topic_id", ""),
        topic.get("title", ""),
        topic.get("summary", ""),
        topic.get("layer", ""),
        topic.get("domain", ""),
    ]
    for key in (
        "symbols",
        "tasks",
        "inputs",
        "outputs",
        "artifacts",
        "errors",
        "case_ids",
        "recipe_ids",
    ):
        fields.extend(str(item) for item in topic.get(key, []))
    return "\n".join(str(item) for item in fields).casefold()


def search_help(
    query: str,
    *,
    kind: str | None = None,
    layer: str | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """按符号、任务、配置、产物、错误或案例搜索帮助主题。"""
    if not isinstance(query, str) or not query.strip():
        raise ValueError("帮助查询不能为空")
    if not isinstance(limit, int) or limit < 1 or limit > 200:
        raise ValueError("limit 必须是 1 到 200 的整数")
    normalized = query.casefold().strip()
    terms = _search_terms(query)
    hits: list[dict[str, Any]] = []
    for topic in list_help_topics(kind=kind, layer=layer):
        score = 0
        symbols = [str(value).casefold() for value in topic.get("symbols", [])]
        if normalized in symbols:
            score += 10_000
        if normalized == str(topic.get("topic_id", "")).casefold():
            score += 9_000
        if normalized in [str(value).casefold() for value in topic.get("case_ids", [])]:
            score += 8_500
        if normalized in [str(value).casefold() for value in topic.get("recipe_ids", [])]:
            score += 8_000
        if normalized == str(topic.get("title", "")).casefold():
            score += 7_500
        if normalized in [str(value).casefold() for value in topic.get("tasks", [])]:
            # 明确声明的用户意图优先于大量 API 描述的偶然命中，仍低于精确符号。
            score += 3_000
        text = _topic_search_text(topic)
        if normalized in text:
            score += 1_000 + min(len(normalized), 200)
        score += sum(50 for term in terms if term in text)
        if score <= 0:
            continue
        hit = dict(topic)
        hit["score"] = score
        hits.append(hit)
    hits.sort(key=lambda item: (-item["score"], item["topic_id"]))
    return hits[:limit]


def read_help_topic(topic_id: str) -> dict[str, Any]:
    """读取一个主题的结构化元数据和 Markdown 正文。"""
    topic = next((item for item in _help_topics() if item.get("topic_id") == topic_id), None)
    if topic is None:
        raise HelpTopicNotFoundError(f"未知帮助主题: {topic_id}")
    path = (help_root() / str(topic["path"])).resolve()
    if not path.is_relative_to(help_root().resolve()) or not path.is_file():
        raise HelpIndexError(f"帮助主题路径缺失或越出资源根: {topic_id}")
    return {**topic, "content": path.read_text(encoding="utf-8")}


def _symbol_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    try:
        for line in _help_index_path("symbols").read_text(encoding="utf-8").splitlines():
            if line.strip():
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise HelpIndexError("symbols.jsonl 包含非对象记录")
                records.append(value)
    except json.JSONDecodeError as exc:
        raise HelpIndexError("symbols.jsonl 包含无效 JSON") from exc
    return records


def describe_help_symbol(symbol: str) -> dict[str, Any]:
    """按全限定名返回签名、稳定性、正文锚点和源码位置。"""
    matches = [
        record
        for record in _symbol_records()
        if symbol in {record.get("symbol"), record.get("canonical_symbol")}
    ]
    if not matches:
        raise HelpSymbolNotFoundError(f"未知 API 符号: {symbol}")
    matches.sort(key=lambda item: (item.get("symbol") != symbol, item.get("symbol", "")))
    record = dict(matches[0])
    record["topic_id"] = f"api:{record['symbol']}"
    record["installed_source"] = None
    package = str(record["module"]).split(".", 1)[0]
    try:
        location = Path(source_location(package)["path"])
        package_root = location.parent if location.suffix == ".py" else location
        source_parts = Path(record["source_path"]).parts
        if len(source_parts) >= 3 and source_parts[0] == "packages":
            candidate = package_root.joinpath(*source_parts[2:])
            if candidate.is_file():
                record["installed_source"] = str(candidate.resolve())
    except (ModuleNotFoundError, FileNotFoundError):
        pass
    return record


def export_help(target: str | Path) -> dict[str, str]:
    """把完整 Agent 帮助中心导出到目标目录的 docs/agent-help。"""
    destination = Path(target).expanduser().resolve() / "docs" / "agent-help"
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(help_root(), destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return {
        "help_root": str(destination),
        "manifest": str(destination / "manifest.json"),
        "entry": str(destination / "index.md"),
    }


def read_case_manifest() -> dict[str, Any]:
    """读取并校验清单顶层契约。"""
    value = json.loads(manifest_path().read_text(encoding="utf-8"))
    required = {"schema_version", "example_contract_version", "recipe_contract_version", "cases"}
    if set(value) != required or not isinstance(value["cases"], list):
        raise ValueError("案例清单缺少统一契约字段")
    if value["example_contract_version"] != 1 or value["recipe_contract_version"] != 1:
        raise ValueError("不支持的案例或 recipe 契约版本")
    return value


def _case_path(case: dict[str, Any]) -> Path:
    relative = Path(case["path"])
    root = resource_root() / "examples"
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("案例路径越出资源根")
    return path


def list_examples(*, case_type: str | None = None) -> list[dict[str, Any]]:
    """列出清单中的 standalone/extension，不导入案例代码。"""
    cases = read_case_manifest()["cases"]
    if case_type is not None and case_type not in {"standalone", "extension"}:
        raise ValueError("案例类型只能是 standalone 或 extension")
    return [dict(case) for case in cases if case_type is None or case["type"] == case_type]


def _find_case(case_id: str) -> dict[str, Any]:
    for case in list_examples():
        if case.get("id") == case_id:
            return case
    raise KeyError(f"未知案例: {case_id}")


def check_example(case_id: str) -> dict[str, Any]:
    """检查案例文件、路径污染和 extension 引用，不执行或导入案例。"""
    case = _find_case(case_id)
    errors: list[str] = []
    path = _case_path(case)
    if case["type"] == "standalone":
        for name in [*_REQUIRED_COMMON, *case.get("required_files", [])]:
            if not (path / name).is_file():
                errors.append(f"缺少文件: {name}")
    else:
        try:
            base = _find_case(case["base_case"])
            if base["type"] != "standalone":
                errors.append("base_case 必须指向 standalone")
        except KeyError:
            errors.append(f"缺少基案例: {case['base_case']}")
        for name in case.get("override_files", []):
            if not (path / name).is_file():
                errors.append(f"缺少覆盖文件: {name}")
    forbidden = (".context", "recipes", "/Users/", "/private/tmp/")
    for file in path.rglob("*"):
        if file.is_file() and file.suffix not in {".pyc"}:
            text = file.read_text(encoding="utf-8", errors="ignore")
            for marker in forbidden:
                if marker in text:
                    errors.append(f"路径污染 {marker}: {file.relative_to(path)}")
    return {
        "id": case_id,
        "type": case["type"],
        "path": str(path),
        "ok": not errors,
        "errors": errors,
    }


def _copy_tree(source: Path, target: Path) -> None:
    """复制普通文件树，拒绝符号链接和目录穿越。"""
    for item in source.rglob("*"):
        relative = item.relative_to(source)
        if (
            any(part in {".context", "__pycache__"} for part in relative.parts)
            or item.suffix == ".pyc"
        ):
            continue
        destination = target / relative
        if item.is_symlink():
            raise ValueError(f"案例不允许符号链接: {relative}")
        if item.is_dir():
            destination.mkdir(parents=True, exist_ok=True)
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, destination)


def copy_example(case_id: str, target: str | Path) -> dict[str, Any]:
    """复制 standalone，或物化 extension 的 base-plus-overlay 目录。"""
    case = _find_case(case_id)
    destination = Path(target).expanduser().resolve()
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"目标目录必须为空: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    if case["type"] == "standalone":
        _copy_tree(_case_path(case), destination)
        provenance = {
            "type": "standalone",
            "case_id": case_id,
            "base_case": None,
            "override_files": [],
        }
    else:
        base = _find_case(case["base_case"])
        _copy_tree(_case_path(base), destination)
        overlay_root = _case_path(case)
        declared = set(case.get("override_files", []))
        actual = {
            str(file.relative_to(overlay_root))
            for file in overlay_root.rglob("*")
            if file.is_file() and file.name != "README.md" and "__pycache__" not in file.parts
        }
        undeclared = actual - declared
        if undeclared:
            raise ValueError(f"extension 存在未声明覆盖文件: {sorted(undeclared)}")
        for name in declared:
            source = overlay_root / name
            destination_file = destination / name
            if source.is_dir():
                _copy_tree(source, destination_file)
            else:
                destination_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination_file)
        provenance = {
            "type": "extension",
            "case_id": case_id,
            "base_case": case["base_case"],
            "override_files": list(case.get("override_files", [])),
        }
    (destination / ".dojo-provenance.json").write_text(
        json.dumps(provenance, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return {**provenance, "target": str(destination)}


def export_guide(target: str | Path) -> dict[str, str]:
    """导出 guide 和唯一 skill 源的构建副本，不创建 AGENTS.md。"""
    target_path = Path(target).expanduser().resolve()
    target_path.mkdir(parents=True, exist_ok=True)
    root = resource_root()
    guide = root / "DOJO_AGENT_GUIDE.md"
    skill = root / ".agents/skills/dojo-research/SKILL.md"
    if not guide.is_file() or not skill.is_file():
        raise FileNotFoundError("安装资源缺少 guide 或 dojo-research skill")
    (target_path / "DOJO_AGENT_GUIDE.md").write_bytes(guide.read_bytes())
    skill_target = target_path / ".agents/skills/dojo-research/SKILL.md"
    skill_target.parent.mkdir(parents=True, exist_ok=True)
    skill_target.write_bytes(skill.read_bytes())
    help_export = export_help(target_path)
    return {
        "guide": str(target_path / "DOJO_AGENT_GUIDE.md"),
        "skill": str(skill_target),
        **help_export,
    }


def guide_info() -> dict[str, Any]:
    """返回当前解释器、版本和实际安装资源位置，不加载训练栈。"""
    root = resource_root()
    try:
        task_version = version("ai4e-task")
    except PackageNotFoundError:
        task_version = "source"
    help_details = help_info()
    return {
        "python": sys.executable,
        "dojo_version": task_version,
        "guide": str((root / "DOJO_AGENT_GUIDE.md").resolve()),
        "skill": str((root / ".agents/skills/dojo-research/SKILL.md").resolve()),
        "manifest": str(manifest_path().resolve()),
        "examples": str((root / "examples").resolve()),
        "help_root": help_details["root"],
        "help_manifest": help_details["manifest"],
        "help_entry": help_details["entry"],
        "source": source_location("ai4e_task")["path"],
    }


def source_location(module: str) -> dict[str, str]:
    """定位当前解释器实际可见的模块源码，不导入模块。"""
    spec = importlib.util.find_spec(module)
    if spec is None:
        raise ModuleNotFoundError(module)
    origin = spec.origin or ""
    location = (
        origin if origin not in {"", "built-in"} else (spec.submodule_search_locations or [""])[0]
    )
    return {
        "module": module,
        "path": str(Path(location).resolve()),
        "loader": type(spec.loader).__name__ if spec.loader else "unknown",
    }


def create_smoke_data(target: str | Path) -> dict[str, Any]:
    """显式加载 contrib，生成 Neumann 最小数据；目标非空时拒绝覆盖。"""
    try:
        from ai4e_contrib.application.datasets.parametric import generate_dataset
    except ModuleNotFoundError as exc:  # pragma: no cover - depends on optional install
        raise RuntimeError("smoke-data 需要安装 ai4e-contrib 的 PDE 数据生成能力") from exc

    output = Path(target).expanduser().resolve()
    manifest = generate_dataset(
        "neumann_diffusion",
        {"train": 2, "test": 1, "nx": 7, "nt": 7, "seed": 42, "output": str(output)},
    )
    return {
        "case": "neumann_diffusion",
        "manifest": manifest,
        "train": 2,
        "test": 1,
        "nx": 7,
        "nt": 7,
        "device": "cpu",
    }
