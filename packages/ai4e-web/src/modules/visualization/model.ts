import type {AssetRef,BinaryBuffer,DisplayAssetManifest,SceneDocument} from '../../infrastructure/contracts/platform.generated';
/** 本地域只补充显示名称，公共身份与显示协议来自生成契约。 */
export type Source=AssetRef & {name?:string};
export type BufferInfo=BinaryBuffer;
export type Display=DisplayAssetManifest & {asset_id?:string};
export type Scene=SceneDocument;
/** 单输入管线是有向树；只发送选中节点的祖先链，拒绝循环和断链。 */
export function pipelineChain(nodes:any[],target:string|null):any[]{
 if(!target)return [];
 const byId=new Map(nodes.map(n=>[n.id,n])),seen=new Set<string>(),chain:any[]=[];let id:string|null=target;
 while(id){if(seen.has(id))throw new Error('过滤器管线存在循环');seen.add(id);const node=byId.get(id);if(!node)throw new Error('过滤器输入节点不存在');chain.unshift(node);id=node.input||null;}
 return chain;
}
/** 删除仅影响后代分支，不删除文件或同源其他分支。 */
export function removePipelineBranch(nodes:any[],id:string){const removed=new Set([id]);let changed=true;while(changed){changed=false;for(const n of nodes)if(n.input&&removed.has(n.input)&&!removed.has(n.id)){removed.add(n.id);changed=true;}}return nodes.filter(n=>!removed.has(n.id));}
/** 坐标上下文中的同源是固定文件及成员/块，不是仅同一个登记文件名。 */
export function sameCoordinateSource(a:Source|undefined,b:Source|undefined):boolean{
 if(!a||!b||!a.project_id||!a.asset_id||!a.revision||!b.project_id||!b.asset_id||!b.revision)return false;
 return a.project_id===b.project_id&&a.asset_id===b.asset_id&&a.revision===b.revision&&(a.member??null)===(b.member??null)&&(a.block??null)===(b.block??null);
}
/** 读取显示清单里绑定本次来源的坐标声明；缺声明返回空，不猜单位。 */
function declaredCoordinateSpace(source:Source|undefined,display:Display|undefined){
 const space=display?.coordinate_space;
 if(!source||!space||space.evidence!=='source-declaration'||!space.id?.trim()||!space.unit?.trim()||!space.source_refs?.some(ref=>sameCoordinateSource(source,ref)))return null;
 return space;
}
/** 相机联动对当前全部窗口生效，不要求共同坐标空间。 */
export function cameraSourcesCompatible(_a?:Source,_b?:Source,_displayA?:Display,_displayB?:Display):boolean{
 return true;
}
/** 已声明单位不一致时提示，不阻止联动。 */
export function cameraLinkUnitNotice(a:Source|undefined,b:Source|undefined,displayA?:Display,displayB?:Display):string{
 const left=declaredCoordinateSpace(a,displayA),right=declaredCoordinateSpace(b,displayB);
 if(left&&right&&left.unit!==right.unit)return `相机已联动；来源单位不一致：${left.unit}、${right.unit}`;
 return '';
}
