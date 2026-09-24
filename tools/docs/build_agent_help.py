"""生成并校验面向 Agent 的 Dojo API 帮助索引与源码参考页。

生成过程只解析 Python AST、Markdown 元数据和案例清单，不导入 Dojo 包、
模型或训练依赖。人工教程保存在 ``docs/agent-help``；本脚本只负责可从
源码确定的签名、源码位置、公开符号覆盖和案例目录。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]
HELP_ROOT = ROOT / "docs/agent-help"
META_PATTERN = re.compile(r"^<!-- dojo-help: (\{.*\}) -->$", re.MULTILINE)
CONFIG_NAMES = {"run_root", "data_root"}


@dataclass(frozen=True)
class Scope:
    """一组需要完整建立源码参考的 Python 文件。"""

    root: Path
    package_root: Path
    import_root: str
    layer: str
    stability: str
    page_root: str


@dataclass
class Symbol:
    """从 AST 得到的一个公开符号。"""

    symbol: str
    canonical_symbol: str
    name: str
    module: str
    kind: str
    signature: str
    parameters: list[dict[str, str]]
    returns: str
    description: str
    exceptions: list[str]
    config_keys: list[str]
    layer: str
    stability: str
    source_path: str
    source_line: int
    source_end_line: int
    page: str = ""
    anchor: str = ""
    case_ids: list[str] | None = None
    recipe_ids: list[str] | None = None


SCOPES = (
    Scope(
        ROOT / "packages/ai4e-core/abilities",
        ROOT / "packages/ai4e-core",
        "ai4e_core",
        "core.ability",
        "extension",
        "api/core/abilities",
    ),
    Scope(
        ROOT / "packages/ai4e-core/applications",
        ROOT / "packages/ai4e-core",
        "ai4e_core",
        "core.application",
        "extension",
        "api/core/applications",
    ),
    Scope(
        ROOT / "packages/ai4e-contrib/ability",
        ROOT / "packages/ai4e-contrib",
        "ai4e_contrib",
        "contrib.ability",
        "extension",
        "api/contrib/abilities",
    ),
    Scope(
        ROOT / "packages/ai4e-contrib/application",
        ROOT / "packages/ai4e-contrib",
        "ai4e_contrib",
        "contrib.application",
        "extension",
        "api/contrib/applications",
    ),
    Scope(
        ROOT / "recipes",
        ROOT / "recipes",
        "recipes",
        "recipe",
        "extension",
        "recipes",
    ),
)


def _module_name(path: Path, package_root: Path, import_root: str) -> str:
    relative = path.relative_to(package_root).with_suffix("")
    parts = list(relative.parts)
    if parts and parts[-1] == "__init__":
        parts.pop()
    return ".".join([import_root, *parts])


def _format_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    result = f"{node.name}({ast.unparse(node.args)})"
    if node.returns is not None:
        result += f" -> {ast.unparse(node.returns)}"
    return result


def _parameter_rows(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[dict[str, str]]:
    args = [*node.args.posonlyargs, *node.args.args]
    defaults: list[ast.expr | None] = [None] * (len(args) - len(node.args.defaults)) + list(
        node.args.defaults
    )
    rows: list[dict[str, str]] = []
    for argument, default in zip(args, defaults, strict=True):
        if argument.arg in {"self", "cls"}:
            continue
        rows.append(
            {
                "name": argument.arg,
                "type": ast.unparse(argument.annotation) if argument.annotation else "未标注",
                "default": ast.unparse(default) if default is not None else "必填",
            }
        )
    if node.args.vararg:
        rows.append(
            {
                "name": f"*{node.args.vararg.arg}",
                "type": ast.unparse(node.args.vararg.annotation)
                if node.args.vararg.annotation
                else "未标注",
                "default": "可变位置参数",
            }
        )
    for argument, default in zip(node.args.kwonlyargs, node.args.kw_defaults, strict=True):
        rows.append(
            {
                "name": argument.arg,
                "type": ast.unparse(argument.annotation) if argument.annotation else "未标注",
                "default": ast.unparse(default) if default is not None else "必填关键字参数",
            }
        )
    if node.args.kwarg:
        rows.append(
            {
                "name": f"**{node.args.kwarg.arg}",
                "type": ast.unparse(node.args.kwarg.annotation)
                if node.args.kwarg.annotation
                else "未标注",
                "default": "可变关键字参数",
            }
        )
    return rows


def _raised_exceptions(node: ast.AST) -> list[str]:
    names: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Raise) or child.exc is None:
            continue
        value = child.exc.func if isinstance(child.exc, ast.Call) else child.exc
        if isinstance(value, ast.Name):
            names.add(value.id)
        elif isinstance(value, ast.Attribute):
            names.add(ast.unparse(value))
    return sorted(names)


def _config_keys(node: ast.AST) -> list[str]:
    keys: set[str] = set()
    for child in ast.walk(node):
        if not isinstance(child, ast.Constant) or not isinstance(child.value, str):
            continue
        value = child.value
        if value in CONFIG_NAMES or value.startswith("inputs."):
            keys.add(value)
    return sorted(keys)


def _class_signature(node: ast.ClassDef) -> tuple[str, list[dict[str, str]]]:
    init = next(
        (
            child
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            and child.name == "__init__"
        ),
        None,
    )
    if init is None:
        return f"class {node.name}", []
    signature = _format_signature(init).replace("__init__", node.name, 1)
    signature = signature.replace("(self, ", "(", 1).replace("(self)", "()", 1)
    if " -> " in signature:
        signature = signature.split(" -> ", 1)[0]
    return signature, _parameter_rows(init)


def _symbols_from_file(path: Path, scope: Scope) -> list[Symbol]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    module = _module_name(path, scope.package_root, scope.import_root)
    result: list[Symbol] = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if node.name.startswith("_"):
            continue
        if isinstance(node, ast.ClassDef):
            signature, parameters = _class_signature(node)
            returns = node.name
            kind = "class"
        else:
            signature = _format_signature(node)
            parameters = _parameter_rows(node)
            returns = ast.unparse(node.returns) if node.returns else "未标注"
            kind = "function"
        fqname = f"{module}.{node.name}"
        result.append(
            Symbol(
                symbol=fqname,
                canonical_symbol=fqname,
                name=node.name,
                module=module,
                kind=kind,
                signature=signature,
                parameters=parameters,
                returns=returns,
                description=ast.get_docstring(node) or "源码未提供 Docstring。",
                exceptions=_raised_exceptions(node),
                config_keys=_config_keys(node),
                layer=scope.layer,
                stability=scope.stability,
                source_path=str(path.relative_to(ROOT)),
                source_line=node.lineno,
                source_end_line=node.end_lineno or node.lineno,
            )
        )
        if isinstance(node, ast.ClassDef):
            for method in node.body:
                if not isinstance(method, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if method.name.startswith("_"):
                    continue
                method_name = f"{fqname}.{method.name}"
                result.append(
                    Symbol(
                        symbol=method_name,
                        canonical_symbol=method_name,
                        name=f"{node.name}.{method.name}",
                        module=module,
                        kind="method",
                        signature=_format_signature(method),
                        parameters=_parameter_rows(method),
                        returns=ast.unparse(method.returns) if method.returns else "未标注",
                        description=ast.get_docstring(method) or "源码未提供 Docstring。",
                        exceptions=_raised_exceptions(method),
                        config_keys=_config_keys(method),
                        layer=scope.layer,
                        stability=scope.stability,
                        source_path=str(path.relative_to(ROOT)),
                        source_line=method.lineno,
                        source_end_line=method.end_lineno or method.lineno,
                    )
                )
    return result


def _all_names(tree: ast.Module) -> list[str]:
    names: list[str] = []
    for node in tree.body:
        value: ast.expr | None = None
        if (
            isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
            )
            or (
                isinstance(node, ast.AugAssign)
                and isinstance(node.target, ast.Name)
                and node.target.id == "__all__"
            )
        ):
            value = node.value
        if isinstance(value, (ast.List, ast.Tuple)):
            names.extend(
                item.value
                for item in value.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            )
    return names


def _exported_symbols(
    init_path: Path,
    public_module: str,
    candidates: Iterable[Symbol],
    *,
    layer: str,
    stability: str,
    page: str,
) -> list[Symbol]:
    tree = ast.parse(init_path.read_text(encoding="utf-8"), filename=str(init_path))
    by_name: dict[str, list[Symbol]] = {}
    for candidate in candidates:
        by_name.setdefault(candidate.symbol.rsplit(".", 1)[-1], []).append(candidate)
    result: list[Symbol] = []
    for name in dict.fromkeys(_all_names(tree)):
        matches = by_name.get(name, [])
        if not matches:
            continue
        source = min(matches, key=lambda item: (item.source_path.count("/"), item.source_path))
        alias = Symbol(**asdict(source))
        alias.symbol = f"{public_module}.{name}"
        alias.canonical_symbol = source.symbol
        alias.name = name
        alias.layer = layer
        alias.stability = stability
        alias.page = page
        result.append(alias)
    return result


def _slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def _case_references(cases: list[dict[str, Any]]) -> tuple[dict[str, str], dict[str, str]]:
    case_text: dict[str, str] = {}
    recipe_by_case: dict[str, str] = {}
    for case in cases:
        path = ROOT / "examples" / case["path"]
        chunks: list[str] = []
        if path.exists():
            for file in path.rglob("*"):
                if file.is_file() and file.suffix in {".py", ".md", ".yaml"}:
                    chunks.append(file.read_text(encoding="utf-8", errors="ignore"))
        case_text[case["id"]] = "\n".join(chunks)
        if case.get("recipe_source"):
            recipe_by_case[case["id"]] = str(case["recipe_source"])
    return case_text, recipe_by_case


def _page_for_symbol(symbol: Symbol) -> str:
    relative = Path(symbol.source_path)
    if symbol.layer == "recipe":
        recipe = relative.parts[1].replace("_", "-") if len(relative.parts) > 1 else "shared"
        return f"recipes/{recipe}/api.md"
    prefix = {
        "core.ability": "api/core/abilities",
        "core.application": "api/core/applications",
        "contrib.ability": "api/contrib/abilities",
        "contrib.application": "api/contrib/applications",
    }.get(symbol.layer)
    if prefix:
        scoped = relative.parts[3:]
        expected_root = {
            "core.ability": "abilities",
            "core.application": "applications",
            "contrib.ability": "ability",
            "contrib.application": "application",
        }[symbol.layer]
        if scoped and scoped[0] == expected_root:
            scoped = scoped[1:]
        path = Path(*scoped).with_suffix(".md")
        if path.name == "__init__.md":
            path = path.with_name("index.md")
        return f"{prefix}/{path.as_posix()}"
    return symbol.page


def _parameter_table(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "本符号没有公开构造参数，或源码未声明可提取的参数。"
    lines = ["| 参数 | 类型 | 默认值 |", "| --- | --- | --- |"]
    lines.extend(f"| `{row['name']}` | `{row['type']}` | `{row['default']}` |" for row in rows)
    return "\n".join(lines)


def _reference_entry(symbol: Symbol) -> str:
    exceptions = ", ".join(f"`{name}`" for name in symbol.exceptions)
    if not exceptions:
        exceptions = "AST 未发现显式 `raise`；依赖函数仍可能报告输入、文件或运行错误。"
    config = ", ".join(f"`{key}`" for key in symbol.config_keys)
    if not config:
        config = "源码没有直接读取公共配置键；配置通常由调用它的 application 或 recipe 传入。"
    cases = (
        ", ".join(f"`{case}`" for case in symbol.case_ids or []) or "机器索引未发现直接文本引用。"
    )
    recipes = (
        ", ".join(f"`{recipe}`" for recipe in symbol.recipe_ids or []) or "无直接 recipe 归属。"
    )
    if symbol.kind == "method":
        owner, method = symbol.name.split(".", 1)
        example = (
            "```python\n"
            "from inspect import signature\n"
            f"from {symbol.module} import {owner}\n\n"
            f"print(signature({owner}.{method}))\n"
            "```"
        )
    else:
        example = (
            "```python\n"
            "from inspect import signature\n"
            f"from {symbol.module} import {symbol.name}\n\n"
            f"print(signature({symbol.name}))\n"
            "```"
        )
    return f"""<a id=\"{symbol.anchor}\"></a>
