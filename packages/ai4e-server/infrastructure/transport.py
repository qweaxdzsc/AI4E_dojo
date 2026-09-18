"""JSON 传输缺失值规则：非有限统计显示为空，不改变运行事实。"""

import math

from fastapi.responses import JSONResponse


def finite_values(value):
    """递归保留普通数值，NaN/Infinity 作为未有有限结果传输。"""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: finite_values(child) for key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_values(child) for child in value]
    return value


class FiniteJSONResponse(JSONResponse):
    """兼容原始产物中的无最优值哨兵，不重写产物。"""

    def render(self, content):
        """将响应映射为标准 JSON。"""
        return super().render(finite_values(content))


def error_payload(detail: str, request_id: str) -> dict:
    """兼容 detail 字段，并提供供页面定位的稳定错误描述。"""
    code, _, location = detail.partition(": ")
    messages = {
        "configuration_revision_conflict": "配置已被修改，请刷新后重试，当前草稿尚未提交。",
        "stage_input_required": "请先选择此阶段需要的输入。",
        "train_requires_preparation": "训练设置只消费已有准备完成的数据，请先完成数据准备。",
        "idempotency_conflict": "重复提交的内容不同，请核对当前操作。",
        "path_outside_root": "所选文件不在可访问范围内。",
        "shared_dataset_exists": "同名项目共享数据集已存在，请确认是否覆盖。",
        "shared_dataset_busy": "该共享数据集正在处理，请等待当前运行结束。",
        "shared_dataset_unavailable": "共享数据集当前不可用，请检查原始处理结果。",
        "processed_dataset_name_conflict": "该平台数据集名称已存在。未确认覆盖时不能提交。",
        "preparation_requires_regeneration": (
            "数据准备已改用现行配置方式，这份旧准备不能再训，请按现行数据准备重新生成。"
        ),
        "inference_batch_not_found": "推理批次不存在或已被清理，请重新选择历史批次。",
    }
    message = messages.get(code, detail)
    if location and code in messages:
        message = message.rstrip("。") + "：" + location
    return {
        "detail": detail,
        "error": {
            "code": code,
            "location": location or None,
            "message": message,
            "request_id": request_id,
        },
    }
