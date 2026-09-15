"""模块化目录和依赖方向的自动架构门禁。

测试只读取源码，不连接真实运行数据库，也不要求启动FastAPI、Trame或前端服务。
"""

from __future__ import annotations

import ast
import re
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_ROOT = BACKEND_ROOT.parent
MODULES_ROOT = BACKEND_ROOT / "modules"
MODULE_NAMES = {
    "dataAssets", "visTaskManage", "visGeometry", "visDatasets", "visPhysField",
    "visFigure", "visIO", "visConvertor", "automation", "MCP",
    "reportManage", "reportDesigner", "visEngine",
}


def _python_files(root: Path) -> list[Path]:
    """返回目录下所有非缓存Python源码。"""

    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


def _source(path: Path) -> str:
    """以UTF-8读取源码，便于依赖和注释门禁复用。"""

    return path.read_text(encoding="utf-8")


def test_thirteen_backend_modules_exist() -> None:
    """十三级一级限界上下文必须全部存在且可作为Python包导入。"""

    actual = {path.name for path in MODULES_ROOT.iterdir() if path.is_dir() and (path / "__init__.py").exists()}
    assert MODULE_NAMES <= actual


def test_data_assets_owns_asset_persistence_boundary() -> None:
    """资产表只能属于dataAssets，visDatasets不得恢复Repository。"""

    assert (MODULES_ROOT / "dataAssets" / "repository.py").exists()
    assert not (MODULES_ROOT / "visDatasets" / "repository.py").exists()
    repository_source = _source(MODULES_ROOT / "dataAssets" / "repository.py")
    assert "CREATE TABLE IF NOT EXISTS artifacts" in repository_source
    assert "artifact_classification_history" in repository_source


def test_phys_field_second_level_modules_share_first_level_base() -> None:
    """物理场二级业务不得复制一级Router、Repository和服务入口。"""

    second_level_root = MODULES_ROOT / "visPhysField" / "modules"
    assert {path.name for path in second_level_root.iterdir() if path.is_dir()} >= {
        "fieldVisualization", "dataExtraction", "dataOverview",
    }
    forbidden_names = {"api.py", "application.py", "repository.py", "module.py", "server.py", "trame.py"}
    violations = [str(path.relative_to(MODULES_ROOT)) for path in second_level_root.rglob("*.py") if path.name in forbidden_names]
    assert violations == []


def test_phys_field_does_not_restore_generic_top_level_names() -> None:
    """禁止用纯技术或泛化名称替代物理场二级业务模块。"""

    root = MODULES_ROOT / "visPhysField"
    assert not any((root / name).exists() for name in ("interaction", "extraction", "overview"))


def test_engine_contains_only_kernel_dependencies() -> None:
    """visEngine不得依赖HTTP、Server、Trame、SQLite或其他业务模块。"""

    violations: list[str] = []
    for path in _python_files(MODULES_ROOT / "visEngine"):
        source = _source(path)
        tree = ast.parse(source, filename=str(path))
        imported_roots: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_roots.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_roots.add(node.module)
        forbidden_imports = ("fastapi", "trame", "sqlite", "server", "modules.")
        has_forbidden_import = any(
            imported == token or imported.startswith(f"{token}.") or imported.startswith(token)
            for imported in imported_roots
            for token in forbidden_imports
        )
        # 内核中出现HTTP地址通常意味着业务服务配置误入，应作为独立门禁处理。
        if has_forbidden_import or "http://" in source or "https://" in source:
            violations.append(str(path.relative_to(MODULES_ROOT)))
    assert violations == []


def test_module_routers_do_not_execute_sql() -> None:
    """一级模块api.py只能做HTTP适配，不能执行SQL或直接连接SQLite。"""

    forbidden_tokens = ("sqlite3", ".execute(", ".executemany(", "select ", "insert ", "update ", "delete ")
    violations: list[str] = []
    for path in MODULES_ROOT.glob("*/api.py"):
        lowered = _source(path).lower()
        if any(token in lowered for token in forbidden_tokens):
            violations.append(str(path.relative_to(MODULES_ROOT)))
    assert violations == []


def test_public_python_functions_have_chinese_docstrings() -> None:
    """新增模块的公开函数必须有包含中文说明的Docstring。"""

    violations: list[str] = []
    for path in _python_files(MODULES_ROOT):
        tree = ast.parse(_source(path), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) or node.name.startswith("_"):
                continue
            docstring = ast.get_docstring(node) or ""
            if not any("\u4e00" <= char <= "\u9fff" for char in docstring):
                violations.append(f"{path.relative_to(MODULES_ROOT)}:{node.lineno}:{node.name}")
    assert violations == []


def test_server_is_composition_only() -> None:
    """Server只允许装配Router和健康检查，不得恢复业务实现或SQL。"""

    source = _source(BACKEND_ROOT / "server" / "api.py")
    lowered = source.lower()
    forbidden_tokens = ("sqlite3", ".execute(", "select ", "insert ", "update ", "delete ")
    assert not any(token in lowered for token in forbidden_tokens)
    assert "include_router" in source


