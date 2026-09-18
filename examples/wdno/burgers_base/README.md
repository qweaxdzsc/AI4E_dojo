# WDNO Burgers 基础预测案例

本目录可独立复制。公共配置、Task托管、续训、旧配置转换与组件扩展见[研究模板](../../../recipes/wdno/README.md)；实际数值范围见[验收记录](../../../.context/mvp/wdno-acceptance.md)。

本案例的完整脚本与配置直接复制到研究目录后使用，不需要先从模板替换文件。先填 `inputs.rawprep.source/indices`，分别配置运行和数据目录；CPU小样本验收可显式缩小模型和更新数，默认配置仍保留原基础网络。

可直接执行复制目录的 `pipeline.py`，也可将复制目录传给Task的 `new_task`。分阶段时绑定上一阶段报告给出的文件，不能依赖当前工作目录或“最新文件”查找。当前安装、两个恢复入口及复制品绑定方式见主模板；本例通过 `task_replay --staged --case example` 单独验收，不能以模板成功代替。
