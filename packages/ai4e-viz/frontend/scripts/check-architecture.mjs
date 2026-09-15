/** 前端模块边界的轻量架构门禁，不依赖ESLint插件即可在本地和CI运行。 */

import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';

const root = resolve(import.meta.dirname, '..', 'src');
const violations = [];

// dataAssets拥有页面，visDatasets只保留解析能力；防止以后又把两个限界上下文揉回去。
const dataAssets = join(root, 'modules', 'dataAssets');
const visDatasets = join(root, 'modules', 'visDatasets');
if (!statSync(join(dataAssets, 'pages')).isDirectory()) violations.push('dataAssets 必须拥有数据资产页面');
try {
  if (statSync(join(visDatasets, 'pages')).isDirectory()) violations.push('visDatasets 不得重新拥有数据资产页面');
} catch {
  // 无pages目录是当前边界要求。
}

/** 递归列出目录中的文件。 */
function files(directory) {
  return readdirSync(directory).flatMap((name) => {
    const path = join(directory, name);
    return statSync(path).isDirectory() ? files(path) : [path];
  });
}

const secondLevel = join(root, 'modules', 'visPhysField', 'modules');
const forbiddenSecondLevelNames = new Set(['api.js', 'module.js', 'index.js', 'store.js']);
for (const path of files(secondLevel)) {
  const name = path.split('/').at(-1);
  if (forbiddenSecondLevelNames.has(name)) violations.push(`${relative(root, path)} 不得出现在物理场二级模块`);
}

const engineFrontend = join(root, 'modules', 'visEngine');
try {
  if (statSync(engineFrontend).isDirectory()) violations.push('visEngine 当前不应建立前端模块');
} catch {
  // 目录不存在正是当前架构要求。
}

for (const path of files(join(root, 'modules'))) {
  if (!/\.(js|jsx)$/.test(path)) continue;
  const source = readFileSync(path, 'utf8').trimStart();
  if (!source.startsWith('/**')) violations.push(`${relative(root, path)} 缺少中文文件头`);
}

if (violations.length) {
  console.error(violations.join('\n'));
  process.exit(1);
}
console.log('前端架构检查通过');
