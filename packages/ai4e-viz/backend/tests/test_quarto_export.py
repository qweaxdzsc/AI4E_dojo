import os
import subprocess
import sys
from pathlib import Path

import pytest


@pytest.mark.skipif(os.environ.get("RUN_QUARTO_SMOKE") != "1", reason="requires pinned Quarto runtime")
def test_quarto_pdf_portable_and_connected_exports():
    backend = Path(__file__).resolve().parents[1]
    subprocess.run(
        [sys.executable, "scripts/quarto_smoke.py", "--output", "test-results/quarto"],
        cwd=backend,
        check=True,
        timeout=360,
    )
    output = backend / "test-results" / "quarto"
    assert list(output.glob("*.pdf"))
    assert list(output.glob("*.zip"))
    assert list(output.glob("*.html"))
    assert list(output.glob("*-index.qmd"))
    assert list(output.glob("*-manifest.json"))
    assert list(output.glob("*-viz-smoke-echarts-v1.png"))
    assert any("viz-smoke-echarts" in path.read_text(encoding="utf-8") for path in output.glob("*-index.qmd"))
