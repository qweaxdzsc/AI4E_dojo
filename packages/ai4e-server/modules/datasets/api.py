"""工作区已处理数据集列表。"""

from fastapi import APIRouter, Request

from ...bootstrap.dependencies import services
from .application import harvest

router = APIRouter()


@router.get("/datasets")
def listing(request: Request):
    """列出平台自己的已处理数据集。"""
    return harvest(services(request))
