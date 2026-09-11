import {readdirSync,readFileSync} from 'node:fs';import {resolve,relative} from 'node:path';
const root=resolve(import.meta.dirname,'../src');let failures=[];
function walk(dir){for(const e of readdirSync(dir,{withFileTypes:true})){const p=resolve(dir,e.name);if(e.isDirectory())walk(p);else if(/\.tsx?$/.test(p)){const source=relative(root,p).split('/');for(const m of readFileSync(p,'utf8').matchAll(/from\s+['"]([^'"]+)['"]/g)){if(!m[1].startsWith('.'))continue;const dest=relative(root,resolve(dir,m[1])).split('/');if(source[0]==='modules'&&dest[0]==='modules'&&source[1]!==dest[1]&&dest.length>2)failures.push(p+': '+m[1]);}}}}
walk(root);if(failures.length){console.error(failures.join('\n'));process.exit(1)}console.log('微领域公开门面检查通过');
