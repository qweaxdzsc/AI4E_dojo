"""平台跨项目登记：只汇聚 Task 已发布资源，不执行或发布物理数据。"""

import hashlib
import json
from pathlib import Path
from uuid import uuid4

import ai4e_task as task


def synchronize(service) -> list[dict]:
    """按来源项目与共享身份同步平台目录，并兼容旧任务路径登记。"""
    workspace = Path(service.settings.root)
    current = []
    projects = workspace / "projects"
    for project in sorted(projects.iterdir()) if projects.is_dir() else []:
        if not (project / "project.json").is_file():
            continue
        info = json.loads((project / "project.json").read_text())
        for item in task.list_shared_datasets(project):
            source = item.get("source", {})
            key = hashlib.sha256(f"{info['id']}:{item['id']}".encode()).hexdigest()[:32]
            record = {
                "registry_id": "ds_" + key,
                "name": item["name"],
                "manifest_path": item["manifest_path"],
                "digest": item.get("manifest_digest"),
                "status": item["status"],
                "reason": item.get("reason"),
                "created_at": item.get("updated_at", item["created_at"]),
                "source_project": info["id"],
                "source_project_name": info.get("name", info["id"]),
                "shared_asset_id": item["id"],
                "claim": {},
                "provenance": {
                    "project": str(project.resolve()),
                    "task_id": source.get("task_id"),
                    "run_id": source.get("run_id"),
                },
            }
            if item.get("migration"):
                record["migration"] = item["migration"]
            path = workspace / "datasets" / record["registry_id"] / "dataset.json"
            encoded = json.dumps(record, ensure_ascii=False, indent=2)
            if not path.is_file() or path.read_text() != encoded:
                path.parent.mkdir(parents=True, exist_ok=True)
                temporary = path.with_name("." + uuid4().hex + ".tmp")
                try:
                    temporary.write_text(encoded)
                    temporary.replace(path)
                finally:
                    temporary.unlink(missing_ok=True)
            current.append(record)
    by_source = {item.get("migration", {}).get("source_manifest") for item in current}
    paths = {item["manifest_path"] for item in current}
    for legacy in task.list_processed_datasets(workspace):
        if legacy.get("shared_asset_id"):
            continue
        if legacy["manifest_path"] in paths or legacy["manifest_path"] in by_source:
            continue
        current.append(legacy)
    return sorted(current, key=lambda item: item.get("created_at", ""), reverse=True)
