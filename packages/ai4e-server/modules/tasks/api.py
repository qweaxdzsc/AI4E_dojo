"""任务创建、派生和管理只调用公开 task 门面。"""

import ai4e_task as task
from fastapi import APIRouter, Request
from pydantic import BaseModel, ConfigDict

from ...bootstrap.dependencies import services
from ..stages import stage_summary

router = APIRouter(prefix="/projects/{project}/tasks")


class TaskEdit(BaseModel):
    """任务管理编辑请求。"""

    model_config = ConfigDict(extra="forbid")
    name: str | None = None
    description: str | None = None
    archived: bool | None = None


class TaskCreate(TaskEdit):
    """从登记案例和受控数据根创建，浏览器不能指定 Python 组件。"""

    case_id: str | None = None
    data_root: str | None = None
    data_path: str = ""
    data_sources: dict[str, dict] = {}


class DatasetEdit(BaseModel):
    """修订保护的数据来源；可按公开数据集副本一次接入处理方式。"""

    model_config = ConfigDict(extra="forbid")
    expected_revision: str
    sources: dict[str, dict] | None = None
    dataset_id: str | None = None
    instance_id: str | None = None


def _source_files(service, project, sources):
    from ...infrastructure.content_access import resolve
    from ..visualization.application import asset

    paths = {}
    for key, ref in sources.items():
        if key not in {"train_h5", "test_h5", "connectivity_h5"}:
            raise ValueError("unsupported_dataset_source: " + key)
        if "asset_id" in ref:
            path = asset(service, project, ref)
        else:
            if set(ref) != {"root", "path"} or not ref["root"].startswith("data"):
                raise ValueError("controlled_dataset_source_required: " + key)
            path = resolve(service, project, ref["root"], ref["path"])
        if not path.is_file():
            raise ValueError("dataset_source_file_missing: " + key)
        paths[key] = str(path)
    return paths


@router.put("/{identity}/dataset")
def update_dataset(project: str, identity: str, body: DatasetEdit, request: Request):
    """解析受控文件后通过 task 保存 dataset，不接受任意绝对路径。"""
    from .dataset import save_binding

    return save_binding(
        services(request),
        project,
        identity,
        body.sources,
        body.expected_revision,
        body.dataset_id,
        body.instance_id,
    )


@router.get("/{identity}/dataset")
def dataset(project: str, identity: str, request: Request):
    """读取当前数据绑定及可定位的失效状态。"""
    from .dataset import read_binding

    return read_binding(services(request), project, identity)


@router.get("/{identity}/datasets")
def public_datasets(project: str, identity: str, request: Request):
    """列出 contrib 公开数据集、处理说明和本机完整副本。"""
    from .dataset import list_public_datasets

    return list_public_datasets(services(request), project, identity)


from ..capabilities import CASES


@router.get("/cases")
def cases(project: str, request: Request):
    """列出服务模板旁登记的正式案例，不接受任意脚本路径。"""
    s = services(request)
    s.project(project)
    root = s.settings.template.parent.parent / "examples/aero_cfd"
    return [
        {"id": key, **item} for key, item in CASES.items() if (root / key / "config.yaml").is_file()
    ]


@router.get("")
def listing(project: str, request: Request):
    """查询当前范围内的真实管理记录。"""
    base = services(request).project(project)
    return [
        {**value, "stage_summary": stage_summary(project, value["id"], services(request))["stages"]}
        for value in task.list_tasks(base)
    ]


@router.post("")
def create(project: str, body: TaskCreate, request: Request):
    """通过任务公开门面创建研究对象。"""
    s = services(request)
    if not body.name or not body.name.strip():
        raise ValueError("task_name_required")
    if task.open_project(s.project(project)).get("archived"):
        raise ValueError("project_archived")
    configuration = None
    if body.case_id:
        if body.case_id not in CASES:
            raise ValueError("unknown_registered_case")
        from omegaconf import OmegaConf

        path = (
            s.settings.template.parent.parent / "examples/aero_cfd" / body.case_id / "config.yaml"
        )
        configuration = OmegaConf.to_container(OmegaConf.load(path), resolve=False)
    if body.data_root:
        from ...infrastructure.content_access import resolve

        if not body.data_root.startswith("data"):
            raise ValueError("registered_data_root_required")
        root = resolve(s, project, body.data_root, body.data_path)
        if not root.is_dir():
            raise ValueError("dataset_directory_required")
        if configuration is None:
            from omegaconf import OmegaConf

            configuration = OmegaConf.to_container(
                OmegaConf.load(s.settings.template / "config.yaml"), resolve=False
            )
        configuration.setdefault("inputs", {}).setdefault("rawprep", {})["source"] = str(root)
    if body.data_sources:
        if configuration is None:
            from omegaconf import OmegaConf

            configuration = OmegaConf.to_container(
                OmegaConf.load(s.settings.template / "config.yaml"), resolve=False
            )
        configuration.setdefault("inputs", {}).setdefault("rawprep", {}).update(_source_files(s, project, body.data_sources))
    declared = CASES.get(body.case_id or "")
    if declared and declared["binding_mode"] == "files" and (body.data_root or body.data_sources):
        from pathlib import Path

        from omegaconf import OmegaConf

        from .dataset import NASA_KEYS

        resolved = OmegaConf.to_container(OmegaConf.create(configuration), resolve=True)
        for key in NASA_KEYS:
            if not Path(resolved["inputs"]["rawprep"].get(key, "")).is_file():
                raise ValueError("dataset_source_file_missing: " + key)
    if body.case_id and not body.data_root and not body.data_sources:
        # 新建任务只选择案例；模板开发路径不能成为用户的默认数据来源。
        configuration.setdefault("inputs", {}).setdefault("rawprep", {})["source"] = None
        configuration.setdefault("inputs", {}).setdefault("trainprep", {})["dataset"] = None
        if declared and declared["binding_mode"] == "files":
            from .dataset import NASA_KEYS

            for key in NASA_KEYS:
                configuration["inputs"]["rawprep"][key] = None
    source = s.settings.template
    if body.case_id:
        from .templates import register_case_template

        source = register_case_template(s, project, body.case_id)
    value = task.new_task(s.project(project), body.name, source=source, configuration=configuration)
    if body.description:
        value = task.update_task(s.project(project), value["id"], description=body.description)
    return value


@router.get("/{identity}")
def detail(project: str, identity: str, request: Request):
    """读取已有对象详情，不创建新运行。"""
    value = task.get_task(services(request).project(project), identity)
    value["stage_summary"] = stage_summary(project, identity, services(request))["stages"]
    value.pop("directory", None)
    return value


@router.patch("/{identity}")
def update(project: str, identity: str, body: TaskEdit, request: Request):
    """更新研究对象管理属性，保留版本身份。"""
    return task.update_task(
        services(request).project(project), identity, **body.model_dump(exclude_none=True)
    )


@router.post("/{identity}/fork")
def fork(project: str, identity: str, body: TaskEdit, request: Request):
    """通过任务公开门面派生新的研究任务。"""
    base = services(request).project(project)
    if task.get_task(base, identity).get("archived") or task.open_project(base).get("archived"):
        raise ValueError("archived")
    return task.fork_task(base, identity, name=body.name)
