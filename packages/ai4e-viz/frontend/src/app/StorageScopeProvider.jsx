/** 应用级明确任务上下文，独立标签页保存目标互不覆盖。 */
import {createContext, useContext, useMemo} from 'react';
import {useLocation} from 'react-router-dom';
import {currentStorageContext} from '../modules/visIO/index.js';
const StorageScope = createContext('');

/** 导航保留当前已选上下文，页面不持有机器目录。 */
export function StorageScopeProvider({children}) {
  const location=useLocation();
  const identity=useMemo(()=>currentStorageContext(),[location.search]);
  return <StorageScope.Provider value={identity}>{children}</StorageScope.Provider>;
}

/** 共享任务上下文只暴露不透明标识。 */
export function useStorageScope() { return useContext(StorageScope); }
