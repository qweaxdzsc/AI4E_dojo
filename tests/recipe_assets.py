"""迁移前配置仅用于底层行为回归；新入口另行集成测试。"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "tests/fixtures/legacy_pre.yaml"
RECIPE_DIR = ROOT
STATS_PATH = ROOT / "packages/ai4e-contrib/application/datasets/shapenet_car/statistics.yaml"
SPLITS_PATH = STATS_PATH.with_name("partition.yaml")
