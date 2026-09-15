/** 几何可视化模块的轻量视角模型。 */

/** 创建不含 O3DV 运行对象的可序列化视角。 */
export const createGeometryView = (overrides = {}) => ({
  projection: 'perspective',
  autoFit: true,
  showEdges: false,
  ...overrides,
});
