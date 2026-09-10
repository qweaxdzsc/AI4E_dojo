# ADR-0001：仓库分包与依赖边界

- 状态：Accepted
- 日期：2026-09-06

## 决策

AI4E_Dojo 采用单仓多包结构，以 `ai4e-spec` 作为稳定契约层，以 `ai4e-core` 作为本地可独立运行的执行层，并将 recipes、task、viz、server、web 和 contrib 放在依赖方向明确的独立包中。

AB-UPT MVP1 不复制或内嵌所有模型源码。AB-UPT 保持独立，框架通过 adapter、constraint 和 recipe 接入；新包不得依赖 Noether。

## 原因

该边界允许训练在无服务环境运行，保证 run artifact 可被 task/viz/server 独立消费，并降低用户组件被 core 重构破坏的概率。

## 当前限制

本 ADR 只确认目录和依赖方向；包清单、公开接口和运行行为尚未实现。
