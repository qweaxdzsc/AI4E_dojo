"""Python 3.9 隔离环境入口，仅消费数值 NPZ 并返回响应 NPY。"""

import argparse
import numpy as np
from kstar import KSTARSolver


def main():
    """每个样本创建原始求解器，保留重置、加载、裁剪和取整。"""
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input",required=True)
    parser.add_argument("--output",required=True)
    args=parser.parse_args()
    actions=np.load(args.input,allow_pickle=False)["controls"]
    if actions.ndim!=3 or actions.shape[1:]!=(121,9) or not np.isfinite(actions).all():
        raise ValueError("KSTAR 控制必须为有限的 B×121×9 数组")
    responses=[]
    for action in actions:
        responses.append(KSTARSolver(random_seed=0).simulate(action))
    np.save(args.output,np.asarray(responses),allow_pickle=False)


if __name__=="__main__":
    main()
