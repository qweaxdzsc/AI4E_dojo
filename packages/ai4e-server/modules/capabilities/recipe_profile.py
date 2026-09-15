"""页面映射的代码兼容门禁；格式与已核验的历史配置入口不改变处理语义。"""

import ast
import hashlib
import json

# 仅放行这一对经过配置/真实处理验收的入口，不把任意旧脚本当作兼容。
# 新入口增加 manifest 默认展开；旧入口多一个未使用的 load 导入。
# 源码夹具：tests/fixtures/rawprep_legacy/configuration.py。
CONFIGURATION_COMPATIBILITY = {
    # 与b82基线逐行核对：只新增rawprep.workers配置透传，推理与训练加载语义不变。
    "7dd4c23842d37671793e39a610c71bcd3969ad2a2b4e1f5ac09291b39bf7dd89": {
        "b82bd73c6f0ab6c3a81741a909f29f11961f034d5d1c485f310f95c2ac00c5c7",
        "62d5131ab27bba644c246e0428a19a93b898d4363da9a363e1e4052a718dacff",
        "8b80397195ba2f07ac33ed4b53af0a248c0ea9b426d4088658a25095a28508e8",
        "d4a8e8165fe31cdf1120ec5fe68383a133c45c1bdc3dd75947ac20b69b51dfce",
    },
    # 当前原生infer加载器的已审查旧配置入口：原处理参数及加载语义保持，
    # 新infer阶段仍由其实际加载器能力校验，不能据此执行未知脚本。
    "b82bd73c6f0ab6c3a81741a909f29f11961f034d5d1c485f310f95c2ac00c5c7": {
        "62d5131ab27bba644c246e0428a19a93b898d4363da9a363e1e4052a718dacff",
        "8b80397195ba2f07ac33ed4b53af0a248c0ea9b426d4088658a25095a28508e8",
        "d4a8e8165fe31cdf1120ec5fe68383a133c45c1bdc3dd75947ac20b69b51dfce",
    },
    "62d5131ab27bba644c246e0428a19a93b898d4363da9a363e1e4052a718dacff": {
        "8b80397195ba2f07ac33ed4b53af0a248c0ea9b426d4088658a25095a28508e8",
        "d4a8e8165fe31cdf1120ec5fe68383a133c45c1bdc3dd75947ac20b69b51dfce",
    },
    "8b80397195ba2f07ac33ed4b53af0a248c0ea9b426d4088658a25095a28508e8": {
        "d4a8e8165fe31cdf1120ec5fe68383a133c45c1bdc3dd75947ac20b69b51dfce",
    },
}


def python_signature(content: bytes) -> str:
    """忽略注释、空白和行号，保留调用顺序、常量、导入和文档字符串。"""
    tree = ast.dump(ast.parse(content), include_attributes=False)
    return hashlib.sha256(tree.encode()).hexdigest()


def compatible_file(name: str, expected: bytes, actual: bytes) -> bool:
    """识别同义语法及已审定旧入口；语法错误、未知逻辑或入口差异拒绝。"""
    if expected == actual:
        return True
    try:
        if name == "task-entry.json":
            return json.loads(expected) == json.loads(actual)
        current, candidate = python_signature(expected), python_signature(actual)
        return current == candidate or (
            name == "configuration.py"
            and candidate in CONFIGURATION_COMPATIBILITY.get(current, set())
        )
    except (SyntaxError, ValueError, UnicodeError):
        return False


def compatible_legacy(folder, actual: set[str], registry, case_id=None, components=None) -> bool:
    """核对受信模板附带的迁移前完整 AST，不读取任务自带的兼容白名单。"""
    from copy import deepcopy

    if not registry.is_file():
        return False
    profiles = json.loads(registry.read_text())["profiles"]
    key = "examples/aero_cfd/" + case_id if case_id else "recipes/aero_cfd"
    if key not in profiles:
        return False
    expected = deepcopy(profiles[key])
    entry = deepcopy(profiles["recipes/aero_cfd"]["task-entry.json"])
    if case_id:
        entry["platform_case"] = case_id
        entry["components"] = components
        if case_id.startswith("nasa_crm_"):
            for name in ("train_h5", "test_h5", "connectivity_h5"):
                entry["inputs"]["dataset." + name] = "dataset"
    expected["task-entry.json"] = entry
    if set(expected) != actual:
        return False
    try:
        for name, signature in expected.items():
            content = (folder / name).read_bytes()
            if name == "task-entry.json":
                if json.loads(content) != signature:
                    return False
            else:
                found = python_signature(content)
                allowed = {signature}
                if name == "configuration.py":
                    allowed |= CONFIGURATION_COMPATIBILITY.get(signature, set())
                if found not in allowed:
                    return False
    except (SyntaxError, ValueError, UnicodeError, OSError):
        return False
    return True


def compatible_native(folder, actual, registry, case_id=None, components=None) -> bool:
    """核验实施前保存的原生 infer 完整模板，未知改动不放行。"""
    if not registry.is_file():
        return False
    try:
        profiles = json.loads(registry.read_text())["profiles"]
        key = "examples/aero_cfd/" + case_id if case_id else "recipes/aero_cfd"
        profile = profiles[key]
        expected = {name: value for name, value in profile.items() if name.endswith(".py")}
        entry = json.loads(profiles["recipes/aero_cfd"]["task-entry.json"]["content"])
        if case_id:
            entry.update(platform_case=case_id, components=components)
            if case_id.startswith("nasa_crm_"):
                for name in ("train_h5", "test_h5", "connectivity_h5"):
                    entry["inputs"]["dataset." + name] = "dataset"
        if actual != {*expected, "task-entry.json"}:
            return False
        if json.loads((folder / "task-entry.json").read_text()) != entry:
            return False
        return all(python_signature((folder / name).read_bytes()) == value["ast"] for name, value in expected.items())
    except (KeyError, ValueError, SyntaxError, OSError):
        return False
