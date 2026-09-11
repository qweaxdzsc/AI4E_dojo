import { query, request } from "../../infrastructure/http/client";
const url = (p: string) => "/projects/" + p + "/files";
export const roots = (p: string, t?: string) =>
  request(url(p) + "/roots" + query({ task_id: t }));
export const list = (p: string, root: string, path: string, t?: string) =>
  request(url(p) + query({ root, path, task_id: t }));
export const download = (p: string, root: string, path: string, t?: string) =>
  "/api/v1" + url(p) + "/download" + query({ root, path, task_id: t });
