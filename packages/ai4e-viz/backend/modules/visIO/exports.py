"""显式输出用例；暂存完成后提交，取消与失败均不发布成功清单。"""

import multiprocessing as mp
import os
import shutil
from pathlib import Path
from threading import RLock, Thread
from uuid import uuid4

from infrastructure.process.supervisor import stop_process
from infrastructure.storage.atomic import contained

from modules.dataAssets import source_fingerprint

from .assetRepository import scope_root
from .exportRepository import export_root, get_export, put_export
from .save import read_asset


def _produce(connection, bindings, spec, options, staging):
    try:
        from modules.visPhysField import produce_output

        files = produce_output(
            bindings,
            spec,
            options,
            Path(staging),
            progress=lambda done, total: connection.send(
                {"progress": {"completed": done, "total": total}}
            ),
        )
        connection.send({"files": [p.name for p in files]})
    except Exception as exc:  # noqa: BLE001 - 进程和界面边界必须返回可见失败，不能吞掉请求。
        connection.send({"error": str(exc)})
    finally:
        connection.close()


class Exports:
    """独立输出进程可取消，不阻塞交互会话。"""

    def __init__(self):
        """维护本服务活动输出的监督信息。"""
        self.jobs = {}
        self.lock = RLock()

    def create(self, context, asset_id, revision, options):
        """从固定修订开始输出，生成摘要不会改变配置身份。"""
        scope = context["scope"]
        saved = read_asset(scope, asset_id, revision)
        export_id = uuid4().hex
        record = {
            "export_id": export_id,
            "visualization_id": asset_id,
            "revision": saved["revision"],
            "content_hash": saved["content_hash"],
            "status": "running",
            "format": options["format"],
            "files": [],
        }
        staging = contained(scope_root(scope, write=True), ".runtime/staging/" + export_id)
        staging.mkdir(parents=True)
        ctx = mp.get_context("spawn")
        parent, child = ctx.Pipe()
        process = ctx.Process(
            target=_produce,
            args=(child, context["bindings"], saved["spec"], options, str(staging)),
            daemon=True,
        )
        with self.lock:
            put_export(scope, asset_id, record)
            process.start()
            child.close()
            self.jobs[export_id] = (process, scope, asset_id, staging)

        def finish():
            """执行当前工作区的异步回调，保持所属操作的生命周期。"""
            try:
                response = parent.recv() if parent.poll(600) else {"error": "export_timeout"}
                while "progress" in response:
                    with self.lock:
                        current = get_export(scope, asset_id, export_id)
                        if current["status"] == "canceled":
                            return
                        put_export(scope, asset_id, {**current, "progress": response["progress"]})
                    response = parent.recv() if parent.poll(600) else {"error": "export_timeout"}
                with self.lock:
                    current = get_export(scope, asset_id, export_id)
                    if current["status"] == "canceled":
                        return
                    if response.get("error"):
                        raise ValueError(response["error"])
                    target = export_root(scope, asset_id, export_id)
                    files = []
                    for name in response["files"]:
                        source = contained(staging, name)
                        if not source.is_file() or source.stat().st_size == 0:
                            raise ValueError("empty_export_output")
                        files.append(
                            {
                                "name": name,
                                "sha256": source_fingerprint(source),
                                "size": source.stat().st_size,
                            }
                        )
                    for file in files:
                        os.replace(
                            contained(staging, file["name"]), contained(target, file["name"])
                        )
                    put_export(scope, asset_id, {**record, "status": "succeeded", "files": files})
            except Exception as exc:  # noqa: BLE001 - 进程和界面边界必须返回可见失败，不能吞掉请求。
                with self.lock:
                    if get_export(scope, asset_id, export_id)["status"] != "canceled":
                        target = export_root(scope, asset_id, export_id)
                        for partial in target.iterdir():
                            if partial.is_file() and partial.name != "manifest.json":
                                partial.unlink()
                        put_export(
                            scope, asset_id, {**record, "status": "failed", "error": str(exc)}
                        )
            finally:
                stop_process(process)
                parent.close()
                shutil.rmtree(staging, ignore_errors=True)
                with self.lock:
                    self.jobs.pop(export_id, None)

        Thread(target=finish, daemon=True).start()
        return record

    def cancel(self, scope, asset_id, export_id):
        """取消已提交输出，不允许迟到成功覆盖取消。"""
        with self.lock:
            record = get_export(scope, asset_id, export_id)
            if record["status"] == "running":
                record["status"] = "canceled"
                put_export(scope, asset_id, record)
                job = self.jobs.get(export_id)
                if job:
                    stop_process(job[0])
            return record

    def shutdown(self):
        """退出时取消活动导出，留下明确状态。"""
        for export_id, (_, scope, asset_id, _) in list(self.jobs.items()):
            self.cancel(scope, asset_id, export_id)


def recording(scope, asset_id, revision, content: bytes):
    """用户明确提交浏览器 WebM 录制，校验容器签名再登记。"""
    if not content.startswith(bytes.fromhex("1a45dfa3")) or len(content) < 64:
        raise ValueError("invalid_webm_recording")
    saved = read_asset(scope, asset_id, revision)
    identity = uuid4().hex
    target = export_root(scope, asset_id, identity)
    scope_root(scope, write=True)
    staging = contained(scope_root(scope, write=True), ".runtime/staging/" + identity)
    staging.mkdir(parents=True)
    path = staging / "recording.webm"
    try:
        path.write_bytes(content)
        import imageio.v2 as imageio

        with imageio.get_reader(path, format="ffmpeg") as video:
            frame = video.get_data(0)
            if frame.ndim != 3 or min(frame.shape[:2]) < 1:
                raise ValueError("invalid_webm_frame")
        record = {
            "export_id": identity,
            "visualization_id": asset_id,
            "revision": saved["revision"],
            "content_hash": saved["content_hash"],
            "status": "succeeded",
            "format": "webm",
            "files": [
                {"name": path.name, "size": path.stat().st_size, "sha256": source_fingerprint(path)}
            ],
        }
        target.mkdir(parents=True)
        os.replace(path, target / path.name)
        put_export(scope, asset_id, record)
        return record
    finally:
        shutil.rmtree(staging, ignore_errors=True)
