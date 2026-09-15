/** 前端一级业务模块注册表；应用壳只消费公开元数据。 */

import { dataAssetsModule } from '../modules/dataAssets/index.js';
import { reportDesignerModule } from '../modules/reportDesigner/index.js';
import { reportManageModule } from '../modules/reportManage/index.js';
import { visDatasetsModule } from '../modules/visDatasets/index.js';
import { visTaskManageModule } from '../modules/visTaskManage/index.js';

export const FRONTEND_MODULES = Object.freeze([dataAssetsModule, visDatasetsModule, visTaskManageModule, reportManageModule, reportDesignerModule]);

/** 返回拥有主导航入口的模块元数据。 */
export function navigationModules() {
  return FRONTEND_MODULES.filter((module) => module.navigation);
}