## `{symbol.symbol}`

- **层级**：`{symbol.layer}`
- **稳定性**：`{symbol.stability}`
- **定义**：`{symbol.signature}`
- **规范定义名**：`{symbol.canonical_symbol}`

### 用途

{symbol.description}

### 导入与签名

```python
from {symbol.module} import {symbol.name.split(".")[0]}
```

```text
{symbol.signature}
```

### 参数

{_parameter_table(symbol.parameters)}

参数的物理单位、实体身份和路径相对基准只有在源码 Docstring 或所选案例明确声明时才成立；不能仅根据参数名推断。

### 返回值

源码返回标注：`{symbol.returns}`。普通 Python 返回值由调用方直接交接；跨阶段文件必须通过案例的 `inputs.<stage>.<name>` 或登记产物交接。

### 异常

{exceptions}

### 副作用与产物

本索引不根据函数名猜测写盘、设备、随机状态或检查点副作用。调用前应阅读下面的源码位置和引用它的完整案例；写运行记录时只能通过公开 run/Task 边界。

### 配置键

{config}

### 最小可执行检查

{example}

这段代码只验证当前解释器中的符号和签名。真实调用请按能力教程提供有效输入；需要完整领域交接时再阅读关联案例或工作流。

### Recipe 与案例

- Recipe：{recipes}
- 案例：{cases}

