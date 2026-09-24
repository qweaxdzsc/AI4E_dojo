"""统计实际进入的 Dojo 实现，区分运行行和所调用函数的完整源码体积。"""

import ast
import hashlib
import inspect
import io
import json
import sys
import tokenize
from pathlib import Path


def code_lines(source):
    """有效物理代码行：排除空行、纯注释和模块/类/函数文档字符串。"""
    docs = set()
    for node in ast.walk(ast.parse(source)):
        if (
            isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.body
            and isinstance(node.body[0], ast.Expr)
        ):
            value = node.body[0].value
            if isinstance(value, ast.Constant) and isinstance(value.value, str):
                docs.update(range(node.body[0].lineno, node.body[0].end_lineno + 1))
    ignored = {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENDMARKER,
    }
    return {
        line
        for token in tokenize.generate_tokens(io.StringIO(source).readline)
        if token.type not in ignored and token.start[0] not in docs
        for line in range(token.start[0], token.end[0] + 1)
    }


class ImplementationCoverage:
    """仅跟踪指定产品包；重复调用/重叠函数/恢复过程按文件行号去重。"""

    def __init__(self, roots):
        self.roots = {name: Path(path).resolve() for name, path in roots.items()}
        self.files = {}
        self.decisions = {}

    def trace(self, frame, event, arg):
        """不追踪第三方、模块导入执行或框架外业务代码。"""
        code = frame.f_code
        if event == "call":
            filename = code.co_filename
            if filename not in self.decisions:
                path = Path(filename).resolve()
                self.decisions[filename] = (
                    next(
                        (
                            (name, str(path.relative_to(root)))
                            for name, root in self.roots.items()
                            if path.is_relative_to(root)
                        ),
                        None,
                    )
                    if path.is_file()
                    else None
                )
            location = self.decisions[filename]
            if location is None or not code.co_flags & inspect.CO_NEWLOCALS:
                return None
            item = self.files.setdefault(
                filename, {"location": location, "executed": set(), "functions": {}}
            )
            key = (code.co_qualname, code.co_firstlineno)
            executable = {n for _, _, n in code.co_lines() if n is not None}
            item["functions"][key] = (
                code.co_firstlineno,
                max(executable, default=code.co_firstlineno),
            )
            return self.trace
        if event == "line":
            self.files[code.co_filename]["executed"].add(frame.f_lineno)
        return self.trace

    def start(self):
        """当前进程开启；子进程/工作线程不自动覆盖。"""
        sys.settrace(self.trace)

    def stop(self):
        """关闭当前进程追踪，不改变模型、数据和训练策略。"""
        sys.settrace(None)

    def save(self, destination):
        """保存逐文件摘要、行号及范围；不是无框架最短重写量或性能测量。"""
        rows = []
        for filename, item in sorted(self.files.items()):
            source = Path(filename).read_text()
            effective = code_lines(source)
            spans = {n for start, end in item["functions"].values() for n in range(start, end + 1)}
            functions = [
                {"name": name, "start": start, "end": end}
                for (name, _), (start, end) in sorted(item["functions"].items())
            ]
            rows.append(
                {
                    "file": filename,
                    "package": item["location"][0],
                    "relative": item["location"][1],
                    "functions": functions,
                    "sha256": hashlib.sha256(source.encode()).hexdigest(),
                    "function_sloc": len(effective & spans),
                    "function_lines": sorted(effective & spans),
                    "executed_sloc": len(effective & item["executed"]),
                    "executed_lines": sorted(effective & item["executed"]),
                }
            )
        result = {
            "schema": "dojo-implementation-coverage-v1",
            "files": rows,
            "function_sloc": sum(r["function_sloc"] for r in rows),
            "executed_sloc": sum(r["executed_sloc"] for r in rows),
            "scope": "entered function source including unexecuted branches; module imports/constants and third-party code excluded; unique source lines, not coding time or minimal no-Dojo implementation",
        }
        Path(destination).write_text(json.dumps(result, ensure_ascii=False, indent=2))
        return result
