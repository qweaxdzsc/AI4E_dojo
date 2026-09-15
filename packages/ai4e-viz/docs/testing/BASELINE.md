# 功能回归基线

## 后端

目录重构前隔离临时 SQLite 的结果为 `51 passed, 2 failed, 1 skipped`。既有失败：

1. 动态参数 Schema 的 `x` 缺少数据画像枚举。
2. A-1030 STL 转 O3DV GLB 返回 500。

加入七项架构门禁并切换模块依赖后，结果为 `58 passed, 2 failed, 1 skipped`，没有新增
功能回归。任何后续失败必须与以上两项区分。

## 前端

`npm run check:architecture` 与 `npm run build` 已通过。当前 `npm test` 在用例启动前因
Node、jsdom 与 undici 组合不兼容而终止：`webidl.util.markAsUncloneable is not a function`。
这属于测试运行时基线问题，不能以“测试通过”表述，修复运行时后必须重新执行用例。

## 重构完成后的复验

2026-08-29 数据恢复修订后按 CI 的真实工作目录执行最终回归：后端在 `backend/` 下运行完整测试，结果为
`85 passed, 1 skipped`；前端架构门禁通过，Vitest 为 `11 passed`，生产构建通过。仓库根
直接执行 `pytest backend/tests` 不属于受支持入口，因为 Python 模块根目录是 `backend/`；
CI 与本地验收均应先进入 `backend/`。

## 2026-08-29 · Excel功能点专项基线

- 逐项矩阵：[`EXCEL_FEATURE_TEST_MATRIX.md`](EXCEL_FEATURE_TEST_MATRIX.md)，覆盖80个非空功能项。
- 既有模块与跨模块契约抽样：`67 passed`。
- 新增后端Excel专项：`18 passed`。
- 新增桌面端Excel E2E：`6 passed`。
- 新增移动端Excel E2E：`6 passed`；第32项通过滑块键盘替代操作，按钮可达性仍记为`partial`。
- 加入专项后的后端最终全量：`107 passed, 1 skipped`。
- 前端架构门禁通过，Vitest为`13 passed`，生产构建通过。
- 完整三服务Playwright（既有主链路+Excel专项、桌面+移动）：`31 passed, 1 skipped`；跳过项是按设计只在桌面执行一次的G-S完整HTML冻结。
- 本基线只把22项记为`implemented`；其余15项`partial`、16项`demo_only`、27项`not_implemented`均不得在验收报告中写成完整通过。
