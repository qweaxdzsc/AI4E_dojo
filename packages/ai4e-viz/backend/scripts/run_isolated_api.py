"""Run the API with disposable SQLite and upload storage for browser tests."""

from __future__ import annotations

import argparse
import os
import shutil
import sys
import tempfile
from pathlib import Path

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=18091)
    args = parser.parse_args()

    backend_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(backend_root))
    runtime_root = Path(tempfile.mkdtemp(prefix="qoder-design2-e2e-"))
    database = runtime_root / "qoder-design2-e2e.sqlite3"
    uploads = runtime_root / "uploads"
    os.environ["QODER_ASSET_DB"] = str(database)
    os.environ["QODER_SPEC_DB"] = str(database)
    os.environ["QODER_REPORT_DB"] = str(database)
    os.environ["QODER_UPLOAD_DIR"] = str(uploads)

    try:
        from server.api import app

        uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="warning")
    finally:
        shutil.rmtree(runtime_root, ignore_errors=True)


if __name__ == "__main__":
    main()
