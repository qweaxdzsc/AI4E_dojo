/** 报告服务离线时用于保持报告中心可读的内置报告摘要。 */

export const fallbackReports = [
  ['rep-2026-0818-a', '机翼跨声速风洞试验 × CFD 对比验证报告', 'partial', '8/9 个块完成；保留一个诊断占位'],
  ['rep-2026-0814-b', '涡轮叶片热结构耦合分析周报', 'succeeded', '12/12 个块完成'],
  ['rep-2026-0812-c', '羽流扩散仿真初步结果', 'succeeded', '6/6 个块完成'],
  ['rep-2026-0811-d', '加热板几何校验与热分析准备报告', 'partial', '几何可读 · 缺少温度场，等待补充物理量'],
  ['rep-gs-pino-2026-0823', 'PINO Grad–Shafranov 多几何泛化审计报告', 'succeeded', '当前 fixture 已重算 · 源文档差异已归档说明'],
  ['rep-miller-tokamak-timeseries', 'Miller 托卡马克静电势时序场分析报告', 'succeeded', '240 帧真实数组已重算 · 合成展示场边界已标注'],
].map(([id, title, status, status_note]) => ({
  id, title, status, status_note, generated_at: '2026-08-23',
  author: 'AI4E 工程团队', formats: ['HTML'],
}));
