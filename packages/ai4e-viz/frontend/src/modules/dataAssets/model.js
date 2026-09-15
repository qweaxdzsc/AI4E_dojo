/** 数据资产模块的前端实体和值对象转换。 */

/** 把后端Artifact DTO转换为页面使用的数据资产对象。 */
export function toDataAsset(dto) {
  return { ...dto, artifactId: dto.artifact_id ?? dto.artifactId };
}
