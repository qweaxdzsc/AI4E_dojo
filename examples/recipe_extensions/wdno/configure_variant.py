"""在复制的完整研究目录中显式选择训练变体，保留已有数据输入。"""

from pathlib import Path

import yaml


def configure():
    path = Path(__file__).with_name("config.yaml")
    cfg = yaml.safe_load(path.read_text())
    cfg["run_root"] = "./runs/research"
    cfg["data_root"] = "./data/research"
    cfg["train"].update(updates=4, lr=0.0002)
    cfg["inputs"]["train"]["resume"] = None
    cfg["components"].update(
        network="variants.custom_network",
        objective="variants.custom_loss",
        derived="variants.energy",
        optimizer="variant_training.optimizer",
        scheduler="variant_training.scheduler",
        update="variant_training.update",
    )
    path.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False))


if __name__ == "__main__":
    configure()
