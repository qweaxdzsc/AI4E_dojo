/** 物理场展示二级Hook；通过一级Provider提交视图Command。 */

import { useCallback } from 'react';
import { usePhysFieldContext } from '../../../components/PhysFieldProvider.jsx';
import { PHYS_FIELD_ACTION } from '../../../model.js';

/** 返回视图变换命令，不创建独立Store或Trame连接。 */
export default function useFieldView() {
  const { dispatch } = usePhysFieldContext();
  return useCallback((view) => dispatch(PHYS_FIELD_ACTION.setView, view), [dispatch]);
}
