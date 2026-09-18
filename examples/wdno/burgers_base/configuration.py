"""可复制的配置入口；普通函数可在此或步骤正文替换。"""

from ai4e_contrib.application.spatiotemporal_pde.wdno.configuration import (
    component,
    load_configuration,
    validate,
)
from ai4e_contrib.application.spatiotemporal_pde.wdno.migration import migrate_legacy

__all__ = ["component", "load_configuration", "validate"]


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    import yaml

    parser = argparse.ArgumentParser(description="将旧WDNO配置显式转换到新文件")
    parser.add_argument("--migrate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    converted = migrate_legacy(
        yaml.safe_load(args.migrate.read_text()), base=args.migrate.resolve().parent
    )
    with args.output.open("x") as stream:
        yaml.safe_dump(converted, stream, sort_keys=False)
