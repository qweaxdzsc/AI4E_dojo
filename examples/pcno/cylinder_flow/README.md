# CylinderFlow 准入未通过

这是来源与阻断说明，不是可训练的standalone案例，不在已可用模型案例中登记。
官方train/valid/test前8/2/2条完整轨迹已取得，每条600帧，网格和字段保持原样。
固定P1三角形散度的面积加权散度/梯度比，训练/验证为5.57%—7.14%，超过本轮预设1%门槛。
没有用测试标签选择算子；没有启动该案例训练、网格映射或物理收益验证。

下载公开入口：`ai4e_contrib.application.datasets.cylinder_flow.download.download_subset`。
准入工具在 `tools/verification/pcno/cylinder/admission.py`；实际原始子集和报告在本机指定研究目录。
下一步应查明来源速度插值/求解离散，重新讨论相容约束；不能调高阈值把当前结果算通过。
