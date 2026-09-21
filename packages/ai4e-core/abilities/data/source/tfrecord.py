"""不依赖 TensorFlow 的 TFRecord 帧与 ``tf.train.Example`` 基础读取原语。

本模块负责长度、CRC、protobuf wire framing 和 bytes feature 提取；dtype、shape、静态
字段展开等业务解释由数据集适配器完成。
"""

from __future__ import annotations

import struct
from collections.abc import Iterator
from pathlib import Path


def _crc_entry(byte: int) -> int:
    crc = byte
    for _ in range(8):
        crc = (crc >> 1) ^ (0x82F63B78 if crc & 1 else 0)
    return crc


_CRC_TABLE = tuple(_crc_entry(i) for i in range(256))


def _crc32c(data: bytes) -> int:
    crc = 0xFFFFFFFF
    for byte in data:
        crc = (crc >> 8) ^ _CRC_TABLE[(crc ^ byte) & 255]
    return crc ^ 0xFFFFFFFF


def _masked_crc(data: bytes) -> int:
    crc = _crc32c(data)
    return ((crc >> 15) | (crc << 17)) + 0xA282EAD8 & 0xFFFFFFFF


def iter_tfrecord(path: str | Path, *, validate_crc: bool = True) -> Iterator[bytes]:
    """逐条读取 TFRecord 内容，返回原始 payload。"""
    with Path(path).open("rb") as stream:
        index = 0
        while True:
            header = stream.read(12)
            if not header:
                return
            if len(header) != 12:
                raise ValueError(f"TFRecord {path} 在记录 {index} 截断")
            length, length_crc = struct.unpack("<QI", header)
            if validate_crc and _masked_crc(header[:8]) != length_crc:
                raise ValueError(f"TFRecord {path} 记录 {index} 长度校验失败")
            payload = stream.read(length)
            payload_crc = stream.read(4)
            if len(payload) != length or len(payload_crc) != 4:
                raise ValueError(f"TFRecord {path} 在记录 {index} 内容截断")
            if validate_crc and _masked_crc(payload) != struct.unpack("<I", payload_crc)[0]:
                raise ValueError(f"TFRecord {path} 记录 {index} 内容校验失败")
            yield payload
            index += 1


def parse_example_bytes(payload: bytes) -> dict[str, list[bytes]]:
    """读取 ``tf.train.Example`` 中的 bytes features。

    MeshGraphNets 把数组编码在 ``BytesList`` 中。这里实现 protobuf wire format 的最小
    中立子集，同时会跳过未知标量字段；遇到非 bytes feature 时明确失败，避免把字段
    类型错误静默解释为数组内容。
    """
    features_message = _single_length_delimited(payload, 1, context="Example.features")
    result: dict[str, list[bytes]] = {}
    for field, wire_type, entry in _fields(features_message):
        if field != 1 or wire_type != 2:
            continue
        key_raw = _single_length_delimited(entry, 1, context="Features.feature.key")
        feature = _single_length_delimited(entry, 2, context="Features.feature.value")
        try:
            key = key_raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("tf.train.Example feature 名称不是 UTF-8") from exc
        bytes_list = _single_length_delimited(feature, 1, context=f"Feature[{key}].bytes_list")
        values = [value for number, kind, value in _fields(bytes_list) if number == 1 and kind == 2]
        if not values:
            raise ValueError(f"tf.train.Example feature {key!r} 没有 bytes 值")
        result[key] = values
    if not result:
        raise ValueError("tf.train.Example 不包含 bytes features")
    return result


def _single_length_delimited(payload: bytes, field: int, *, context: str) -> bytes:
    values = [value for number, kind, value in _fields(payload) if number == field and kind == 2]
    if len(values) != 1:
        raise ValueError(f"{context} 必须恰好出现一次")
    return values[0]


def _fields(payload: bytes) -> Iterator[tuple[int, int, bytes | int]]:
    offset = 0
    while offset < len(payload):
        tag, offset = _varint(payload, offset)
        field, wire_type = tag >> 3, tag & 7
        if field <= 0:
            raise ValueError("protobuf 字段编号必须为正")
        if wire_type == 0:
            value, offset = _varint(payload, offset)
            yield field, wire_type, value
        elif wire_type == 1:
            end = offset + 8
            if end > len(payload):
                raise ValueError("protobuf fixed64 字段截断")
            yield field, wire_type, payload[offset:end]
            offset = end
        elif wire_type == 2:
            length, offset = _varint(payload, offset)
            end = offset + length
            if end > len(payload):
                raise ValueError("protobuf bytes 字段截断")
            yield field, wire_type, payload[offset:end]
            offset = end
        elif wire_type == 5:
            end = offset + 4
            if end > len(payload):
                raise ValueError("protobuf fixed32 字段截断")
            yield field, wire_type, payload[offset:end]
            offset = end
        else:
            raise ValueError(f"不支持的 protobuf wire type: {wire_type}")


def _varint(payload: bytes, offset: int) -> tuple[int, int]:
    value = 0
    for shift in range(0, 70, 7):
        if offset >= len(payload):
            raise ValueError("protobuf varint 截断")
        byte = payload[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if byte < 0x80:
            return value, offset
    raise ValueError("protobuf varint 超出 64 位范围")