def test_context_index_and_project_rules_are_complete() -> None:
    """上下文索引、模块逐文件清单与前后端规则必须完整且可解析。"""

    context_root = REPOSITORY_ROOT / ".context"
    required_context = {
        "index.md", "api-registry.md", "modules/backend-architecture.md",
        "modules/frontend-architecture.md", "modules/task-data-io.md",
        "modules/geometry-figure-convertor.md", "modules/physical-field-engine.md",
        "modules/reporting.md", "modules/automation-mcp.md",
        "modules/storage-observability.md",
    }
    required_context.update(f"modules/{module_name}.md" for module_name in MODULE_NAMES)
    required_context.update({
        "modules/visPhysField/index.md",
        "modules/visPhysField/fieldVisualization.md",
        "modules/visPhysField/dataExtraction.md",
        "modules/visPhysField/dataOverview.md",
    })
    assert required_context <= {
        str(path.relative_to(context_root)) for path in context_root.rglob("*.md")
    }

    # 每个 Markdown 相对链接都必须指向现存文档或源码，防止索引随重构静默失效。
    broken_links: list[str] = []
    for document in context_root.rglob("*.md"):
        for target_text in re.findall(r"\[[^]]*\]\(([^)#]+)(?:#[^)]+)?\)", _source(document)):
            if "://" in target_text:
                continue
            if not (document.parent / target_text).resolve().exists():
                broken_links.append(f"{document.relative_to(context_root)} -> {target_text}")
    assert broken_links == []

    # 每个业务源码都必须出现在所属模块索引，避免新增文件成为不可发现的“散乱文件”。
    missing_inventory: list[str] = []
    frontend_modules = REPOSITORY_ROOT / "frontend" / "src" / "modules"
    global_index = _source(context_root / "index.md")
    for module_name in MODULE_NAMES:
        documents = [context_root / "modules" / f"{module_name}.md"]
        if module_name == "visPhysField":
            documents.extend((context_root / "modules" / "visPhysField").glob("*.md"))
        inventory = "\n".join(_source(document) for document in documents)
        prd_relative = f"docs/PRD/{module_name}.md"
        assert (REPOSITORY_ROOT / prd_relative).exists()
        assert prd_relative in global_index
        assert prd_relative in inventory
        roots = [MODULES_ROOT / module_name, frontend_modules / module_name]
        for root in roots:
            if not root.exists():
                continue
            for path in sorted(candidate for candidate in root.rglob("*") if candidate.is_file()):
                if "__pycache__" in path.parts or path.suffix not in {".py", ".js", ".jsx", ".css"}:
                    continue
                relative = path.relative_to(REPOSITORY_ROOT).as_posix()
                if relative not in inventory:
                    missing_inventory.append(relative)
    assert missing_inventory == []

    agents = _source(REPOSITORY_ROOT / "AGENTS.md")
    for required_pointer in (
        ".context/index.md", ".cursor/rules/ai4e-vis-backend.mdc",
        ".cursor/rules/ai4e-vis-frontend.mdc", "backend/requirements.txt",
        "run_project.py", "docs/PRD/", "docs/architecture/architecture.md", "error.log",
    ):
        assert required_pointer in agents
    assert (REPOSITORY_ROOT / "docs" / "PRD" / "README.md").exists()
    assert (REPOSITORY_ROOT / "docs" / "PRD" / "CHANGELOG.md").exists()
    assert (REPOSITORY_ROOT / "error.log").exists()

    rules_root = REPOSITORY_ROOT / ".cursor" / "rules"
    backend_rule = _source(rules_root / "ai4e-vis-backend.mdc")
    frontend_rule = _source(rules_root / "ai4e-vis-frontend.mdc")
    assert "globs: backend/**/*.py" in backend_rule
    assert "globs: frontend/src/**/*.{js,jsx,css}" in frontend_rule
    assert "DDD" in backend_rule and "限界上下文" in backend_rule
    assert "模块优先" in frontend_rule and "微领域驱动" in frontend_rule
    assert "Page" in frontend_rule and "聚合业务对象" in frontend_rule
    assert all(token in agents for token in (".context", "PRD", "测试用例", "error.log", "中文注释", "上下游链路"))

    architecture_plan = REPOSITORY_ROOT / "docs" / "architecture" / "architecture.md"
    assert architecture_plan.exists()
    plan_source = _source(architecture_plan)
    assert "十三级一级模块" in plan_source
    assert "dataAssets" in plan_source and "visEngine" in plan_source
    assert "后端 DDD 设计" in plan_source and "前端微领域驱动设计" in plan_source

    global_index = _source(context_root / "index.md")
    assert "后端：DDD" in global_index
    assert "前端：模块优先的微领域驱动" in global_index
    for module_name in MODULE_NAMES:
        module_context = _source(context_root / "modules" / f"{module_name}.md")
        assert "模块设计" in module_context
    assert "SPDM" not in backend_rule + frontend_rule


def test_root_readme_and_single_agents_entry_are_complete() -> None:
    """README必须覆盖当前架构，且代码子目录不得散落局部AGENTS。"""

    agents_files = sorted(REPOSITORY_ROOT.rglob("AGENTS.md"))
    assert agents_files == [REPOSITORY_ROOT / "AGENTS.md"]

    readme_path = REPOSITORY_ROOT / "README.md"
    readme = _source(readme_path)
    for required in (
        "业务主链路", "十三级业务模块", "dataAssets", "visDatasets", "visPhysField",
        "visEngine", "DDD", "微领域驱动", "var/db/ai4e_vis.sqlite3",
        ".context/index.md", "docs/PRD/README.md", "EXCEL_FEATURE_TEST_MATRIX.md",
    ):
        assert required in readme

    broken_links: list[str] = []
    for target_text in re.findall(r"\[[^]]*\]\(([^)#]+)(?:#[^)]+)?\)", readme):
        if "://" in target_text:
            continue
        if not (readme_path.parent / target_text).resolve().exists():
            broken_links.append(target_text)
    assert broken_links == []
