"""源码开发启动入口，使用与安装包相同的 API 装配。"""
import argparse
import json
import os


def main():
    """从明确运行根启动，供独立应用浏览器验收使用。"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=8091)
    parser.add_argument('--context')
    parser.add_argument('--runtime-root')
    args = parser.parse_args()
    if args.runtime_root:
        os.environ['AI4E_VIS_RUNTIME_DIR'] = args.runtime_root
    from .api import app
    if args.context:
        from pathlib import Path
        value = app.state.runtime.register(json.loads(Path(args.context).read_text()))
        print('CONTEXT=' + value['context_id'], flush=True)
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=args.port)


if __name__ == '__main__':
    main()
