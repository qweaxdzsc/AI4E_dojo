# SafeDiffCon · tokamak

本目录可整体复制，直接运行pipeline.py或作为Task新建来源；不依赖仓库外的recipe脚本。六阶段正文允许自由编辑。

配置及命令见[研究模板说明](../../../recipes/safediffcon/README.md)，实际安装与训练证据见[验收记录](../../../.context/mvp/safediffcon-acceptance.md)。config.yaml和quick.yaml保留同一缩小科研默认；每案例累计180分钟仍由原账本监督。

先填写inputs.rawprep.source；Tokamak另外填写inputs.infer.solver_assets及solver.python。独立阶段绑定各自inputs，完整流程由Python传递返回值。源码导入成功不能代替实际训练和求解成功。
