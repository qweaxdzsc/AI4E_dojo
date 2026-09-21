"""infer 独立阶段入口，算法由领域 application 执行。"""

import sys

sys.dont_write_bytecode = True
from configuration import load_configuration
from pipeline import execute

from ai4e_core import run

if __name__ == "__main__":
    raise SystemExit(
        run.launch(
            {"infer": lambda cfg: execute("infer", cfg)},
            script=__file__,
            only=["infer"],
            config_loader=load_configuration,
        )
    )
