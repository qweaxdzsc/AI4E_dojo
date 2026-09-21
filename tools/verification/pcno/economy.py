"""原作者固定预测的独立经济回放，仅替换文件路径。"""

import argparse
import ast
import json
from pathlib import Path

from tools.verification.pcno.reference import digest


def replay(source: Path, data: Path, output: Path, expected: Path):
    """执行原经济脚本，并要求输出与附带 CSV 逐字节一致。"""
    output.mkdir(parents=True, exist_ok=False)
    tree = ast.parse(source.read_text())

    class Paths(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str):
                for prefix, target in [("/data", data.resolve()), ("/results", output.resolve())]:
                    if node.value == prefix or node.value.startswith(prefix + "/"):
                        return ast.copy_location(
                            ast.Constant(str(target) + node.value[len(prefix) :]), node
                        )
            return node

    tree = ast.fix_missing_locations(Paths().visit(tree))
    (output / "adapted-economy.py").write_text(ast.unparse(tree) + "\n")
    exec(compile(tree, str(source), "exec"), {"__name__": "__main__"})  # noqa: S102 — 本地作者基线回放。
    actual = output / "Tech_Eco_Result_75_0.85.csv"
    equal = actual.read_bytes() == expected.read_bytes()
    result = {
        "source_sha256": digest(source),
        "expected_sha256": digest(expected),
        "actual_sha256": digest(actual),
        "byte_equal": equal,
        "scope": "author stored predictions only; no training or prediction accuracy claim",
    }
    (output / "comparison.json").write_text(json.dumps(result, indent=2))
    if not equal:
        raise ValueError("Economic CSV differs from the author result")
    return result


def main():
    """明确指定原脚本、输入、输出和预期结果。"""
    parser = argparse.ArgumentParser(description=__doc__)
    for key in ["source", "data", "output", "expected"]:
        parser.add_argument("--" + key, type=Path, required=True)
    args = parser.parse_args()
    replay(args.source, args.data, args.output, args.expected)


if __name__ == "__main__":
    main()
