"""主控复用集合计量；位置与来源须由冻结源码和真实重放证据提供。"""

import ast
import hashlib
from pathlib import Path


def trace_positions(traces, *, provided_sha256=()):
    """将真实重放转为带摘要的源码位置并去重，同时保留未覆盖路径。

    local前缀为实验实现，ai4e前缀为冻结Dojo包；其他来源不计入Dojo。
    原样给定源码按已冻结摘要排除。复制来源须另用有证据的映射登记，
    不能仅凭相似行自动认定来自Dojo。本函数核验源文件仍与追踪时一致。
    """
    local, dojo, provided, imports = set(), set(), set(), set()
    executed, sources = set(), {}
    approved = set(provided_sha256)
    for trace in traces:
        file_rows = {r["file"]: r for r in trace["files"]}
        for glue in trace.get("local_module_execution", []):
            if glue["file"] not in file_rows:
                path = Path(glue["file"])
                file_rows[str(path)] = {
                    "file": str(path),
                    "package": "local-glue",
                    "relative": str(path),
                    "sha256": glue["sha256"],
                    "function_lines": [],
                    "executed_lines": [],
                }
        for filename, row in file_rows.items():
            path = Path(filename)
            source = path.read_text()
            sha = hashlib.sha256(source.encode()).hexdigest()
            if sha != row["sha256"]:
                raise ValueError(f"追踪源码摘要变化: {filename}")
            package = row["package"]
            is_local = package.startswith("local")
            is_dojo = package.startswith("ai4e_")
            if not (is_local or is_dojo):
                continue
            # 同一内容在多个路径复制不增加代码量；来源类别仍分开。
            identity = f"{'local' if is_local else 'dojo'}:{sha}"
            body = set(row["function_lines"])
            ran = set(row["executed_lines"])
            for glue in trace.get("local_module_execution", []):
                if glue["file"] == filename:
                    body.update(glue["executed_lines"])
                    ran.update(glue["executed_lines"])
            imported = {
                line
                for node in ast.walk(ast.parse(source))
                if isinstance(node, (ast.Import, ast.ImportFrom))
                for line in range(node.lineno, node.end_lineno + 1)
            }
            positions = {f"{identity}:{n}" for n in body}
            (local if is_local else dojo).update(positions)
            imports.update(f"{identity}:{n}" for n in body & imported)
            executed.update(f"{identity}:{n}" for n in ran - imported)
            if is_local and sha in approved:
                provided.update(positions)
            sources.setdefault(identity, []).append(
                {"file": filename, "package": package, "relative": row["relative"]}
            )
    return {
        "local": local,
        "dojo": dojo,
        "provided": provided,
        "imports": imports,
        "executed_positions": executed,
        "sources": sources,
        "coverage_limits": "Only traced processes and paths; replay is not proof every original attempt was traced. Native/compiled and third-party internals excluded.",
    }


def reuse_sets(local, dojo, *, provided=(), imports=(), copied_origin=None):
    """同源复制与库调用去重；输入为已核实实际相关有效位置，而非整包行数。

    每个位置是稳定的源码身份加行号。copied_origin 只接受有来源证据的
    本地到冻结Dojo源码映射；不能把语义相似或用户新增代码映射为框架复用。
    """
    local, dojo, provided, imports = map(set, (local, dojo, provided, imports))
    mapping = copied_origin or {}
    if not set(mapping).issubset(local):
        raise ValueError("复制映射不属于候选相关实现")
    relevant = local - provided - imports
    origins = {mapping[p] for p in relevant if p in mapping}
    normalized = {mapping.get(p, p) for p in relevant}
    library = (dojo - imports) | origins
    union = normalized | library
    return {
        "local_relevant_sloc": len(local),
        "provided_excluded_sloc": len(local & provided),
        "import_excluded_sloc": len((local - provided) & imports),
        "local_implementation_sloc": len(relevant),
        "dojo_copied_retained_sloc": len(origins),
        "local_source_reuse_ratio": len(origins) / len(normalized) if normalized else None,
        "expanded_dojo_sloc": len(library),
        "expanded_implementation_sloc": len(union),
        "expanded_dojo_reuse_ratio": len(library) / len(union) if union else None,
        "copied_and_called_overlap_sloc": len(normalized & library),
        "local_canonical_positions": sorted(normalized),
        "dojo_canonical_positions": sorted(library),
        "scope": "reached effective function bodies; not every line executed or minimal standalone LOC",
    }


def responsibilities(rows):
    """职责复用保留未知上下界；适配后参与训练也算，阅读/导入不算执行。"""
    needed, known, used, unknown = 0, 0, 0, 0
    for row in rows:
        if row["needed"] is False:
            continue
        needed += 1
        availability = row["availability"]
        if availability not in {"direct", "adaptable", "unavailable", "unknown"}:
            raise ValueError("适用性枚举错误")
        if availability == "unavailable":
            continue
        if availability == "unknown" or row.get("executed") is None:
            unknown += 1
            continue
        known += 1
        if row.get("adopted") and row["executed"]:
            if not row.get("evidence"):
                raise ValueError("实际复用缺执行证据")
            used += 1
    total = known + unknown
    return {
        "needed": needed,
        "known_applicable": known,
        "adopted_executed": used,
        "unknown": unknown,
        "known_ratio": used / known if known else None,
        "lower": used / total if total else None,
        "upper": (used + unknown) / total if total else None,
    }
