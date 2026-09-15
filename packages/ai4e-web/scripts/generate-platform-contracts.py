"""从稳定 Python 契约生成浏览器类型；无需导入服务或数值运行时。"""

import importlib.util
import json
import types
from pathlib import Path
from typing import Any, Literal, NotRequired, get_args, get_origin, is_typeddict

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "packages/ai4e-spec/artifacts/platform.py"
TARGET = ROOT / "packages/ai4e-web/src/infrastructure/contracts/platform.generated.ts"


def render_type(value):
    """将契约使用的轻量类型转换为 TypeScript。"""
    origin, args = get_origin(value), get_args(value)
    if origin is NotRequired:
        return render_type(args[0])
    if origin is Literal:
        return " | ".join(json.dumps(x) for x in args)
    if origin is types.UnionType:
        return " | ".join(render_type(x) for x in args)
    if origin is list:
        return f"Array<{render_type(args[0])}>"
    if origin is dict:
        return f"Record<string, {render_type(args[1])}>"
    if is_typeddict(value):
        return value.__name__
    return {
        str: "string",
        int: "number",
        float: "number",
        bool: "boolean",
        type(None): "null",
        Any: "unknown",
    }[value]


def generate():
    """按 Python 字段定义生成稳定且可重复的类型文件。"""
    spec = importlib.util.spec_from_file_location("platform_contract", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    lines = ["/** 自动生成自 ai4e-spec/artifacts/platform.py；请勿手改。 */"]
    extra_spec = importlib.util.spec_from_file_location("visualization_contract", SOURCE.with_name("visualization.py"))
    extra = importlib.util.module_from_spec(extra_spec)
    extra_spec.loader.exec_module(extra)
    values = {**vars(module), **{name: value for name, value in vars(extra).items() if is_typeddict(value) and name != "VisualizationStorageScope"}}
    inference_spec = importlib.util.spec_from_file_location("inference_contract", SOURCE.with_name("inference.py"))
    inference = importlib.util.module_from_spec(inference_spec)
    inference_spec.loader.exec_module(inference)
    values.update({name: value for name, value in vars(inference).items() if is_typeddict(value)})
    for name, value in values.items():
        if not is_typeddict(value):
            continue
        lines.append(f"export interface {name} {{")
        for key, annotation in value.__annotations__.items():
            suffix = "?" if key in value.__optional_keys__ else ""
            lines.append(f"  {key}{suffix}: {render_type(annotation)};")
        lines.append("}\n")
    return "\n".join(lines)


if __name__ == "__main__":
    TARGET.write_text(generate(), encoding="utf-8")
