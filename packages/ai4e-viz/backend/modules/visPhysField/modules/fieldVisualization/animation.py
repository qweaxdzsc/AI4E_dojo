"""动画录制请求和输出格式业务规则。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class AnimationRequest:
    """一次物理场动画录制的业务参数。"""

    frames_per_second: int = 24
    format: str = "mp4"


def validate_animation(request: AnimationRequest) -> AnimationRequest:
    """校验动画帧率和当前支持的输出格式。"""

    if not 1 <= request.frames_per_second <= 120:
        raise ValueError("动画帧率必须位于1到120")
    if request.format.lower() not in {"mp4", "gif"}:
        raise ValueError("动画仅支持MP4或GIF")
    return request
