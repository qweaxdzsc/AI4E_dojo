/** 三维物理场一级共享模型、Command和Query名称。 */

export const PHYS_FIELD_ACTION = Object.freeze({ setView: 'setView', setScalarCloud: 'setScalarCloud', extractData: 'extractData', loadOverview: 'loadOverview' });

/** 构造不携带渲染器对象的物理场Command。 */
export function createFieldCommand(action, payload = {}) {
  if (!action) throw new Error('物理场操作名称不能为空');
  return { action, payload: { ...payload } };
}
