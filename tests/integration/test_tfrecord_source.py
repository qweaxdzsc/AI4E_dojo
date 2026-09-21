"""TFRecord 帧读取保持字段解释在数据集适配器之外。"""

import struct

import numpy as np
import pytest

from ai4e_contrib.application.datasets.cylinder_flow.adapter import decode_trajectory
from ai4e_core.abilities.data.source import tfrecord


def _varint(value):
    result = bytearray()
    while value >= 0x80:
        result.append((value & 0x7F) | 0x80)
        value >>= 7
    result.append(value)
    return bytes(result)


def _field(number, payload):
    return _varint(number << 3 | 2) + _varint(len(payload)) + payload


def _example(features):
    entries = []
    for key, value in features.items():
        bytes_list = _field(1, value)
        feature = _field(1, bytes_list)
        entries.append(_field(1, _field(1, key.encode()) + _field(2, feature)))
    return _field(1, b"".join(entries))


def test_tfrecord_frame_and_crc(tmp_path):
    payloads = [b"first", b"second"]
    path = tmp_path / "sample.tfrecord"
    with path.open("wb") as stream:
        for payload in payloads:
            length = struct.pack("<Q", len(payload))
            stream.write(length)
            stream.write(struct.pack("<I", tfrecord._masked_crc(length)))
            stream.write(payload)
            stream.write(struct.pack("<I", tfrecord._masked_crc(payload)))
    assert list(tfrecord.iter_tfrecord(path)) == payloads
    damaged = bytearray(path.read_bytes())
    damaged[-5] ^= 1
    path.write_bytes(damaged)
    with pytest.raises(ValueError, match="校验失败"):
        list(tfrecord.iter_tfrecord(path))


def test_example_bytes_and_cylinder_trajectory_decode():
    cells = np.array([[[0, 1, 2]]], dtype=np.int32)
    position = np.array([[[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]], dtype=np.float32)
    node_type = np.array([[[0], [5], [6]]], dtype=np.int32)
    velocity = np.arange(18, dtype=np.float32).reshape(3, 3, 2)
    pressure = np.zeros((3, 3, 1), dtype=np.float32)
    payload = _example(
        {
            "cells": cells.tobytes(),
            "mesh_pos": position.tobytes(),
            "node_type": node_type.tobytes(),
            "velocity": velocity.tobytes(),
            "pressure": pressure.tobytes(),
        }
    )
    assert tfrecord.parse_example_bytes(payload)["velocity"] == [velocity.tobytes()]
    meta = {
        "trajectory_length": 3,
        "field_names": ["cells", "mesh_pos", "node_type", "velocity", "pressure"],
        "features": {
            "cells": {"type": "static", "shape": [1, -1, 3], "dtype": "int32"},
            "mesh_pos": {"type": "static", "shape": [1, -1, 2], "dtype": "float32"},
            "node_type": {"type": "static", "shape": [1, -1, 1], "dtype": "int32"},
            "velocity": {"type": "dynamic", "shape": [3, -1, 2], "dtype": "float32"},
            "pressure": {"type": "dynamic", "shape": [3, -1, 1], "dtype": "float32"},
        },
    }
    decoded = decode_trajectory(payload, meta)
    assert decoded["velocity"].shape == (3, 3, 2)
    assert decoded["node_type"].tolist() == [0, 5, 6]
