"""MCP协议适配边界。

MCP只能封装其他一级模块已经公开的应用操作，不能越过公开门面访问Repository。
"""

from fastapi import APIRouter

router = APIRouter(tags=["MCP"])
