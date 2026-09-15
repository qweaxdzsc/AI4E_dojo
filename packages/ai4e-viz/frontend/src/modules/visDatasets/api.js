/** 数据集查看模块的解析、画像和体检API。 */

import { requestJson } from '../../infrastructure/http/client.js';

/** 重新分析一个已登记资产的数据内容。 */
export const apiAnalyzeArtifact = (artifactId) => requestJson(`/api/artifacts/${encodeURIComponent(artifactId)}/analyze`, { method: 'POST' });

/** 读取一个已登记资产的解析画像。 */
export const apiParseDataset = (artifactId) => requestJson(`/api/artifact/${encodeURIComponent(artifactId)}/parse`);
