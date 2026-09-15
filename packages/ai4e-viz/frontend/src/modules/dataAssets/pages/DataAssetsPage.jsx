/** 数据资产一级模块的列表路由页。 */

import DataAssets from './DataAssets.jsx';

/** 渲染数据资产列表，并把导航事件交给应用壳。 */
export default function DataAssetsPage(props) {
  return <DataAssets {...props} />;
}
