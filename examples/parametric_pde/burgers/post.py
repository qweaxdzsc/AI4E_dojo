"""post 独立阶段入口，算法由领域 application 执行。"""

import sys

sys.dont_write_bytecode = True
from configuration import load_configuration
from pipeline import execute

from ai4e_core import run

if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"post": lambda cfg: execute("post", cfg)},
            script=__file__,
            only=["post"],
            config_loader=load_configuration,
        )
    )