### 源码位置

- 模块：`{symbol.module}`
- 仓库相对路径：`{symbol.source_path}:{symbol.source_line}`
- 安装源码：先调用 `ai4e_task.source_location({symbol.module.split(".")[0]!r})`，再按模块相对路径定位。

### 相关 API

通过 `search_help({symbol.module!r})` 查询同模块符号，通过案例 ID 查询完整阶段连接。

### 不适用场景与证据边界

API 可导入或最小检查通过只证明符号存在，不证明组件兼容、训练有效、恢复一致或达到论文精度。`internal-visible` 符号不构成兼容承诺。
"""


def _api_pages(symbols: list[Symbol]) -> dict[str, str]:
    grouped: dict[str, list[Symbol]] = {}
    for symbol in symbols:
        symbol.page = _page_for_symbol(symbol)
        symbol.anchor = f"symbol-{_slug(symbol.symbol)}"
        grouped.setdefault(symbol.page, []).append(symbol)
    pages: dict[str, str] = {}
    for path, records in grouped.items():
        records.sort(key=lambda item: item.symbol)
        metadata = {
            "topic_id": f"module:{records[0].module}",
            "kind": "api" if records[0].layer != "recipe" else "recipe",
            "layer": records[0].layer,
            "domain": records[0].module,
            "title": records[0].module,
            "summary": f"{records[0].module} 的完整源码参考与公开符号索引。",
        }
        header = (
            f"<!-- dojo-help: {json.dumps(metadata, ensure_ascii=False, sort_keys=True)} -->\n"
            f"# `{records[0].module}` API 参考\n\n"
            "> 本页由 AST 生成，签名和源码位置来自当前工作树。用途语义优先使用源码 Docstring，"
            "完整研究调用请继续阅读关联工作流和案例。\n\n"
        )
        pages[path] = header + "\n".join(_reference_entry(record) for record in records)
    return pages


def _case_readme(case: dict[str, Any], page: str, cases: list[dict[str, Any]]) -> str:
    """内嵌真实案例正文；转换可导出链接，显式标出未交付的历史参考。"""
    source = ROOT / "examples" / case["path"] / "README.md"
    original = source.read_bytes()
    targets = {
        (ROOT / "examples" / item["path"] / "README.md").resolve(): HELP_ROOT
        / f"examples/cases/{item['id'].replace('.', '/')}.md"
        for item in cases
    }

    def link(match):
        marker, label, raw = match.groups()
        raw = raw.strip().removeprefix("<").removesuffix(">")
        if raw.startswith(("https://", "http://", "mailto:", "#")):
            return match.group(0)
        path, separator, anchor = raw.partition("#")
        resolved = (source.parent / unquote(path)).resolve()
        target = targets.get(resolved)
        if target is None and resolved.is_relative_to(HELP_ROOT.resolve()) and resolved.is_file():
            target = resolved
        if target is not None:
            relative = Path(os.path.relpath(target, (HELP_ROOT / page).parent)).as_posix()
            # README标题加深但文字不变，Markdown标题锚点仍保持。
            return f"{marker}[{label}](<{relative}{separator + anchor if separator else ''}>)"
        return f"{label}（原参考 `{raw}` 未随此帮助交付；实际阶段源码请在复制案例内阅读）"

    text = re.sub(r"(!?)\[([^\]\n]+)\]\((<[^>]+>|[^)\n]+)\)", link, original.decode("utf-8"))
    text = re.sub(
        r"^(#{1,6}) ", lambda m: "#" * min(6, len(m[1]) + 2) + " ", text, flags=re.MULTILINE
    )
    return f"来源：案例 README；SHA256 `{hashlib.sha256(original).hexdigest()}`。\n\n{text}"


def _case_pages(cases: list[dict[str, Any]]) -> dict[str, str]:
    pages: dict[str, str] = {}
    for case in cases:
        case_id = case["id"]
        path = f"examples/cases/{case_id.replace('.', '/')}.md"
        metadata = {
            "topic_id": f"case:{case_id}",
            "kind": "case",
            "layer": "example",
            "domain": case_id.split(".", 1)[0],
            "title": case_id,
            "summary": case.get("research", {}).get(
                "summary", case.get("purpose", "Dojo 研究案例")
            ),
            "tasks": [
                *case.get("research", {}).get("data_form", []),
                *case.get("research", {}).get("extension_points", []),
            ],
            "case_ids": [case_id],
        }
        lines = [
            f"<!-- dojo-help: {json.dumps(metadata, ensure_ascii=False, sort_keys=True)} -->",
            f"# `{case_id}`",
            "",
            f"- 类型：`{case['type']}`",
            f"- 用途：{case.get('purpose', '未声明')}",
            f"- 资源路径：`examples/{case['path']}`",
        ]
        research = case.get("research", {})
        if research:
            lines.extend(
                [
                    "",
                    research["summary"],
                    "",
                    f"- 数据形态：{', '.join(research['data_form'])}",
                    f"- 训练机制：{', '.join(research['training_pattern'])}",
                    f"- 替换入口：{', '.join(research['extension_points'])}",
                    *[f"- 限制：{value}" for value in research["limitations"]],
                ]
            )
        if case["type"] == "standalone":
            lines.extend(
                [
                    f"- 模型：`{case.get('model', '未声明')}`",
                    f"- 数据集：`{case.get('dataset', '未声明')}`",
                    f"- 入口：`{case.get('entry', 'pipeline.py')}`",
                    f"- Recipe 来源：`{case.get('recipe_source', '未声明')}`",
                    f"- 依赖：{', '.join(f'`{item}`' for item in case.get('dependencies', [])) or '无额外声明'}",
                    "",
                    "## 阶段",
                    "",
                    *[f"- `{stage}`" for stage in case.get("stages", [])],
                    "",
                    "## 使用流程",
                    "",
                    "1. 用 `check_example` 检查资源，再用 `copy_example` 复制到仓库外空目录。",
                    "2. 阅读复制目录的 README、config、pipeline 和全部阶段脚本。",
                    "3. 先直接执行 pipeline；需要版本、后台运行或恢复时再把同一目录交给 Task。",
                    "4. 按 README 读回配置、阶段摘要、检查点、预测、指标和 post 结果。",
                    "",
                    "目录和文件存在不代表运行成功；当前真实输入、预算和证据边界以案例 README 为准。",
                ]
            )
        else:
            lines.extend(
                [
                    f"- 基案例：`{case.get('base_case', '未声明')}`",
                    "- 覆盖文件：",
                    *[f"  - `{item}`" for item in case.get("override_files", [])],
                    "",
                    "## 物化流程",
                    "",
                    "`copy_example` 会先复制完整基案例，再叠加声明的覆盖文件并写 provenance。",
                    "物化后必须重新检查配置、输入和恢复兼容性；不能直接运行原 extension 目录。",
                ]
            )
        lines.extend(["", "## 案例详细说明", "", _case_readme(case, path, cases)])
        if case["type"] == "extension":
            base = next(item for item in cases if item["id"] == case["base_case"])
            base_path = f"examples/cases/{base['id'].replace('.', '/')}.md"
            relative = Path(os.path.relpath(base_path, Path(path).parent)).as_posix()
            lines.extend(["", f"基案例完整说明：[本地正文]({relative})。", ""])
        pages[path] = "\n".join(lines).rstrip() + "\n"
    return pages


def _topic_from_text(path: str, content: str) -> dict[str, Any] | None:
    match = META_PATTERN.search(content)
    if not match:
        return None
    value = json.loads(match.group(1))
    value["path"] = path
    value.setdefault("anchor", "")
    value.setdefault("symbols", [])
    value.setdefault("tasks", [])
    value.setdefault("inputs", [])
    value.setdefault("outputs", [])
    value.setdefault("artifacts", [])
    value.setdefault("errors", [])
    value.setdefault("case_ids", [])
    value.setdefault("recipe_ids", [])
    value.setdefault("stability", "stable")
    return value


def _manual_topics(generated_paths: set[str]) -> list[dict[str, Any]]:
    topics: list[dict[str, Any]] = []
    if not HELP_ROOT.exists():
        return topics
    for path in HELP_ROOT.rglob("*.md"):
        relative = path.relative_to(HELP_ROOT).as_posix()
        if relative in generated_paths:
            continue
        topic = _topic_from_text(relative, path.read_text(encoding="utf-8"))
        if topic:
            topics.append(topic)
    return topics


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def navigation_outputs() -> dict[str, str]:
    """从能力教程元数据生成三个入口的直达菜单，避免独立维护能力清单。"""
    pages = []
    for path in sorted((HELP_ROOT / "capabilities").glob("*.md")):
        topic = _topic_from_text(path.relative_to(HELP_ROOT).as_posix(), path.read_text())
        if topic is None or "navigation_order" not in topic or not topic["symbols"]:
            raise ValueError(f"能力教程缺少导航顺序或 API: {path}")
        pages.append(topic)
    if not pages or len({p["navigation_order"] for p in pages}) != len(pages):
        raise ValueError("能力菜单为空或导航顺序重复")
    pages.sort(key=lambda item: item["navigation_order"])
    start, end = "<!-- capability-menu:start -->", "<!-- capability-menu:end -->"
    targets = {
        "DOJO_AGENT_GUIDE.md": "docs/agent-help/",
        ".agents/skills/dojo-research/SKILL.md": "../../../docs/agent-help/",
        "docs/agent-help/index.md": "",
    }
    outputs = {}
    for name, prefix in targets.items():
        content = (ROOT / name).read_text(encoding="utf-8")
        if content.count(start) != 1 or content.count(end) != 1:
            raise ValueError(f"能力菜单标记缺失或重复: {name}")
        menu = "\n".join(
            f"- **[{p['title']}]({prefix}{p['path']})**：{p['summary']}。主题 `{p['topic_id']}`。"
            for p in pages
        )
        before, rest = content.split(start)
        _, after = rest.split(end)
        outputs[name] = before + start + "\n" + menu + "\n" + end + after
    return outputs


def build_outputs() -> dict[str, str]:
    """返回所有可重建文件，调用方决定写入或只比较。"""
    all_symbols: list[Symbol] = []
    for scope in SCOPES:
        for path in sorted(scope.root.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            all_symbols.extend(_symbols_from_file(path, scope))

    run_scope = Scope(
        ROOT / "packages/ai4e-core/run",
        ROOT / "packages/ai4e-core",
        "ai4e_core",
        "core.run.internal",
        "internal-visible",
        "api/core",
    )
    run_candidates = [
        symbol
        for path in sorted(run_scope.root.rglob("*.py"))
        for symbol in _symbols_from_file(path, run_scope)
    ]
    run_exports = _exported_symbols(
        run_scope.root / "__init__.py",
        "ai4e_core.run",
        run_candidates,
        layer="core.run",
        stability="stable",
        page="api/core/run-reference.md",
    )

    task_scope = Scope(
        ROOT / "packages/ai4e-task",
        ROOT / "packages/ai4e-task",
        "ai4e_task",
        "task.internal",
        "internal-visible",
        "api/task",
    )
    task_candidates = [
        symbol
        for path in sorted(task_scope.root.rglob("*.py"))
        if ".hatch-resources" not in path.parts
        for symbol in _symbols_from_file(path, task_scope)
    ]
    task_exports = _exported_symbols(
        task_scope.root / "__init__.py",
        "ai4e_task",
        task_candidates,
        layer="task",
        stability="stable",
        page="api/task/public-api.md",
    )
    all_symbols.extend(run_exports)
    all_symbols.extend(task_exports)

    manifest = json.loads((ROOT / "examples/case-manifest.json").read_text(encoding="utf-8"))
    cases = manifest["cases"]
    case_text, recipe_by_case = _case_references(cases)
    for symbol in all_symbols:
        short = symbol.symbol.rsplit(".", 1)[-1]
        symbol.case_ids = sorted(
            case_id
            for case_id, text in case_text.items()
            if re.search(rf"\b{re.escape(short)}\b", text)
        )
        if symbol.layer == "recipe":
            relative_recipe = Path(symbol.source_path).relative_to("recipes").as_posix()
            matches = [
                source
                for source in recipe_by_case.values()
                if relative_recipe.startswith(source.rstrip("/") + "/")
            ]
            recipe = max(matches, key=len) if matches else Path(relative_recipe).parts[0]
            symbol.recipe_ids = [recipe]
            symbol.case_ids = sorted(
                case_id for case_id, source in recipe_by_case.items() if source == recipe
            )
        else:
            symbol.recipe_ids = sorted(
                {recipe_by_case[case] for case in symbol.case_ids if case in recipe_by_case}
            )

    docs = _api_pages(all_symbols)
    docs.update(_case_pages(cases))
    symbol_records = sorted(
        (asdict(symbol) for symbol in all_symbols), key=lambda item: item["symbol"]
    )

    topics = _manual_topics(set(docs))
    for path, content in docs.items():
        topic = _topic_from_text(path, content)
        if topic:
            topics.append(topic)
    for record in symbol_records:
        topics.append(
            {
                "topic_id": f"api:{record['symbol']}",
                "kind": "api" if record["layer"] != "recipe" else "recipe",
                "layer": record["layer"],
                "domain": record["module"],
                "title": record["symbol"],
                "summary": record["description"].splitlines()[0],
                "path": record["page"],
                "anchor": record["anchor"],
                "symbols": [record["symbol"], record["canonical_symbol"]],
                "tasks": [],
                "inputs": record["config_keys"],
                "outputs": [record["returns"]],
                "artifacts": [],
                "errors": record["exceptions"],
                "case_ids": record["case_ids"],
                "recipe_ids": record["recipe_ids"],
                "stability": record["stability"],
                "source_module": record["module"],
                "source_path": record["source_path"],
                "source_line": record["source_line"],
            }
        )
    unique_topics = {topic["topic_id"]: topic for topic in topics}
    ordered_topics = [unique_topics[key] for key in sorted(unique_topics)]

    outputs = dict(docs)
    outputs["indexes/topics.json"] = _json(ordered_topics)
    outputs["indexes/cases.json"] = _json(cases)
    outputs["indexes/symbols.jsonl"] = "".join(
        json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n" for record in symbol_records
    )
    outputs["indexes/source-map.jsonl"] = "".join(
        json.dumps(
            {
                "symbol": record["symbol"],
                "canonical_symbol": record["canonical_symbol"],
                "module": record["module"],
                "source_path": record["source_path"],
                "source_line": record["source_line"],
                "source_end_line": record["source_end_line"],
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n"
        for record in symbol_records
    )
    outputs["manifest.json"] = _json(
        {
            "schema_version": 1,
            "help_contract_version": 1,
            "default_entry": "index.md",
            "indexes": {
                "topics": "indexes/topics.json",
                "symbols": "indexes/symbols.jsonl",
                "cases": "indexes/cases.json",
                "source_map": "indexes/source-map.jsonl",
            },
            "coverage": {
                "symbols": len(symbol_records),
                "topics": len(ordered_topics),
                "cases": len(cases),
            },
        }
    )
    return outputs


def write_outputs(outputs: dict[str, str], root: Path = HELP_ROOT) -> None:
    """原子写入生成文件。"""
    root.mkdir(parents=True, exist_ok=True)
    for relative, content in outputs.items():
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(target.suffix + ".tmp")
        temporary.write_text(content, encoding="utf-8")
        temporary.replace(target)


def check_outputs(outputs: dict[str, str]) -> list[str]:
    """比较生成结果，返回缺失或漂移的相对路径。"""
    failures: list[str] = []
    for relative, content in outputs.items():
        target = HELP_ROOT / relative
        if not target.is_file() or target.read_text(encoding="utf-8") != content:
            failures.append(relative)
    return failures


def main() -> None:
    """生成或校验 Agent 帮助中心。"""
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()
    navigation = navigation_outputs()
    if args.write:
        write_outputs(navigation, ROOT)
    outputs = build_outputs()
    if args.write:
        write_outputs(outputs)
        print(f"wrote {len(outputs)} generated help files")
        return
    failures = check_outputs(outputs)
    failures.extend(
        name
        for name, content in navigation.items()
        if (ROOT / name).read_text(encoding="utf-8") != content
    )
    if failures:
        raise SystemExit("agent help files are stale:\n" + "\n".join(failures))
    print(f"checked {len(outputs)} generated help files")


if __name__ == "__main__":
    main()
