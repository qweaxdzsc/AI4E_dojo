"""识别旧官方物理包装脚本并替换为现行模板；不解释算法参数，不创建研究版本。"""

from __future__ import annotations

import hashlib
import shutil
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from ..storage.database import transaction
from ..storage.files import write_json
from ..storage.layout import task_dir
from ..storage.records import get, put

STAGE_FILES = ("train.py", "trainprep.py", "infer.py", "post.py", "rawprep.py")
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
    return bool(expected_digest and name in STAGE_FILES and
                hashlib.sha256(text.encode()).hexdigest() == expected_digest)


def migrate_official_aero_scripts(
    project: str | Path, task_id: str, official_recipe: str | Path,
    *, expected_sources: dict[str, str] | None = None,
) -> dict:
    """显式迁移已核验的单例阶段；完整树升级使用离线迁移包。"""
    if not expected_sources:
        raise ValueError("migration_verified_sources_required")
    recipe = task_dir(project, task_id) / "recipe"
    official = Path(official_recipe)
    backup = recipe.parent / ".dojo" / "script-migrations" / uuid4().hex
    replacements = {}
    originals = {}
    replaced: list[str] = []
    task_file = recipe.parent / "task.json"
    old_task = task_file.read_bytes()
    receipt = {"expected_sources": expected_sources, "template": str(official.resolve()),
               "replaced": replaced, "status": "preparing"}
    try:
        # 与提交时的源码捕获串行，避免捕获只替换了一半的阶段。
        with transaction(project) as db:
            record = get(db, "task", task_id)
            if record.get("archived"):
                raise ValueError("task_archived")
            for name, expected in expected_sources.items():
                if name not in STAGE_FILES:
                    raise ValueError(f"migration_unknown_stage: {name}")
                target, source = recipe / name, official / name
                if not target.is_file() or not source.is_file():
                    raise FileNotFoundError(name)
                originals[name] = target.read_bytes()
                if hashlib.sha256(originals[name]).hexdigest() != expected:
                    raise ValueError(f"migration_source_changed: {name}")
                replacements[name] = source.read_bytes()
            shutil.copytree(recipe, backup / "original")
            receipt["status"] = "applying"
            write_json(backup / "receipt.json", receipt)
            for name, payload in replacements.items():
                if (recipe / name).read_bytes() != originals[name]:
                    raise ValueError(f"migration_source_changed: {name}")
                _replace_bytes(recipe / name, payload)
                replaced.append(name)
            record["updated_at"] = datetime.now(UTC).isoformat()
            put(db, "task", record, replace=True)
            write_json(task_file, record)
            receipt["status"] = "applied"
            write_json(backup / "receipt.json", receipt)
    except BaseException:
        # 只恢复本次已替换的文件；用户没有参与迁移的正文不受影响。
        for name in reversed(replaced):
            _replace_bytes(recipe / name, originals[name])
        if replaced:
            _replace_bytes(task_file, old_task)
        if (backup / "receipt.json").exists():
            receipt["status"] = "rolled_back"
            write_json(backup / "receipt.json", receipt)
        raise
    return {"replaced": replaced, "backup": str(backup)}


def _replace_bytes(path: Path, payload: bytes) -> None:
    """同级临时文件原子替换，不留下半份脚本。"""
    temp = path.with_name(f".{path.name}.{uuid4().hex}.tmp")
    try:
        temp.write_bytes(payload)
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)
