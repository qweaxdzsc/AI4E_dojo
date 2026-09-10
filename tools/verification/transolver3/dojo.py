"""运行真实 recipe 并通过原 writer 额外保留轮次快照，供恢复验收使用。"""

import argparse
import runpy
import shutil
import sys
from pathlib import Path


def main():
    """只观察已提交状态，不改训练数据、权重或更新步骤。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    from ai4e_core.run.training import TrainingRun

    original = TrainingRun.checkpoint

    def checkpoint(self, label, payload):
        result = original(self, label, payload)
        if label == "latest" and payload["epoch"] > 0:
            # 验收副本属于工具输出；运行目录仍只有原 writer 写入。
            folder = args.config.parent / "dojo-epoch-snapshots" / self.run_dir.name
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(result, folder / f"epoch-{payload['epoch']}.pt")
        return result

    TrainingRun.checkpoint = checkpoint
    recipe = Path(__file__).resolve().parents[3] / "recipes/aero_cfd/pipeline.py"
    sys.path.insert(0, str(recipe.parent))
    sys.argv = [str(recipe), "--config", str(args.config)]
    runpy.run_path(str(recipe), run_name="__main__")


if __name__ == "__main__":
    main()
