# visFigure 文件索引

职责：PNG/JPG/视频等同源静态预览；当前没有独立前端模块，由任务预览组合。PRD：[`visFigure.md`](../../docs/PRD/visFigure.md)。

## 模块设计

`visFigure`拥有图片/同源静态媒体的格式白名单、尺寸与预览语义，不拥有原始资产记录。Application通过`dataAssets`公开门面定位文件并产出受控预览响应；当前前端能力由`visTaskManage`预览聚合，功能规模不足时不创建空Page或全局图片Store。

| 后端文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visFigure/__init__.py) | 图片预览公开门面 |
| [`api.py`](../../backend/modules/visFigure/api.py) | 示例静态资产 Router |
| [`application.py`](../../backend/modules/visFigure/application.py) | 资产定位与预览用例 |
| [`domain.py`](../../backend/modules/visFigure/domain.py) | 格式、尺寸和白名单规则 |

测试：[`test_vis_figure.py`](../../backend/tests/modules/test_vis_figure.py)、[`test_contract.py`](../../backend/tests/test_contract.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)及图片真实解码E2E。前端调用位置见 [`visTaskManage/components/ExamplePreview.jsx`](../../frontend/src/modules/visTaskManage/components/ExamplePreview.jsx)。


## Dojo 当前实现文件

- `backend/modules/visFigure/__init__.py`：图片预览一级模块公开门面。
- `backend/modules/visFigure/api.py`：图片及静态预览资产的 HTTP 适配层。
- `backend/modules/visFigure/application.py`：PNG/JPG图片预览用例。
- `backend/modules/visFigure/domain.py`：图片预览领域值对象。
