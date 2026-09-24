"""固定版本的分阶段配置与运行摘要，不将当前工作目录当创建事实。"""

from pathlib import Path

from omegaconf import OmegaConf

from ..storage.records import fetch
from ..storage.snapshots import digest, inventory
from ..tasks.query import list_runs


def read_version_details(project, version_id: str) -> dict:
    """校验创建快照，返回固定配置和带身份的各阶段实际运行。"""
    version = fetch(project, "version", version_id)
    folder = Path(project).resolve() / "tasks" / version["task_id"] / ".dojo/snapshots/creation"
    if digest(inventory(folder)) != version["snapshot"]["digest"]:
        raise ValueError("version_snapshot_changed")
    config = {}
    if (folder / "config.yaml").is_file():
        config_file = (folder / "config.yaml").resolve()
        if not config_file.is_relative_to(folder):
            raise ValueError("version_configuration_escape")
        config = OmegaConf.to_container(OmegaConf.load(config_file), resolve=False)
    runs = list_runs(project, version["task_id"])
    stages = []
    for stage in dict.fromkeys(
        [
            *config.get("pipeline", {}).get("stages", []),
            *[stage for run in runs for stage in run.get("stages", [])],
        ]
    ):
        selected = []
        for run in runs:
            if stage in (run.get("stages") or list(run.get("summary", {}).get("reports", {}))):
                selected.append(
                    {
                        "run_id": run["id"],
                        "status": run["status"],
                        "created_at": run["created_at"],
                        "operation_mode": run.get("operation_mode", "execute"),
                    }
                )
        stages.append({"stage": stage, "configuration": config.get(stage, {}), "runs": selected})
    return {
        "version_id": version_id,
        "task_id": version["task_id"],
        "source": "creation_snapshot",
        "revision": version["snapshot"]["digest"],
        "stages": stages,
    }
