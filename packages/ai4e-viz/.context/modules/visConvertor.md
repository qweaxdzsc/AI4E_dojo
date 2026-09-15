# visConvertor 文件索引

职责：几何兼容格式到 GLB 的转换和失败诊断；当前无前端模块。PRD：[`visConvertor.md`](../../docs/PRD/visConvertor.md)。

## 模块设计

`visConvertor`以一次格式转换命令/结果为业务边界，负责输入能力判断、输出约束和失败诊断；转换实现是本模块适配器，不属于`visEngine`。调用方只能使用`__init__.py`公开用例，输入/输出文件落盘复用Infrastructure存储原语。没有独立UI需求时不建立前端模块。

| 后端文件 | 作用 |
| --- | --- |
| [`__init__.py`](../../backend/modules/visConvertor/__init__.py) | 转换公开门面 |
| [`api.py`](../../backend/modules/visConvertor/api.py) | 预留协议适配，不建立独立 Server |
| [`application.py`](../../backend/modules/visConvertor/application.py) | 转换用例、输入输出和错误编排 |
| [`domain.py`](../../backend/modules/visConvertor/domain.py) | 格式能力与转换结果规则 |
| [`converter.py`](../../backend/modules/visConvertor/converter.py) | VTK/trimesh GLB 转换实现 |

测试：[`test_vis_convertor.py`](../../backend/tests/modules/test_vis_convertor.py)、[`test_excel_implemented_features.py`](../../backend/tests/test_excel_implemented_features.py)与几何契约测试；Excel专项构造真实STL并反读GLB。调用方为 [`visGeometry/application.py`](../../backend/modules/visGeometry/application.py)。


## Dojo 当前实现文件

- `backend/modules/visConvertor/__init__.py`：解析格式转换器一级模块公开门面。
- `backend/modules/visConvertor/api.py`：格式转换HTTP适配层；转换过程不自行创建Server。
- `backend/modules/visConvertor/application.py`：STEP、STL、DXF、CSV/JSON和GLB转换用例入口。
- `backend/modules/visConvertor/converter.py`：把VTK可读几何格式转换为浏览器O3DV可加载的GLB表现。
- `backend/modules/visConvertor/domain.py`：格式转换请求的纯领域对象。
