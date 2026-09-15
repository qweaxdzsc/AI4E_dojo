# 模块组：几何、图片与格式转换

## 业务边界

- [`visGeometry`](../../backend/modules/visGeometry/)：判断资产是否为几何，返回源 GLB 或生成 O3DV GLB 派生表现；不拥有解析数据库和转换内核。
- [`visConvertor`](../../backend/modules/visConvertor/)：低层文件格式到 GLB 转换及失败诊断，无独立前端和 Server。
- [`visFigure`](../../backend/modules/visFigure/)：白名单图片、视频和同源静态预览；不生成物理场动画，也不负责可视化资产持久化。

## 依赖方向

```text
visGeometry → dataAssets 公开资产/文件读取
            → visDatasets 公开内容解析
            → visConvertor 公开转换
            → var/derived/conversions
visFigure   → resources/examples/assets
```

前端几何入口为 [`frontend/src/modules/visGeometry/`](../../frontend/src/modules/visGeometry/)，`GeometryViewer` 与 O3DV URL 只从 `index.js` 暴露。图片当前由任务预览组合，没有独立 `visFigure` 前端模块。

## 测试入口

- `backend/tests/modules/test_vis_geometry.py`
- `backend/tests/modules/test_vis_convertor.py`
- `backend/tests/modules/test_vis_figure.py`
- `backend/tests/test_contract.py` 覆盖 VTU/PLY/OBJ/GLB、静态回退和真实文件头。

新增格式时先落 `visConvertor`，再由几何模块公开表现；不得把 URL、Router、资产状态或业务参数塞进 `visEngine`。
