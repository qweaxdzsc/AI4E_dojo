"""MeshGraphNet 的固定结果和运行索引交接声明。"""

from __future__ import annotations


def result_contract() -> dict:
    """返回固定 rollout 结果和指标的公开字段说明。"""
    return {
        "kind": "meshgraphnet-cylinder-flow-trajectory-v2",
        "fields": {
            "sample_id": "string",
            "prediction": "T,N,2",
            "target": "T,N,2",
            "position": "N,2",
            "cells": "F,3",
            "node_type": "N",
        },
        "metric_semantics": "cumulative rollout MSE over predicted frames 1..H",
        "metrics": [
            "mse_1_steps",
            "mse_10_steps",
            "mse_20_steps",
            "mse_50_steps",
            "mse_100_steps",
            "mse_200_steps",
        ],
    }
