"""独立数据生成入口，只调用 contrib 生成器，不启动训练。"""

import argparse
from pathlib import Path

from omegaconf import OmegaConf

from ai4e_contrib.application.datasets.parametric import component

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="独立生成 PDE 数据集")
    parser.add_argument("--config", required=True)
    parser.add_argument("--set", action="append", default=[])
    args = parser.parse_args()
    cfg = OmegaConf.to_container(
        OmegaConf.merge(OmegaConf.load(args.config), OmegaConf.from_dotlist(args.set)), resolve=True
    )
    case = cfg.pop("case")
    root = Path(cfg["output"]).expanduser()
    cfg["output"] = str(root if root.is_absolute() else Path(args.config).resolve().parent / root)
    print(component(case).generate(cfg))
