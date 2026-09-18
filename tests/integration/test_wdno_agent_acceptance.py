"""独立Agent产物需要真实运行证据，不能仅凭自报成功。"""

import json
import os
from pathlib import Path

import pytest

from tools.verification.wdno.agent_trials import verify_trial


def test_claim_without_execution_is_rejected(tmp_path):
    (tmp_path / "acceptance.json").write_text(json.dumps({"status": "passed"}))
    with pytest.raises(ValueError, match="初稿"):
        verify_trial(tmp_path)


def test_actual_independent_agent_outputs():
    value = os.environ.get("DOJO_WDNO_AGENT_TRIAL")
    if not value:
        pytest.skip("需要本次独立Agent实际研究目录，夹具不能代替现场验收")
    result = verify_trial(Path(value))
    assert result["passed"] and result["updates"] == [2, 3]
    assert len(result["fixed_results"]) == 4
    assert not result["paper_reproduced"]
