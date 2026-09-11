import { request } from "../../infrastructure/http/client";
export const list = () => request("/projects");
export const save = (v: unknown, id?: string) =>
  request("/projects" + (id ? "/" + id : ""), v, id ? "PATCH" : "POST");
/** 项目卡片统计消费服务实际任务记录，不填入原型样例计数。 */
export const projectTasks = (p:string) => request(`/projects/${p}/tasks`);
