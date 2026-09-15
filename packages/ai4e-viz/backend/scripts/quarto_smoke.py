"""Create real PDF, portable HTML ZIP and connected HTML smoke artifacts."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path


def _wait_for(url: str, process: subprocess.Popen, timeout: float = 90.0) -> None:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"service exited before readiness: {process.returncode}")
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310 - controlled localhost URL
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = exc
        time.sleep(0.5)
    raise TimeoutError(f"service readiness timed out for {url}: {last_error}")


def _visualization_block(visualization: dict) -> dict:
    return {
        "id": "block-smoke-visualization",
        "type": "visualization",
        "title": "冻结 ECharts 趋势证据",
        "body": "",
        "source_ref": {
            "artifact_id": visualization["artifact_id"],
            "visualization_id": visualization["visualization_id"],
            "spec_id": visualization["spec_id"],
            "spec_version": visualization["spec_version"],
            "content_hash": visualization["content_hash"],
        },
        "layout": {
            "span": 12, "align": "stretch", "min_height": 360,
            "page_break_before": False, "keep_together": True, "hidden": False,
        },
        "display": {
            "caption": "由同一 renderer 与冻结参数生成", "alt_text": "训练损失趋势折线图", "show_source": True,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="test-results/quarto")
    args = parser.parse_args()
    backend = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend))
    output = (backend / args.output).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="qoder-quarto-smoke-") as temporary:
        root = Path(temporary)
        database = str(root / "smoke.sqlite3")
        api_port = int(os.environ.get("QODER_SMOKE_API_PORT", "8191"))
        frontend_port = int(os.environ.get("QODER_SMOKE_FRONTEND_PORT", "5375"))
        os.environ["QODER_REPORT_DB"] = database
        os.environ["QODER_ASSET_DB"] = database
        os.environ["QODER_SPEC_DB"] = database
        os.environ["QODER_FRONTEND_BASE"] = f"http://127.0.0.1:{frontend_port}"
        # CI must retain generated QMD, manifest, same-renderer captures and
        # logs long enough to publish them as job artifacts. Production does
        # not set this flag and compacts the reproducible project immediately.
        os.environ["QODER_KEEP_EXPORT_PROJECT"] = "1"
        from modules.reportManage import quarto as quarto_service
        from modules.visDatasets import build_example, recommend_artifact
        from modules.reportDesigner import replace_draft
        from modules.reportManage import create_export, create_report, freeze_report, get_export
        from modules.dataAssets import upsert_artifact
        from modules.visIO import create_visualization

        quarto_service.EXPORT_ROOT = root / "exports"
        health = quarto_service.quarto_health()
        if health["state"] != "live":
            raise SystemExit(f"Quarto health failed: {health}")
        draft = create_report({
            "title": "AI4E 中文导出冒烟报告", "author": "CircleCI",
            "audience": "工程团队", "goal": "验证 Quarto 1.10.18 的中文、分页与打包链路",
            "key_questions": ["PDF 是否可读？", "HTML 是否可离线打开？"], "template": "analysis",
            "page_size": "A4", "orientation": "portrait",
        })
        document = draft["document"]
        document["sections"][0]["rows"][0]["blocks"][0].update({
            "title": "验证结论", "body": "本段包含中文、数字 151×241 与安全 Markdown。\n\n不执行任何用户代码单元。"
        })
        series_path = root / "training_metrics.csv"
        series_path.write_text("epoch,loss\n1,0.82\n2,0.51\n3,0.34\n4,0.23\n", encoding="utf-8")
        digest = hashlib.sha256(series_path.read_bytes()).hexdigest()
        upsert_artifact({
            "artifact_id": "A-SMOKE", "name": "Quarto 冻结训练曲线", "file_name": series_path.name,
            "file_path": str(series_path), "format": "CSV", "sha256": digest,
            "size_bytes": series_path.stat().st_size, "declared_kind": "series", "detected_kind": "series",
            "family": "PLT", "source": "ci-smoke", "parse_status": "queued", "validation_status": "pending",
            "profile": None, "recommendations": None,
        })
        recommendations = recommend_artifact("A-SMOKE")
        candidate = next(
            item for item in recommendations["detected_candidates"]
            if item["kind"] == "series" and item["renderer"] == "echarts-svg"
        )
        parameters = {
            **candidate["default_parameters"], "title": "训练损失趋势",
            "line_width": 3, "show_symbols": True, "height": 420,
        }
        payload = build_example(
            "A-SMOKE", f"http://127.0.0.1:{api_port}/",
            recommendation_id=candidate["recommendation_id"], parameters=parameters,
        )
        visualization = create_visualization({
            "visualization_id": "viz-smoke-echarts", "artifact_id": "A-SMOKE",
            "recommendation_id": candidate["recommendation_id"], "spec_id": "vspec-smoke-echarts", "spec_version": 1,
            "function_id": candidate["function_id"], "renderer": candidate["renderer"],
            "parameters": parameters, "payload": payload,
            "representations": {}, "status": "live",
        })
        document["sections"][0]["rows"].append({
            "id": "row-smoke-visualization", "gap": 16, "align": "start",
            "blocks": [_visualization_block(visualization)],
        })
        replace_draft(draft["report_id"], draft["draft_revision"], document)
        version = freeze_report(draft["report_id"])
        service_env = {**os.environ, "VITE_API_BASE": f"http://127.0.0.1:{api_port}"}
        api_log = (output / "smoke-api.log").open("w", encoding="utf-8")
        frontend_log = (output / "smoke-frontend.log").open("w", encoding="utf-8")
        api_process = subprocess.Popen(
            [sys.executable, "-m", "server.api", "--port", str(api_port)], cwd=backend,
            env=service_env, stdout=api_log, stderr=subprocess.STDOUT, text=True,
        )
        frontend_process = subprocess.Popen(
            ["npm", "run", "dev", "--", "--host", "127.0.0.1", "--port", str(frontend_port)],
            cwd=backend.parent / "frontend", env=service_env, stdout=frontend_log,
            stderr=subprocess.STDOUT, text=True,
        )
        try:
            _wait_for(f"http://127.0.0.1:{api_port}/api/health", api_process)
            _wait_for(f"http://127.0.0.1:{frontend_port}/", frontend_process)
            jobs = [
                create_export(draft["report_id"], version["version"], "pdf", "static"),
                create_export(draft["report_id"], version["version"], "html", "portable"),
                create_export(draft["report_id"], version["version"], "html", "connected"),
            ]
            for job in jobs:
                quarto_service.run_export(job["export_id"])
                result = get_export(job["export_id"])
                if result["status"] != "succeeded":
                    if result.get("log_path") and Path(result["log_path"]).is_file():
                        print(Path(result["log_path"]).read_text(encoding="utf-8"), file=sys.stderr)
                    raise SystemExit(f"Export failed: {result}")
                source = Path(result["output_path"])
                shutil.copy2(source, output / source.name)
                project = quarto_service.EXPORT_ROOT / job["export_id"] / "project"
                for name in ("index.qmd", "_quarto.yml", "manifest.json"):
                    shutil.copy2(project / name, output / f"{job['export_id']}-{name}")
                static_dir = project / "assets" / "static"
                if static_dir.is_dir():
                    for static_file in static_dir.iterdir():
                        if static_file.is_file():
                            shutil.copy2(static_file, output / f"{job['export_id']}-{static_file.name}")
                if result.get("log_path"):
                    shutil.copy2(result["log_path"], output / f"{job['export_id']}-quarto.log")
        finally:
            for process in (frontend_process, api_process):
                if process.poll() is None:
                    process.terminate()
            for process in (frontend_process, api_process):
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
            api_log.close()
            frontend_log.close()
    print(output)


if __name__ == "__main__":
    main()
