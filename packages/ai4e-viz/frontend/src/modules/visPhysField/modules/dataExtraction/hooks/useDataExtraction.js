/** 数据提取二级Hook；共享一级API、Provider和状态。 */

import { useCallback } from 'react';
import { usePhysFieldContext } from '../../../components/PhysFieldProvider.jsx';
import { PHYS_FIELD_ACTION } from '../../../model.js';

/** 返回统一点线面体提取命令。 */
export default function useDataExtraction() {
  const { dispatch } = usePhysFieldContext();
  return useCallback((request) => dispatch(PHYS_FIELD_ACTION.extractData, request), [dispatch]);
}
