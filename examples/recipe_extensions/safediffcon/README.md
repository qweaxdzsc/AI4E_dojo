# 控制研究扩展

复制SafeDiffCon模板和本目录`variants.py`到仓库外实验目录，按模板README设置模型、引导或派生组件路径。三种变体使用独立输出位置；数值和实际运行证据见`.context/mvp/safediffcon-acceptance.md`。

安全变体只改变采样时的安全梯度，并增加控制能量惩罚；校准、重加权与评价阈值保持基线语义，因此可直接比较结果。
