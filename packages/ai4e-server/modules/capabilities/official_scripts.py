"""Server 官方案例脚本识别及显式迁移清单；不自动改写历史任务。"""

import hashlib
from pathlib import Path

STAGE_FILES = ("train.py", "trainprep.py", "infer.py", "post.py", "rawprep.py")


def model_switch_replacements(template, recipe, previous, selected):
    """显式换模同步当前官方科学链；用户改过的异链正文要求显式编辑。"""
    from .model_cases import current_variant, dataset_id, model_id, resolve_case

    def directory(config):
        case = resolve_case(dataset_id(config), model_id(config), current_variant(config))
        if case is None:
            raise ValueError("model_switch_registered_case_required")
        return Path(template).parent.parent / "examples/aero_cfd" / case

    old, new = directory(previous), directory(selected)
    result = {}
    for name in ("trainprep.py", "train.py", "infer.py"):
        before, after = (old / name).read_bytes(), (new / name).read_bytes()
        if before == after:
            continue
        actual = (Path(recipe) / name).read_bytes()
        if actual == after:
            continue
        if actual != before:
            raise ValueError("model_switch_requires_explicit_script_update: " + name)
        result[name] = {"source": str(new / name), "revision": hashlib.sha256(actual).hexdigest()}
    return result


OLD_IMPORTS = {
    "train.py": ("from ai4e_core.applications.aero_cfd.train import physical as fitting",),
    "trainprep.py": (
        "from ai4e_core.applications.aero_cfd.trainprep import physical as prep",
        "from ai4e_core.applications.aero_cfd.trainprep import physical as preparation",
    ),
    "infer.py": ("from ai4e_core.applications.aero_cfd import infer as infer_stage",),
    "post.py": ("from ai4e_core.applications.aero_cfd.post import physical as post_stage",),
}
OFFICIAL_DEFS = {
    "train.py": {"train", "observe_epoch"},
    "trainprep.py": {"trainprep"},
    "infer.py": {"infer"},
    "post.py": {"post"},
    "rawprep.py": {"rawprep"},
}
# 离线核验过的原官方包装摘要；不能凭导入名替换用户改过的脚本。
VERIFIED_OLD_DIGESTS = {
    "train.py": {
        "5775d4f10dfd6353cf6b6df7c6a2345c6b6760878bbc87a92bcdd639324c25e9",
        "6bb642449fa96dc35609d64fc3ad86a6c78c486afea170bbec786e51370bd3f0",
        "bd65ce30d49afb8827827019db40a076c9ec556c4a90de9e58de73bef182772c",
        "74492ae8c1c85a823aac1cc3d4381475a351a447cfd9e6e4d9fc1666fb86046b",
        "4490907c12cc8c724c1cd12050a368f413964d1809f628ba58e78fade86f2f00",
    },
    "trainprep.py": {
        "b5e0c07bcac120394937d1e3e34c5162d49e1f74d9816d84815c168aee754d1f",
        "2e32fed9ddffa4d76d16776320646f5b1ebaa6958e18d5f38c9547bf9cc1dca8",
        "e1cd282f15805be811dbe7994c6137df453558ad096910e4ce1cc2e6e4ad3344",
    },
    "infer.py": {
        "77311d93b917bc77f52ba499edd028997c5f272782c5b284719d852368d43c62",
        "8ec280823e51e938d3239f775591f4025c1a3b59f69a8500fd90fa9058b172e7",
        "8dff1efcd79f54eb0250774f62445845ea7821271d98f6d5c9719ee8abcf8a81",
    },
    "post.py": {
        "b578c52e862b27ecd4a670d34336a6fd6cbf6a4f65942ce311a9a839e7da5e71",
        "cf9ffc9245efef3455978f3373163361edda824fa8a01392e607b8225bce48d2",
        "229feb36cb17d4bfddedb9747a0dcc2752ff52eb5c3496bf424540dae8352bc0",
        "aa53c03932e0decfc754fb145433792a07b3c004cc29822333685b5e9f0e7ee4",
        "75348acd7211da68621bc4a7fa4a7c93158e939bd068aaf992591ff079774298",
    },
    "rawprep.py": {
        "57af230de2770535fcb28216043eae8a2118eef55a316745a0f0dff8d99d45e2",
        "bca6ee92bb76082a3552918bedd42ad20a2a3cc415444952455cf17c24a437f3",
    },
}


def verified_old_sources(recipe: str | Path) -> dict[str, str]:
    """只返回当前正文摘要已核验的旧官方包装；现行模板或用户改过的脚本不进入。"""
    folder = Path(recipe)
    expected = {}
    for name, known in VERIFIED_OLD_DIGESTS.items():
        path = folder / name
        if not path.is_file():
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest in known:
            expected[name] = digest
    return expected


def is_old_official_stage(text: str, name: str, *, expected_digest: str | None = None) -> bool:
    """只接受明确核验的原件摘要；导入或函数名相同不足以证明正文未修改。"""
    return bool(
        expected_digest
        and name in STAGE_FILES
        and hashlib.sha256(text.encode()).hexdigest() == expected_digest
    )


def migrate_official_aero_scripts(project, task_id, official_recipe, *, expected_sources=None):
    """将已核验官方文件清单交给 Task 事务，不由 Task 识别案例。"""
    from ai4e_task.storage.script_replacement import replace_scripts

    if not expected_sources or set(expected_sources) - set(STAGE_FILES):
        raise ValueError("migration_verified_sources_required")
    return replace_scripts(
        project,
        task_id,
        {
            name: {"source": str(Path(official_recipe) / name), "revision": revision}
            for name, revision in expected_sources.items()
        },
    )
