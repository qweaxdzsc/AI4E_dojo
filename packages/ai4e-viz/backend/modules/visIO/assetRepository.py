"""可視化资产索引的任务目录存储；不使用全局资产数据库。"""

from pathlib import Path

from infrastructure.storage.atomic import contained, identity, read_json, write_json


def scope_root(scope: dict, *, write: bool = False) -> Path:
    """只接受服务注入的明确作用域；写入核对只读状态。"""
    if not all(scope.get(key) for key in ("root", "project_id", "task_id", "scope_id")):
        raise ValueError("storage_scope_required")
    if write and not scope.get("writable", False):
        raise ValueError("storage_scope_read_only")
    root = Path(scope["root"]).expanduser().resolve()
    # 源码安装树绝不能成为运行写入目标。
    package_root = Path(__file__).resolve().parents[3]
    if root == package_root or root.is_relative_to(package_root):
        raise ValueError("storage_inside_package")
    for ancestor in package_root.parents:
        if (ancestor / ".git").exists() and root.is_relative_to(ancestor):
            raise ValueError("storage_inside_repository")
    return root


def asset_root(scope: dict, asset_id: str) -> Path:
    """取得作用域内指定资产目录。"""
    return contained(scope_root(scope), identity(asset_id))


def get_asset(scope: dict, asset_id: str) -> dict:
    """读取资产索引并核验所属项目与任务。"""
    value = read_json(contained(asset_root(scope, asset_id), "asset.json"))
    if any(value[key] != scope[key] for key in ("project_id", "task_id")):
        raise ValueError("asset_scope_mismatch")
    return value


def list_assets(scope: dict) -> list[dict]:
    """扫描已提交索引，不要求全局数据库存在。"""
    root = scope_root(scope)
    return [get_asset(scope, folder.name) for folder in sorted(root.iterdir()) if not folder.name.startswith(".") and folder.is_dir() and (folder / "asset.json").is_file()] if root.exists() else []


def commit_index(scope: dict, value: dict) -> None:
    """最后提交资产索引，配置修订可先写入但未提交前不可见。"""
    scope_root(scope, write=True)
    write_json(contained(asset_root(scope, value["visualization_id"]), "asset.json"), value)
