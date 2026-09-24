# Dojo 测试最新状态

最新运行：2026-09-24 07:13–09:39 CST（周四增量轮次）。

- 圈定去重结果：289 passed / 1 failed / 2 skipped。
- 已恢复：上轮 16 个 recipe/infer、资源/probe 与 Task wheel 失败全部未复现。
- 新失败：Transolver-3 能力描述已发布 `eval`，测试仍断言旧名 `validation`；最小修复是更新测试并保留旧名兼容覆盖。
- 主安装副本抽查与源码一致；正式 8000 只读 200，但进程早于本轮变化，5173 未运行，正式 Web 未验收。
- `dojo_train` 约 320 GiB，磁盘可用约 139 GiB；未发现训练进程。

完整记录：[2026-09-24/report.md](2026-09-24/report.md)。
