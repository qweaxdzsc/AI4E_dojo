"""主控隔离重放入口：真实函数调用与本地源码一起采集，不用于延迟计时。"""

import argparse
import ast
import hashlib
import json
import runpy
import sys
from pathlib import Path

# 作为独立脚本复制到主控审计目录，与implementation_coverage.py同目录使用。
if __package__:
    from .recipe_probe.implementation_coverage import ImplementationCoverage, code_lines
else:
    from implementation_coverage import ImplementationCoverage, code_lines


class ReplayCoverage(ImplementationCoverage):
    """库仍按进入的函数体统计；本地脚本额外保存真实执行的顶层连接语句。"""

    def __init__(self, roots):
        super().__init__(roots)
        self.module_lines = {}
        self.tracked_files = {}
        self.import_only_calls = set()

    def trace(self, frame, event, arg):
        if event == "call":
            filename = frame.f_code.co_filename
            if filename not in self.tracked_files:
                path = Path(filename).resolve()
                self.tracked_files[filename] = any(
                    path.is_relative_to(root) for root in self.roots.values()
                )
            if self.tracked_files[filename]:
                parent = frame.f_back
                while parent is not None:
                    if parent.f_code.co_filename.startswith("<frozen importlib."):
                        self.import_only_calls.add(
                            (filename, frame.f_code.co_qualname, frame.f_code.co_firstlineno)
                        )
                        return None
                    parent = parent.f_back
        if frame.f_code.co_name == "<module>":
            path = Path(frame.f_code.co_filename).resolve()
            local = any(
                name.startswith("local") and path.is_relative_to(root)
                for name, root in self.roots.items()
            )
            if not local or not path.is_file():
                return None
            if event == "line":
                self.module_lines.setdefault(str(path), set()).add(frame.f_lineno)
            return self.trace
        return super().trace(frame, event, arg)

    def save(self, destination):
        result = super().save(destination)
        rows = []
        for filename, executed in sorted(self.module_lines.items()):
            source = Path(filename).read_text()
            excluded = set()
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    excluded.update(range(node.lineno, node.end_lineno + 1))
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    first = min([node.lineno, *[d.lineno for d in node.decorator_list]])
                    excluded.update(range(first, node.body[0].lineno))
                    excluded.add(node.lineno)
            lines = sorted(code_lines(source) & executed - excluded)
            rows.append(
                {
                    "file": filename,
                    "executed_lines": lines,
                    "executed_sloc": len(lines),
                    "sha256": hashlib.sha256(source.encode()).hexdigest(),
                }
            )
        result["local_module_execution"] = rows
        result["local_module_scope"] = (
            "executed top-level glue only; imports and definition statements excluded; union with function positions before counting"
        )
        result["import_context_calls_excluded"] = [
            {"file": file, "function": name, "first_line": line}
            for file, name, line in sorted(self.import_only_calls)
        ]
        result["import_context_scope"] = (
            "calls under frozen importlib frames excluded; a later scientific call to the same function is counted normally"
        )
        Path(destination).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result


def main():
    """显式指定只读源码根；网络/文件权限由外层同款Seatbelt实施。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("script", type=Path)
    parser.add_argument("arguments", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    cfg = json.loads(args.config.read_text())
    collector = ReplayCoverage(cfg["roots"])
    sys.argv = [str(args.script), *args.arguments]
    sys.path.insert(0, str(args.script.resolve().parent))
    collector.start()
    try:
        runpy.run_path(str(args.script), run_name="__main__")
    finally:
        collector.stop()
        collector.save(cfg["output"])


if __name__ == "__main__":
    main()
