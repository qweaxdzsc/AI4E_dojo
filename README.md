# AI4E_Dojo

AI4E_Dojo 是面向 Engineering AI / AI4S 的研究循环加速器。北极星指标是缩短“提出想法到得到可信结论”的时间。

## 当前状态

已建立 uv workspace。**本切片可安装并验收**数据源下载、路径读取、VTK 家族/NPY 统一 VTK 内存适配、字段提取、有效点 mask、几何派生（点到最近顶点 / 点到网格表面 / 表面法向）、重合点标记、点数校验、具名场张量落盘与读回、官方分片与打开样本、外流 pre 单样本/批量编排与统计量、外流 train 选定 AB-UPT 与作业级读盘探测；已提供显式训练、锚点评估及轮次恢复；完整网格推理、报告和 Web 仍为后续范围。

## 权威入口

1. [AI4E_Dojo_ARCHITECTURE (1).md](<docs/AI4E_Dojo_ARCHITECTURE (1).md>)：业务与代码架构的唯一权威来源。
2. [AGENTS.md](AGENTS.md)：开发顺序、依赖边界和强制工作流。
3. [.context/index.md](.context/index.md)：当前实现状态与模块导航。
4. [.context/mvp/abupt-mvp1.md](.context/mvp/abupt-mvp1.md)：AB-UPT MVP1 的目标链路和验收边界。

## 第一个 MVP

```text
ShapeNet-Car 原始数据
→ preprocess
→ AB-UPT train
→ checkpoint
→ full-mesh inference
→ 反归一化与网格回贴
→ eval
→ report
```

`user_project/` 和 `dos/` 是已有验证材料与迁移参考，不属于正式框架 API。新框架的 AB-UPT 接入不得依赖 Noether；完整模型位于 contrib，recipe 注入构造器，core 只保留提炼组件。

当前可复制运行入口：[aero_cfd 模板](recipes/aero_cfd/README.md)。模板不安装；共享数据集随 contrib 安装。

## 多域输入与缓存查询

多域 AB-UPT 使用结构版本 2：命名域、字段、局部特征、全局/几何条件由有序声明确定；固定布局多样本、无梯度推理缓存与分块查询已实现。输入对齐以锁定 Noether 实际处理器生成夹具为依据，不承诺网络数值、训练轨迹或精度等价。当前验证结果见 `.context/mvp/abupt-multidomain-acceptance.md`。

新案例配置使用 `model.data_specs`、`model.supervision`、`trainprep`、`sampling.domains`。`post.py` 经现有会话执行，显式设置 `post.checkpoint`，默认块长 `post.query_chunk_size=1024`；默认 pipeline 仍只 pre。旧五键入口和旧模型检查点已移除。
