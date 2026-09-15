/** 三维物理场一级Provider；统一承载共享状态和未来Trame会话。 */

import { createContext, useContext } from 'react';
import usePhysField from '../hooks/usePhysField.js';

const PhysFieldContext = createContext(null);

/** 为展示、提取和概览二级业务提供同一状态基座。 */
export function PhysFieldProvider({ children, initialState }) {
  const value = usePhysField(initialState);
  return <PhysFieldContext.Provider value={value}>{children}</PhysFieldContext.Provider>;
}

/** 读取一级物理场上下文；禁止二级模块自行创建Store。 */
export function usePhysFieldContext() {
  const value = useContext(PhysFieldContext);
  if (!value) throw new Error('物理场组件必须位于PhysFieldProvider内');
  return value;
}
