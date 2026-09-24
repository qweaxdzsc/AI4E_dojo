"""架构复审来源探针：仅创建临时小模块，不改产品或环境。"""

import hashlib
import importlib
import importlib.util
import json
import pathlib
import sys
import tempfile


def main():
    root = pathlib.Path(__file__).resolve().parents[3]
    output = pathlib.Path(__file__).resolve().parent
    sys.dont_write_bytecode = True
    path = root / "packages/ai4e-task/tasks/operation_sources.py"
    spec = importlib.util.spec_from_file_location("ai4e_task.tasks.operation_sources", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    results = {
        "scope": "current source function level probe; no training or formal service",
        "source": str(path),
        "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    with tempfile.TemporaryDirectory(prefix="source-probe-", dir=output) as directory:
        base = pathlib.Path(directory)
        recipe, deps = base / "recipe", base / "dependency"
        recipe.mkdir()
        deps.mkdir()
        (recipe / "review_provider.py").write_text(
            'def infer(request):\n    import review_dependency\n'
            '    return {"value": review_dependency.value}\n'
        )
        (deps / "review_dependency.py").write_text("value = 1\n")
        sys.path[:0] = [str(recipe), str(deps)]
        captured = module._source("review_provider.infer", recipe)
        first = module.load_verified_operation(captured, recipe)({})
        (deps / "review_dependency.py").write_text("value = 2\n")
        sys.modules.pop("review_dependency", None)
        importlib.invalidate_caches()
        module.verify_source(captured, recipe)
        changed = module.load_verified_operation(captured, recipe)({})
        (recipe / "review_dependency.py").write_text("value = 3\n")
        sys.modules.pop("review_dependency", None)
        importlib.invalidate_caches()
        module.verify_source(captured, recipe)
        shadowed = module.load_verified_operation(captured, recipe)({})
        results.update(
            captured_roots=[
                {"local": r["local"], "root": r.get("root"), "file_count": len(r["files"])}
                for r in captured["roots"]
            ],
            captured_revision=captured["revision"],
            baseline=first,
            external_dependency_change={"verification": "accepted", "result": changed},
            new_local_shadow_module={"verification": "accepted", "result": shadowed},
        )
    (output / "2026-09-23-source-probe.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
