"""在隔离进程中解析应用依赖；固定代码与资源，不冻结解释器和驱动。"""

import ast
import hashlib
import importlib.util
import pkgutil
import sys
from functools import cache
from pathlib import Path
from types import SimpleNamespace

# 数值/存储运行库按被导入模块与发行版本固定，不递归冻结其整个环境。
# 用户安装的应用包不在此边界内，其内部 Python 依赖仍递归发现。
RUNTIME_PACKAGES = frozenset(
    {
        "torch",
        "numpy",
        "scipy",
        "pandas",
        "matplotlib",
        "vtk",
        "vtkmodules",
        "pyvista",
        "h5py",
        "zarr",
        "omegaconf",
        "yaml",
        "pydantic",
        "einops",
        "torch_geometric",
        "torch_scatter",
        "torch_cluster",
        "torchvista",
        "safetensors",
        "huggingface_hub",
        "timm",
        "sklearn",
        "lightgbm",
        "PIL",
        "plotly",
        "tqdm",
        "ema_pytorch",
        "fsspec",
        "numcodecs",
        "tensorboard",
        "wandb",
        "trame",
        "trame_vtk",
        "trame_vuetify",
    }
)


@cache
def _spec(name):
    """沿当前搜索顺序解析模块，不执行可选依赖的包初始化。"""
    search = sys.path
    spec = None
    for index in range(1, len(name.split(".")) + 1):
        part = ".".join(name.split(".")[:index])
        namespaces = []
        spec = None
        for directory in search:
            finder = pkgutil.get_importer(directory or str(Path.cwd()))
            candidate = finder.find_spec(part) if finder and hasattr(finder, "find_spec") else None
            if candidate is None:
                continue
            if candidate.loader is not None:
                spec = candidate
                break
            namespaces.extend(candidate.submodule_search_locations or [])
        if spec is None and namespaces:
            spec = SimpleNamespace(origin=None, submodule_search_locations=namespaces)
        if spec is None:
            return None
        search = spec.submodule_search_locations
        if index < len(name.split(".")) and search is None:
            return None
    return spec


def _location(path, recipe):
    path = Path(path).resolve()
    return {
        "local": path.is_relative_to(recipe),
        "path": str(path.relative_to(recipe)) if path.is_relative_to(recipe) else str(path),
    }


def collect_dependencies(target: str, recipe: Path) -> dict:
    """递归捕获应用静态导入及显式动态依赖；第三方包作为发行边界。"""
    recipe = recipe.resolve()
    _spec.cache_clear()
    pending = [target.rsplit(".", 1)[0]]
    modules, resources = {}, {}
    while pending:
        name = pending.pop()
        if name in modules or name.split(".")[0] in sys.stdlib_module_names:
            continue
        spec = _spec(name)
        if spec is None:
            # 可选导入的缺席也是解析身份；后来同名文件不能改变原运行。
            modules[name] = None
            continue
        locations = spec.submodule_search_locations
        paths = [_location(p, recipe) for p in locations or []]
        record = {"locations": paths, "file": None}
        modules[name] = record
        if not spec.origin or spec.origin in {"built-in", "frozen"}:
            continue
        path = Path(spec.origin).resolve()
        record["file"] = {
            **_location(path, recipe),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        parts = name.split(".")
        pending.extend(".".join(parts[:i]) for i in range(1, len(parts)))
        # 不递归第三方框架内部或整个运行环境；本地/外部用户代码及 ai4e 源码递归。
        third_party = any(p in {"site-packages", "dist-packages"} for p in path.parts)
        if path.suffix != ".py" or (third_party and name.split(".")[0] in RUNTIME_PACKAGES):
            continue
        tree = ast.parse(path.read_bytes(), filename=str(path))
        package = name if spec.submodule_search_locations is not None else name.rpartition(".")[0]
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                pending.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    base = importlib.util.resolve_name("." * node.level + base, package)
                if base:
                    pending.append(base)
                    for alias in node.names:
                        candidate = base + "." + alias.name
                        if alias.name != "*" and _spec(candidate) is not None:
                            pending.append(candidate)
            elif (
                isinstance(node, ast.Call)
                and node.args
                and (
                    isinstance(node.func, ast.Attribute)
                    and node.func.attr == "import_module"
                    or isinstance(node.func, ast.Name)
                    and node.func.id == "__import__"
                )
            ):
                argument = node.args[0]
                if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                    pending.append(importlib.util.resolve_name(argument.value, package))
        for node in tree.body:
            if not isinstance(node, ast.Assign) or not any(
                isinstance(t, ast.Name) and t.id == "SOURCE_DEPENDENCIES" for t in node.targets
            ):
                continue
            declaration = ast.literal_eval(node.value)
            if not isinstance(declaration, dict) or set(declaration) - {"modules", "files"}:
                raise ValueError("invalid_source_dependencies: " + name)
            for key in ("modules", "files"):
                if not isinstance(declaration.get(key, []), (list, tuple)) or not all(
                    isinstance(value, str) and value for value in declaration.get(key, [])
                ):
                    raise ValueError("invalid_source_dependencies: " + name)
            for dependency in declaration.get("modules", []):
                dependency = importlib.util.resolve_name(dependency, package)
                if _spec(dependency) is None:
                    raise ValueError("application_dependency_missing: " + dependency)
                pending.append(dependency)
            for resource in declaration.get("files", []):
                resolved = (path.parent / resource).resolve()
                if Path(resource).is_absolute() or not resolved.is_relative_to(path.parent):
                    raise ValueError("invalid_source_resource: " + resource)
                resources[name + ":" + resource] = {
                    **_location(resolved, recipe),
                    "sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
                }
    return {"modules": dict(sorted(modules.items())), "resources": dict(sorted(resources.items()))}
