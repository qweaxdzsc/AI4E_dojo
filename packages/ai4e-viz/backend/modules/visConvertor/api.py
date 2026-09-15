"""格式转换HTTP适配层；转换过程不自行创建Server。"""

from fastapi import APIRouter

router = APIRouter(tags=["visConvertor"])
