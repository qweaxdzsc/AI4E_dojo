/** 数据概览二级Hook；共享一级API和状态。 */

import { useCallback } from 'react';
import { usePhysFieldContext } from '../../../components/PhysFieldProvider.jsx';
import { PHYS_FIELD_ACTION } from '../../../model.js';

/** 返回加载概览数据的Command入口。 */
export default function useDataOverview() {
  const { dispatch } = usePhysFieldContext();
  return useCallback((request) => dispatch(PHYS_FIELD_ACTION.loadOverview, request), [dispatch]);
}
