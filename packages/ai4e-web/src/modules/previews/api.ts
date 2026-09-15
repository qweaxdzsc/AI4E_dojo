import { query, request } from "../../infrastructure/http/client";
export const preview = (
  p: string,
  root?: string,
  path?: string,
  t?: string,
  operation = "inspect",
  field?: string,
  offset = 0,
  ref?: {asset_id?:string;revision?:string},
) =>
  request(
    "/projects/" +
      p +
      "/preview" +
      query({ root, path, task_id: t, operation, field, offset, asset_id: ref?.asset_id, revision: ref?.revision }),
  );

/** 将受控文件固定为查看器资产。 */
export const registerPreviewAsset = (project:string,root:string,path:string,task_id?:string) => request(`/projects/${project}/assets`,{root,path,task_id});
