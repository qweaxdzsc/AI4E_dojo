"""时序播放、前进、倒退、暂停和循环业务规则。"""


def clamp_frame(frame: int, frame_count: int, loop: bool = False) -> int:
    """规范帧索引；循环模式取模，非循环模式限制到有效边界。"""

    if frame_count <= 0:
        raise ValueError("帧数必须大于零")
    if loop:
        return frame % frame_count
    return min(frame_count - 1, max(0, frame))
