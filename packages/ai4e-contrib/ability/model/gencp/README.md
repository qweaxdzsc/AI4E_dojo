# GenCP 网络来源

来源提交与关键文件 SHA256 见 `source.json`。CNO 和 SiT-FNO 保留原网络算术；迁入只改变包内导入路径、增加模块说明。CNO 内部支持文件保留原版权声明及 LICENSE_NVIDIA.txt；GenCP 根许可证见 LICENSE。未使用的调试、JAX residual 和 FourierFeatures 模块未迁入。

支持原构造参数；官方缩小案例的参数在 examples 中显式展开。默认 CNO 激活沿用原实现，不据论文名称改成过滤激活。原 CUDA 扩展源文件随包保留，但本机验收只覆盖默认未过滤激活及 MPS/CPU；CUDA 自定义扩展未验收。
