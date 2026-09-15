"""Readable report fixtures served by the backend API."""

from __future__ import annotations


REPORTS = [
    {
        "id": "rep-2026-0818-a",
        "title": "机翼跨声速风洞试验 × CFD 对比验证报告",
        "status": "partial",
        "status_note": "8/9 个块完成；一个频谱块以诊断占位呈现",
        "generated_at": "2026-08-18 15:42",
        "author": "李航",
        "spec": "rspec-1027 v2",
        "formats": ["HTML", "PDF", "PNG"],
    },
    {
        "id": "rep-2026-0814-b",
        "title": "涡轮叶片热结构耦合分析周报",
        "status": "succeeded",
        "status_note": "12/12 个块完成",
        "generated_at": "2026-08-14 18:20",
        "author": "原力",
        "spec": "rspec-1019 v1",
        "formats": ["HTML", "PDF"],
    },
    {
        "id": "rep-2026-0812-c",
        "title": "羽流扩散仿真初步结果",
        "status": "succeeded",
        "status_note": "6/6 个块完成",
        "generated_at": "2026-08-12 11:05",
        "author": "张奕",
        "spec": "rspec-1003 v3",
        "formats": ["HTML"],
    },
    {
        "id": "rep-2026-0811-d",
        "title": "加热板几何校验与热分析准备报告",
        "status": "partial",
        "status_note": "几何可读 · 缺少温度场，等待补充物理量",
        "generated_at": "2026-08-11 09:48",
        "author": "原力",
        "spec": "rspec-heater-preflight v2",
        "formats": ["HTML", "数据诊断"],
    },
]


REPORT_BY_ID = {item["id"]: item for item in REPORTS}


