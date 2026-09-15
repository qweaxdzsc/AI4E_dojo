import json
import importlib.util
import subprocess
import sys
from pathlib import Path


def test_portable_bundle_plan_excludes_machine_specific_dependencies():
    backend = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/create_portable_bundle.py", "--check-only"],
        cwd=backend,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["forbidden"] == []
    assert payload["source_and_business_data_mib"] < 300


def test_maintenance_defaults_to_a_non_destructive_plan():
    backend = Path(__file__).resolve().parents[1]
    result = subprocess.run(
        [sys.executable, "scripts/maintenance.py"],
        cwd=backend,
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["applied"] is False
    assert "resources/examples" in payload["preserved"]


def test_frontend_lock_is_complete_for_clean_cross_platform_npm_install():
    root = Path(__file__).resolve().parents[2]
    package = json.loads((root / "frontend" / "package.json").read_text(encoding="utf-8"))
    lock = json.loads((root / "frontend" / "package-lock.json").read_text(encoding="utf-8"))

    locked_root = lock["packages"][""]
    assert locked_root["dependencies"] == package["dependencies"]
    assert locked_root["devDependencies"] == package["devDependencies"]

    # Vitest 4 resolves its own Vite 8, whose optional esbuild peer must be
    # represented completely in a portable lock. Older npm 11 releases reject
    # `npm ci` when the esbuild package exists without all platform packages.
    nested_prefix = "node_modules/vitest/node_modules/"
    esbuild = lock["packages"][f"{nested_prefix}esbuild"]
    assert esbuild["version"] == "0.28.2"
    assert len(esbuild["optionalDependencies"]) >= 20
    for name, version in esbuild["optionalDependencies"].items():
        platform = lock["packages"][f"{nested_prefix}{name}"]
        assert platform["version"] == version
        assert platform["optional"] is True
        assert platform["integrity"].startswith("sha512-")


def test_launcher_rejects_legacy_api_health(monkeypatch):
    """启动器不得把仍连接旧 ``backend/state`` 的 api_app 误判为当前API。"""

    root = Path(__file__).resolve().parents[2]
    spec = importlib.util.spec_from_file_location("ai4e_run_project", root / "run_project.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    api = next(service for service in module.SERVICES if service.name == "api")

    monkeypatch.setattr(module, "_http_json", lambda _url: {"ok": True, "artifacts": 0})
    assert module._compatible_running_service(api) is False
    monkeypatch.setattr(
        module, "_http_json",
        lambda _url: {"entrypoint": "server.api", "runtime_layout": "var-v1"},
    )
    assert module._compatible_running_service(api) is True
