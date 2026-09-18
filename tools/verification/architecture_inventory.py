"""生成全仓源码、文档和测试清单；结构关联不冒充功能验收结果。"""

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXCLUDED = {"node_modules", "__pycache__", "dist", "test-results", "playwright-report"}


def declarations(tree: ast.AST, prefix: str = "") -> list[dict]:
    """记录模块入口及类方法的位置/签名，不复制函数正文或推断语义。"""
    result = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = prefix + node.name
            signature = (
                f"{node.name}({ast.unparse(node.args)})"
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                else f"class {node.name}"
            )
            if getattr(node, "returns", None) is not None:
                signature += f" -> {ast.unparse(node.returns)}"
            result.append(
                {
                    "name": name,
                    "line": node.lineno,
                    "end_line": node.end_lineno,
                    "signature": signature,
                    "description": ast.get_docstring(node) or "",
                }
            )
            if isinstance(node, ast.ClassDef):
                result.extend(declarations(node, name + "."))
    return result


def inventory(root: Path = ROOT) -> dict:
    """记录正式文件内容和模块关系，供人工沿调用链核对和最终复跑比对。"""
    listing = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=root,
        capture_output=True,
        check=True,
    )
    files = []
    for name in sorted(set(listing.stdout.decode().split("\0")) - {""}):
        path = root / name
        if (
            not path.is_file()
            or set(path.parts) & EXCLUDED
            or any(part.startswith("test-results") for part in path.parts)
        ):
            continue
        if name not in {
            "AGENTS.md",
            "README.md",
            "pyproject.toml",
            ".context/index.md",
        } and not name.startswith(
            (
                "packages/",
                "recipes/",
                "examples/",
                "tools/",
                "tests/",
                "docs/",
                ".context/modules/",
                ".context/tasks/",
                ".agents/skills/",
                ".cursor/rules/",
            )
        ):
            continue
        if path.suffix not in {
            ".py",
            ".ts",
            ".tsx",
            ".js",
            ".jsx",
            ".cjs",
            ".mjs",
            ".md",
            ".mdc",
            ".yaml",
            ".toml",
            ".json",
            ".css",
            ".html",
            ".sql",
            ".sh",
        }:
            continue
        source = path.read_text(encoding="utf-8")
        record = {"path": name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        record["role"] = (
            "test"
            if "/tests/" in name or name.startswith("tests/") or "/e2e/" in name
            else "document"
            if path.suffix in {".md", ".mdc"}
            else "configuration"
            if path.suffix in {".yaml", ".toml", ".json"}
            else "source"
        )
        if path.suffix == ".py":
            tree = ast.parse(source, filename=name)
            record["description"] = ast.get_docstring(tree) or ""
            record["declarations"] = [
                n.name
                for n in tree.body
                if isinstance(n, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            record["declaration_details"] = declarations(tree)
            record["imports"] = sorted(
                {n.module for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module}
                | {
                    alias.name
                    for n in ast.walk(tree)
                    if isinstance(n, ast.Import)
                    for alias in n.names
                }
            )
        files.append(record)
    packages = []
    for package in sorted((root / "packages").iterdir()):
        if not package.is_dir() or not package.name.startswith("ai4e-"):
            continue
        modules = sorted(
            p.name
            for p in package.iterdir()
            if p.is_dir()
            and not p.name.startswith(".")
            and p.name not in EXCLUDED
            and not p.name.startswith("test-results")
        )
        packages.append(
            {
                "package": package.name,
                "modules": modules,
                "context": f".context/modules/{package.name}.md",
                "prds": [
                    f["path"]
                    for f in files
                    if f["role"] == "document"
                    and (
                        f["path"].startswith(f"docs/PRD/{package.name}/")
                        or f["path"].startswith(f"packages/{package.name}/docs/PRD/")
                    )
                ],
            }
        )
    return {
        "scope": "全仓正式源码、模块文档及测试；关联表示检索入口，不是通过证据",
        "packages": packages,
        "files": files,
    }


def main() -> None:
    """写出可比较清单；执行结果由验收记录单独维护。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(inventory(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