REPORT_DOCUMENTS = {
    "rep-2026-0818-a": {
        **REPORT_BY_ID["rep-2026-0818-a"],
        "summary": "在 Ma 0.82、Re 4.1×10⁶ 工况下，CFD 与风洞测得的升力趋势一致；主要偏差集中在上表面激波位置。",
        "takeaways": [
            "升力系数相对误差 2.8%，满足 5% 验收阈值。",
            "上表面激波位置较试验提前 1.7% 弦长。",
            "P4 通道缺测 34%，不参与峰值判定。",
        ],
        "sections": [
            {
                "id": "overview", "title": "结论摘要", "blocks": [
                    {"type": "metrics", "title": "关键验证指标", "items": [
                        {"label": "升力系数误差", "value": "2.8", "unit": "%", "state": "ok"},
                        {"label": "激波位置偏差", "value": "1.7", "unit": "%c", "state": "warn"},
                        {"label": "有效测压通道", "value": "8/9", "unit": "", "state": "partial"},
                    ]},
                    {"type": "markdown", "title": "工程判断", "body": "CFD 可用于本轮载荷外推，但应在后续网格中加密上表面 55%–70% 弦长区域。"},
                ],
            },
            {
                "id": "evidence", "title": "压力分布证据", "blocks": [
                    {"type": "example", "title": "Cp 分布与测点证据", "artifact_id": "A-1025", "caption": "多通道时序用于确认稳态窗口；关键值不依赖 hover。"},
                    {"type": "table", "title": "代表测点", "columns": ["测点", "x/c", "试验 Cp", "CFD Cp", "差值"], "rows": [
                        ["U-08", "0.18", "-1.82", "-1.76", "+0.06"],
                        ["U-21", "0.61", "-1.18", "-0.94", "+0.24"],
                        ["L-11", "0.34", "+0.42", "+0.39", "-0.03"],
                    ]},
                    {"type": "error", "title": "频谱块未生成", "code": "BLOCK-FFT-014", "message": "P4 缺测率超过频谱分析阈值；其余报告块不受影响。", "recovery": "补齐 P4 数据或在 Spec 中排除该通道后重新生成。"},
                ],
            },
            {
                "id": "geometry", "title": "几何与复现信息", "blocks": [
                    {"type": "example", "title": "机翼表面几何固定视角", "artifact_id": "A-1031", "caption": "交互使用 Online3DViewer；静态降级来自同一模型和固定相机。"},
                    {"type": "source", "title": "来源与限制", "body": "风洞批次 WT-2026-0817；CFD release cfd-r118；P4 缺测不用于统计结论。"},
                ],
            },
        ],
    },
    "rep-2026-0814-b": {
        **REPORT_BY_ID["rep-2026-0814-b"],
        "summary": "叶片在本周目标工况下满足热与结构安全裕度，压力面前缘仍是热梯度敏感区域。",
        "takeaways": [
            "最高温度 1,168 K，低于材料限值 1,220 K。",
            "最大等效应力 486 MPa，安全系数 1.34。",
            "冷却方案 B 将前缘温度降低 37 K。",
        ],
        "sections": [
            {"id": "overview", "title": "本周结论", "blocks": [
                {"type": "metrics", "title": "热结构裕度", "items": [
                    {"label": "最高温度", "value": "1168", "unit": "K", "state": "warn"},
                    {"label": "最大等效应力", "value": "486", "unit": "MPa", "state": "ok"},
                    {"label": "安全系数", "value": "1.34", "unit": "", "state": "ok"},
                ]},
                {"type": "markdown", "title": "建议", "body": "冻结冷却方案 B，并在前缘 12% 弦长区域增加一个温度监测点。"},
            ]},
            {"id": "thermal", "title": "温度与压力场", "blocks": [
                {"type": "example", "title": "燃烧室温度体数据", "artifact_id": "A-1028", "caption": "默认正交切片，按需进入体渲染。"},
                {"type": "example", "title": "叶片压力场", "artifact_id": "A-1108", "caption": "物理场由 Trame 渲染，与 O3DV 几何语义分离。"},
            ]},
            {"id": "geometry", "title": "几何检查", "blocks": [
                {"type": "example", "title": "涡轮叶片几何网格", "artifact_id": "A-1027", "caption": "VTU 表面转换为 GLB 后由 Online3DViewer 加载。"},
                {"type": "table", "title": "方案对照", "columns": ["方案", "Tmax (K)", "应力 (MPa)", "安全系数"], "rows": [["A", "1205", "498", "1.29"], ["B", "1168", "486", "1.34"], ["C", "1179", "472", "1.38"]]},
                {"type": "source", "title": "来源与限制", "body": "热边界来自 combustor-r42；材料曲线为 IN718 rev.6；接触热阻仍按设计值。"},
            ]},
        ],
    },
    "rep-2026-0812-c": {
        **REPORT_BY_ID["rep-2026-0812-c"],
        "summary": "羽流核心长度和扩散半角已进入设计窗口，但下游温度衰减仍比目标慢。",
        "takeaways": [
            "羽流核心长度 1.82 m，目标 1.7–1.9 m。",
            "扩散半角 11.6°，较基线增加 1.9°。",
            "x=2.0 m 处中心线温度高于目标 42 K。",
        ],
        "sections": [
            {"id": "overview", "title": "阶段结论", "blocks": [
                {"type": "metrics", "title": "羽流尺度", "items": [
                    {"label": "核心长度", "value": "1.82", "unit": "m", "state": "ok"},
                    {"label": "扩散半角", "value": "11.6", "unit": "°", "state": "ok"},
                    {"label": "温度超差", "value": "+42", "unit": "K", "state": "warn"},
                ]},
                {"type": "markdown", "title": "下一步", "body": "提高二次流掺混比 3%，并在下游 1.5–2.5 m 区间补充截面采样。"},
            ]},
            {"id": "trajectory", "title": "轨迹与截面证据", "blocks": [
                {"type": "example", "title": "羽流粒子轨迹", "artifact_id": "A-1029", "caption": "轨迹颜色编码速度，二维备用图保留相同结论。"},
                {"type": "example", "title": "喷口粒子瞬时点集", "artifact_id": "A-1109", "caption": "高温粒子集中在轴线，点选不是读取关键值的唯一方式。"},
                {"type": "table", "title": "阶段目标", "columns": ["指标", "当前", "目标", "状态"], "rows": [["核心长度", "1.82 m", "1.7–1.9 m", "通过"], ["扩散半角", "11.6°", "> 11°", "通过"], ["2m 温度", "742 K", "≤700 K", "需改进"]]},
                {"type": "source", "title": "来源与限制", "body": "粒子数 900；采样 160 帧；当前结果未包含环境横风。"},
            ]},
        ],
    },
    "rep-2026-0811-d": {
        **REPORT_BY_ID["rep-2026-0811-d"],
        "summary": "加热板 STL 已按识别出的 GEO/mesh 成功解析并可在线查看；文件不含温度或热流密度数组，因此本报告完成几何验收与热分析输入准备，不虚构热场结论。",
        "takeaways": [
            "A-1030 的源文件是可解析的 STL 几何，识别类型为 GEO/mesh。",
            "原声明 FLD/field 与实际内容不一致，已保留为可恢复的校验警告。",
            "当前文件没有温度、热流密度或材料属性，不能生成真实热场；补充场数据后即可继续。",
        ],
        "sections": [
            {"id": "conclusion", "title": "验收结论", "blocks": [
                {"type": "metrics", "title": "当前可证实状态", "items": [
                    {"label": "几何解析", "value": "通过", "unit": "", "state": "ok"},
                    {"label": "识别类型", "value": "GEO/mesh", "unit": "", "state": "ok"},
                    {"label": "物理场数组", "value": "0", "unit": "个", "state": "warn"},
                ]},
                {"type": "markdown", "title": "工程判断", "body": "当前数据足以完成几何完整性检查，但不足以计算温度分布、热梯度或热应力。系统将类型不一致作为警告呈现，同时允许按识别出的几何类型查看真实模型。"},
            ]},
            {"id": "geometry", "title": "加热板几何证据", "blocks": [
                {"type": "example", "title": "加热板 STL 几何", "artifact_id": "A-1030", "caption": "按识别出的 GEO/mesh 使用 Online3DViewer 打开；不会把 STL 冒充为物理场。"},
                {"type": "table", "title": "输入完整性检查", "columns": ["检查项", "结果", "处理"], "rows": [
                    ["STL 几何拓扑", "可解析", "进入几何验收"],
                    ["温度数组", "缺失", "补充 VTI/VTU/NPZ 场数据"],
                    ["热流密度", "缺失", "补充边界条件或场数组"],
                    ["材料属性", "未提供", "在热分析配置中补充"],
                ]},
            ]},
            {"id": "next", "title": "恢复热分析的输入要求", "blocks": [
                {"type": "source", "title": "建议数据包", "body": "保留 A-1030 作为几何资产，并新增一个关联的 FLD/field 或 FLD/volume 数据资产。场文件需要包含温度变量、单位、网格关联方式以及必要的时间步；系统会分别用 Online3DViewer 展示几何、用 Trame/vtk.js 展示物理场。"},
                {"type": "source", "title": "来源", "body": "几何来源：A-1030 / heater_plate_field.stl。该报告不再引用已删除的 vspec-0388 或 A-1019。"},
            ]},
        ],
    },
}
