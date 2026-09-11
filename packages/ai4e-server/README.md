# Dojo 本机服务

项目、任务、配置、血缘、固定比较与研究执行均通过 ai4e-task 公开接口。服务提供五段配置、检查/试跑/正式执行、模型跟踪、训练恢复与真实指标；可视化转换经独立 viz 进程。报告发布、批量派生与排队研究运行尚未开放。

从仓库根启动（Python 3.12）：

```bash
uv sync --group dev --inexact
uv run python -m ai4e_server --root /path/to/dojo-platform --template "$PWD/recipes/aero_cfd" --data-root /path/to/shapenet --data-root /path/to/nasa --port 8000
```

`--root` 是需要长期保留的本机平台目录：项目与 task 运行在 projects，服务记录在 server.sqlite，辅助显示产物在 display，旧预览缓存在 previews。重启使用同一 root；不要将需要保留的正式研究放在会自动清理的临时目录。服务只监听 127.0.0.1；接口说明 /docs，健康检查 /api/v1/health。增加 `--web-dist "$PWD/packages/ai4e-web/dist"` 可同源托管页面。

可重复登记 `--data-root`，按顺序获得 data0、data1 等身份。登记案例要求模板位于仓库 recipes/aero_cfd，并在同仓 examples/aero_cfd 找到四个正式案例配置。`GET projects/{p}/tasks/cases` 返回实际存在的登记项；创建传 case_id，可不绑定数据。研究运行前严格检查实际输入。

NASA 的 train_h5/test_h5/connectivity_h5 可以分别绑定到不同目录。创建传 `data_sources`，已有任务使用 `PUT projects/{p}/tasks/{t}/dataset`，请求包含 expected_revision 与 sources；每个值是 `{root:"data1",path:"相对文件路径"}` 或固定 AssetRef。浏览器不传任意绝对路径；文件缺失按来源键报告，用户无需复制或移动数据。

配置修订冲突拒绝覆盖；试跑产物独立标记，不成为默认正式输入。辅助操作可取消，服务关闭会中断、终止并回收自身辅助进程，清理未完成显示缓存；重启保留 interrupted 状态而不重放计算。task 研究运行独立管理，服务关闭不停止研究运行，重启后查询现有事实。

单层包安装通过 wheel 映射。源码修改后核对加载位置，必要时刷新安装副本：

```bash
uv sync --offline --all-packages --reinstall-package ai4e-task --reinstall-package ai4e-server --reinstall-package ai4e-viz --reinstall-package ai4e-spec
```

当前整体证据与未交付边界见 ../../.context/mvp/web-integrated-acceptance.md；历史首期证据保留于 web-rawprep-acceptance.md。工程构建不代表真实流程验收。
