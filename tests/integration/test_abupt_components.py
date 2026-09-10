"""与锁定来源组件比较，参考源码只读，不成为运行时依赖。"""

import importlib.util
from pathlib import Path

import pytest
import torch

from ai4e_core.abilities.modeling.modules.feed_forward import Mlp


@pytest.mark.parametrize(
    "filename,classname,parameters,shape",
    [
        ("mlp.py", "Mlp", {"dim": 24}, (2, 4, 24)),
        ("continuous_sincos_embed.py", "ContinuousSincosEmbed", {"dim": 24, "ndim": 3}, (2, 4, 3)),
        ("rope_frequency.py", "RopeFrequency", {"dim": 24, "ndim": 3}, (2, 4, 3)),
    ],
)
def test_component_output_gradient_and_keys(filename, classname, parameters, shape):
    source = Path("/Users/zonghui/work/new_code_project/AB-UPT/src/modules") / filename
    spec = importlib.util.spec_from_file_location("reference_" + classname, source)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    original = getattr(module, classname)(**parameters)
    if classname == "Mlp":
        extracted = Mlp(**parameters)
    else:
        from ai4e_core.abilities.modeling.modules import position_encoding

        extracted = getattr(position_encoding, classname)(**parameters)
    extracted.load_state_dict(original.state_dict(), strict=True)
    assert list(original.state_dict()) == list(extracted.state_dict())
    x = torch.rand(shape, requires_grad=True)
    y = x.detach().clone().requires_grad_()
    a, b = original(x), extracted(y)
    torch.testing.assert_close(a, b)
    a.real.sum().backward()
    b.real.sum().backward()
    torch.testing.assert_close(x.grad, y.grad)
    for left, right in zip(original.parameters(), extracted.parameters(), strict=True):
        torch.testing.assert_close(left.grad, right.grad)
