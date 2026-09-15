/** 可视化任务模块统一对外展示的中文业务术语。 */

export const UI_TERMS = Object.freeze({
  artifact: '数据资产',
  family: '数据家族',
  kind: '数据语义类型',
  method: '可视化方法',
  spec: '可视化配置',
  visualization: '可视化结果',
  renderer: '渲染器',
  format: '文件格式',
  dtype: '字段类型'
});

export const TECHNICAL_TERMS = Object.freeze({
  family: 'Family',
  kind: 'ArtifactKind',
  method: 'Function',
  spec: 'Spec',
  visualization: 'Visualization'
});

export const terminologyLabel = (key) => `${UI_TERMS[key]}（${TECHNICAL_TERMS[key]}）`;
