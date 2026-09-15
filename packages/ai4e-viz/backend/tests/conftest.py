"""后端测试的统一运行数据隔离。

环境变量在测试模块导入前设置，确保模块级TestClient也不会接触真实数据库、上传和派生文件。
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


TEST_RUNTIME = Path(tempfile.mkdtemp(prefix="ai4e-vis-pytest-"))
TEST_DATABASE = TEST_RUNTIME / "db" / "tests.sqlite3"

os.environ.setdefault("AI4E_VIS_RUNTIME_DIR", str(TEST_RUNTIME))
os.environ.setdefault("QODER_ASSET_DB", str(TEST_DATABASE))
os.environ.setdefault("QODER_SPEC_DB", str(TEST_DATABASE))
os.environ.setdefault("QODER_REPORT_DB", str(TEST_DATABASE))
os.environ.setdefault("QODER_UPLOAD_DIR", str(TEST_RUNTIME / "uploads"))
