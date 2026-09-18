"""可复制控制模板的配置连接。"""

from ai4e_contrib.application.pde_control.safediffcon.configuration import (
    application_parameters,
    component,
    load_configuration,
)

__all__ = ["component", "load_configuration", "plain"]


def plain(cfg, *, stage="train"):
    """程序入口也执行与文件加载相同的参数校验。"""
    return application_parameters(cfg, stage=stage)


if __name__ == "__main__":
    import argparse
    from pathlib import Path

    import yaml

    from ai4e_contrib.application.pde_control.safediffcon.migration import migrate_legacy

    parser = argparse.ArgumentParser(description="显式迁移旧控制配置到新文件")
    parser.add_argument("--migrate", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    value = migrate_legacy(
        yaml.safe_load(args.migrate.read_text()), base=args.migrate.resolve().parent
    )
    with args.output.open("x") as stream:
        yaml.safe_dump(value, stream, sort_keys=False)
