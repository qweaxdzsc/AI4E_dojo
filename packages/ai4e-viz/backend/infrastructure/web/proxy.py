"""流式代理本实例回环服务；地址仅由监督器提供。"""
import asyncio
import aiohttp
from fastapi import WebSocketDisconnect
from fastapi.responses import Response


async def http_proxy(request, base, path):
    """代理 HTTP 内容，保留媒体类型，不转发宿主 Cookie。"""
    url = base.rstrip('/') + '/' + path
    if request.url.query:
        url += '?' + request.url.query
    async with aiohttp.ClientSession() as client:
        async with client.request(request.method, url, data=await request.body(), headers={k:v for k,v in request.headers.items() if k.lower() in ('content-type','accept','range')}, allow_redirects=True) as response:
            return Response(await response.read(), status_code=response.status, headers={k:v for k,v in response.headers.items() if k.lower() in ('content-type','cache-control','content-range','accept-ranges')})


async def websocket_proxy(websocket, base, path):
    """双向转发文本与二进制帧，任一路断连同时关闭另一路。"""
    url = base.rstrip('/') + '/' + path
    if websocket.url.query:
        url += '?' + websocket.url.query
    await websocket.accept()
    async with aiohttp.ClientSession() as client:
        async with client.ws_connect(url, max_msg_size=0) as remote:
            async def inbound():
                try:
                    while True:
                        message = await websocket.receive()
                        if message['type'] == 'websocket.disconnect':
                            return
                        if message.get('bytes') is not None:
                            await remote.send_bytes(message['bytes'])
                        elif message.get('text') is not None:
                            await remote.send_str(message['text'])
                except WebSocketDisconnect:
                    pass
            async def outbound():
                async for message in remote:
                    if message.type == aiohttp.WSMsgType.BINARY:
                        await websocket.send_bytes(message.data)
                    elif message.type == aiohttp.WSMsgType.TEXT:
                        await websocket.send_text(message.data)
                    elif message.type in (aiohttp.WSMsgType.CLOSED, aiohttp.WSMsgType.ERROR):
                        return
            jobs = [asyncio.create_task(inbound()), asyncio.create_task(outbound())]
            try:
                await asyncio.wait(jobs, return_when=asyncio.FIRST_COMPLETED)
            finally:
                for job in jobs:
                    job.cancel()
                await asyncio.gather(*jobs, return_exceptions=True)
