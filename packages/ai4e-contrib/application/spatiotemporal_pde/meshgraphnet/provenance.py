"""MeshGraphNet 来源和协议身份。"""


def identity() -> dict:
    """返回模型、案例、锁定参考版本和运行实现身份。"""
    return {
        "model": "MeshGraphNet",
        "case": "CylinderFlow",
        "reference": "DeepMind meshgraphnets cfd_model.py/cfd_eval.py",
        "reference_commit": "f5de0ede8430809180254ee957abf36ed62579ef",
        "runtime": "Dojo PyTorch implementation",
        "physicsnemo": {
            "role": "reference-only; not a runtime dependency",
            "commit": "aa19b58a129f8d1fabdcaa41c6ca85d5dc01aae1",
        },
    }
