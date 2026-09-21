"""获取本轮约定的官方 8/2/2 轨迹；输出目录必须显式给定。"""

import argparse

from ai4e_contrib.application.datasets.cylinder_flow.download import download_subset

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    args = parser.parse_args()
    download_subset(args.output)
